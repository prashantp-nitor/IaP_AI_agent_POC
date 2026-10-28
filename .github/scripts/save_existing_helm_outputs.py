#!/usr/bin/env python3
"""save_existing_helm_outputs.py — Persist existing Helm deployment outcomes (Task T3 & T7).

Reads runner results and dispatch metadata, saving execution outputs directly to the database.
Preserves historical public URL on failure rather than marking a failed run as a success.
Guarantees concurrency safety by checking active CD dispatch_id under lock and skipping stale runs.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable


def save_outputs(
    dispatch_data: dict[str, Any],
    result_data: dict[str, Any],
    commit_sha: str = "",
    run_id: str = "",
    workflow_status: str = "",
    db_saver: Callable[[dict[str, Any]], None] | None = None,
    existing_record: dict[str, Any] | None = None,
    db_url: str | None = None,
    client: Any = None,
) -> dict[str, Any] | None:
    """Structure and persist execution outputs for an existing Helm deployment run."""
    job_id = str(dispatch_data.get("job_id") or result_data.get("job_id") or "")
    dispatch_id = str(dispatch_data.get("dispatch_id") or result_data.get("dispatch_id") or "")

    # Superseded dispatch check via existing_record or client
    active_cd = None
    if existing_record:
        deploy_out = existing_record.get("deploy_output") or existing_record.get("existing_helm") or {}
        if isinstance(deploy_out, dict):
            active_cd = deploy_out.get("existing_helm", {}).get("cd") if "existing_helm" in deploy_out else deploy_out.get("cd")

    if not active_cd and client is not None:
        try:
            resp = client.table("deployment_jobs").select("deploy_output").eq("job_id", job_id).execute()
            if resp and resp.data:
                deploy_out = resp.data[0].get("deploy_output") or {}
                active_cd = (deploy_out.get("existing_helm") or {}).get("cd")
        except Exception as e:
            print(f"Warning querying deployment_jobs via client: {e}")

    if active_cd and isinstance(active_cd, dict):
        active_disp = active_cd.get("dispatch_id")
        if active_disp and str(active_disp) != str(dispatch_id):
            print(f"Stale dispatch {dispatch_id} superseded by {active_disp} for job {job_id}; skipping save.")
            return {"status": "skipped_stale", "job_id": job_id, "dispatch_id": dispatch_id}
        if active_cd.get("discovery_revision") and dispatch_data.get("discovery_revision"):
            if str(active_cd["discovery_revision"]) != str(dispatch_data["discovery_revision"]):
                print(f"Discovery revision mismatch for job {job_id}; skipping save.")
                return {"status": "skipped_stale", "job_id": job_id, "dispatch_id": dispatch_id}
        if active_cd.get("config_digest") and dispatch_data.get("config_digest"):
            if str(active_cd["config_digest"]) != str(dispatch_data["config_digest"]):
                print(f"Config digest mismatch for job {job_id}; skipping save.")
                return {"status": "skipped_stale", "job_id": job_id, "dispatch_id": dispatch_id}

    status = result_data.get("status")
    if not status:
        status = "failed" if str(workflow_status).lower() in ("failure", "cancelled") else "succeeded"

    infra_details = {
        "provider": dispatch_data.get("provider", "azure"),
        "cluster_name": dispatch_data.get("cluster_name"),
        "resource_group": dispatch_data.get("resource_group"),
        "namespace": dispatch_data.get("namespace"),
        "acr_registry": dispatch_data.get("acr_registry"),
        "target_key": dispatch_data.get("target_key"),
    }

    infra_outputs = {
        "frontend_endpoint": result_data.get("frontend_endpoint"),
    }

    deployment_details = {
        "mode": "existing",
        "dispatch_id": dispatch_id,
        "discovery_revision": dispatch_data.get("discovery_revision") or result_data.get("discovery_revision"),
        "config_digest": dispatch_data.get("config_digest") or result_data.get("config_digest"),
        "commit_sha": commit_sha,
        "run_id": run_id,
        "workflow_status": workflow_status,
        "releases": result_data.get("releases", {}),
        "completed_releases": result_data.get("completed_releases", []),
        "failed_release": result_data.get("failed_release"),
        "failed_step": result_data.get("failed_step"),
        "error_message": result_data.get("error_message") or result_data.get("error_summary"),
        "error_summary": result_data.get("error_summary") or result_data.get("error_message"),
        "diagnostics": result_data.get("diagnostics"),
        "stage_statuses": result_data.get("stage_statuses"),
        "pod_statuses": result_data.get("pod_statuses"),
        "events": result_data.get("events"),
        "logs": result_data.get("logs"),
    }

    deployment_outputs: dict[str, Any] = {
        "status": status,
        "helm_mode": "existing",
        "job_id": job_id,
        "dispatch_id": dispatch_id,
    }

    if status == "succeeded" and result_data.get("public_url"):
        deployment_outputs["public_url"] = result_data.get("public_url")
    else:
        status = "failed"
        deployment_outputs["status"] = "failed"
        deployment_outputs["public_url"] = None
        # Preserve previous public URL as historical data on failure
        prev_url = None
        if existing_record and isinstance(existing_record.get("deployment_outputs"), dict):
            prev_url = (
                existing_record["deployment_outputs"].get("public_url")
                or existing_record["deployment_outputs"].get("historical_public_url")
                or existing_record["deployment_outputs"].get("previous_public_url")
            )
        if prev_url:
            deployment_outputs["historical_public_url"] = prev_url
            deployment_outputs["previous_public_url"] = prev_url
            deployment_details["historical_public_url"] = prev_url

    payload = {
        "job_id": job_id,
        "infra_details": infra_details,
        "infra_outputs": infra_outputs,
        "deployment_details": deployment_details,
        "deployment_outputs": deployment_outputs,
    }

    if db_saver is not None:
        db_saver(payload)
        return payload

    effective_db_url = db_url or os.environ.get("DATABASE_URL")
    if not effective_db_url:
        if client is not None:
            # Supabase client persistence fallback
            try:
                # Read historical public_url if failed and not yet set
                if status != "succeeded" and "historical_public_url" not in deployment_outputs:
                    resp_prev = client.table("deployment_execution_outputs").select("deployment_outputs").eq("job_id", job_id).execute()
                    if resp_prev and resp_prev.data:
                        prev_row = resp_prev.data[0].get("deployment_outputs") or {}
                        prev_url = prev_row.get("public_url") or prev_row.get("historical_public_url")
                        if prev_url:
                            deployment_outputs["historical_public_url"] = prev_url
                            deployment_outputs["previous_public_url"] = prev_url
                            deployment_details["historical_public_url"] = prev_url
                            payload["deployment_outputs"] = deployment_outputs
                            payload["deployment_details"] = deployment_details

                client.table("deployment_execution_outputs").upsert(payload, on_conflict="job_id").execute()
                req_status = "completed" if status == "succeeded" else "failed"
                client.table("requests").update({"status": req_status}).eq("request_id", job_id).execute()
                print(f"Successfully saved execution outputs via client for job {job_id}")
            except Exception as client_err:
                print(f"Client persistence error: {client_err}")
            return payload

        print("DATABASE_URL not configured. Skipping live database update.")
        return payload

    try:
        import psycopg2

        conn = psycopg2.connect(effective_db_url)
        cur = conn.cursor()

        # Check deployment_jobs row under FOR UPDATE lock
        cur.execute(
            "SELECT deploy_output FROM deployment_jobs WHERE job_id = %s FOR UPDATE;",
            (job_id,),
        )
        job_row = cur.fetchone()
        if job_row and job_row[0]:
            deploy_out = job_row[0] if isinstance(job_row[0], dict) else json.loads(job_row[0])
            active_cd = (deploy_out.get("existing_helm") or {}).get("cd") or {}
            active_disp = active_cd.get("dispatch_id")
            if active_disp and str(active_disp) != str(dispatch_id):
                print(f"Stale dispatch {dispatch_id} superseded by {active_disp} for job {job_id}; skipping save.")
                cur.close()
                conn.close()
                return {"status": "skipped_stale", "job_id": job_id, "dispatch_id": dispatch_id}
            if active_cd.get("discovery_revision") and dispatch_data.get("discovery_revision"):
                if str(active_cd["discovery_revision"]) != str(dispatch_data["discovery_revision"]):
                    print(f"Discovery revision mismatch for job {job_id}; skipping save.")
                    cur.close()
                    conn.close()
                    return {"status": "skipped_stale", "job_id": job_id, "dispatch_id": dispatch_id}
            if active_cd.get("config_digest") and dispatch_data.get("config_digest"):
                if str(active_cd["config_digest"]) != str(dispatch_data["config_digest"]):
                    print(f"Config digest mismatch for job {job_id}; skipping save.")
                    cur.close()
                    conn.close()
                    return {"status": "skipped_stale", "job_id": job_id, "dispatch_id": dispatch_id}

        # Check existing row if status is failed and previous url not yet populated
        if status != "succeeded" and "historical_public_url" not in deployment_outputs:
            try:
                cur.execute(
                    "SELECT deployment_outputs FROM deployment_execution_outputs WHERE job_id = %s;",
                    (job_id,),
                )
                row = cur.fetchone()
                if row and row[0]:
                    existing_out = row[0] if isinstance(row[0], dict) else json.loads(row[0])
                    prev = (
                        existing_out.get("public_url")
                        or existing_out.get("historical_public_url")
                        or existing_out.get("previous_public_url")
                    )
                    if prev:
                        deployment_outputs["historical_public_url"] = prev
                        deployment_outputs["previous_public_url"] = prev
                        deployment_details["historical_public_url"] = prev
                        payload["deployment_outputs"] = deployment_outputs
                        payload["deployment_details"] = deployment_details
            except Exception as read_err:
                print(f"Warning reading existing record: {read_err}")

        sql = """
        INSERT INTO deployment_execution_outputs (
            job_id, infra_details, infra_outputs, deployment_details, deployment_outputs, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (job_id) DO UPDATE SET
            infra_details = COALESCE(EXCLUDED.infra_details, deployment_execution_outputs.infra_details),
            infra_outputs = COALESCE(EXCLUDED.infra_outputs, deployment_execution_outputs.infra_outputs),
            deployment_details = EXCLUDED.deployment_details,
            deployment_outputs = EXCLUDED.deployment_outputs,
            updated_at = NOW();
        """
        cur.execute(
            sql,
            (
                job_id,
                json.dumps(infra_details),
                json.dumps(infra_outputs),
                json.dumps(deployment_details),
                json.dumps(deployment_outputs),
            ),
        )
        conn.commit()

        # Update requests status
        try:
            req_status = "completed" if status == "succeeded" else "failed"
            cur.execute(
                """
                UPDATE requests
                SET status = %s, updated_at = NOW()
                WHERE request_id = %s OR id = %s;
                """,
                (req_status, job_id, job_id),
            )
            conn.commit()
        except Exception as req_err:
            print(f"Warning updating requests table: {req_err}")

        cur.close()
        conn.close()
        print(f"Successfully saved existing Helm execution outputs for job {job_id}")

    except Exception as exc:
        print(f"Direct DB save error: {exc}")

    return payload


def persist_existing_helm_outputs(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    """Convenience alias for save_outputs."""
    return save_outputs(*args, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Save existing Helm deployment execution outputs")
    parser.add_argument("--dispatch-file", default=".deploy/helm-release.json", help="Path to dispatch metadata JSON")
    parser.add_argument("--result-file", default="/tmp/existing-helm-deploy-result.json", help="Path to runner result JSON")
    parser.add_argument("--commit-sha", default="", help="Commit SHA")
    parser.add_argument("--run-id", default="", help="GitHub Action Run ID")
    parser.add_argument("--workflow-status", default="", help="GitHub Action Job Status")
    parser.add_argument("--db-url", default=None, help="Postgres database URL override")
    args = parser.parse_args()

    dispatch_path = Path(args.dispatch_file)
    dispatch_data: dict[str, Any] = {}
    if dispatch_path.exists():
        try:
            dispatch_data = json.loads(dispatch_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Warning reading dispatch file: {exc}")

    result_path = Path(args.result_file)
    result_data: dict[str, Any] = {}
    if result_path.exists():
        try:
            result_data = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Warning reading result file: {exc}")
    else:
        result_data = {
            "status": "failed",
            "error_message": f"Deploy result file missing: {result_path}",
        }

    save_outputs(
        dispatch_data=dispatch_data,
        result_data=result_data,
        commit_sha=args.commit_sha or os.environ.get("GITHUB_SHA", ""),
        run_id=args.run_id or os.environ.get("GITHUB_RUN_ID", ""),
        workflow_status=args.workflow_status or os.environ.get("JOB_STATUS", ""),
        db_url=args.db_url,
    )


if __name__ == "__main__":
    main()

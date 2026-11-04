"""
Deployment Execution Outputs Saver
Reads environment variables provided by GitHub Actions runner and records
execution state into the primary database via psycopg2.
"""
import os
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit

def build_success_snapshot(deployment_outputs, deployment_details, infra_details, recorded_at):
    outputs = deployment_outputs or {}
    if str(outputs.get("status") or "").strip().lower() != "success":
        return None
    value = outputs.get("public_url")
    if not isinstance(value, str):
        return None
    public_url = value.strip()
    if not public_url or any(char.isspace() for char in public_url):
        return None
    if "pending" in public_url.lower() or "<" in public_url or ">" in public_url:
        return None
    try:
        parsed = urlsplit(public_url)
        if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        if parsed.port is not None and not 1 <= parsed.port <= 65535:
            return None
    except ValueError:
        return None
    details = deployment_details or {}
    infrastructure = infra_details or {}
    return {
        "public_url": value,
        "status": "success",
        "run_id": details.get("github_run_id") or details.get("run_id"),
        "commit_sha": details.get("commit_sha"),
        "project_name": details.get("project_name"),
        "provider": infrastructure.get("provider"),
        "environment": details.get("environment") or infrastructure.get("environment"),
        "recorded_at": recorded_at,
    }

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Required execution output write failed: database configuration is unavailable.")
        raise SystemExit(1)

    job_id = os.environ.get("JOB_ID")
    provider = os.environ.get("PROVIDER") or "azure"
    region = os.environ.get("REGION") or ""
    namespace = os.environ.get("NAMESPACE") or "default"
    project_name = os.environ.get("PROJECT_NAME") or "default"
    deployment_strategy = os.environ.get("DEPLOYMENT_STRATEGY") or "canary"
    commit_sha = os.environ.get("COMMIT_SHA") or ""
    run_id = os.environ.get("RUN_ID") or ""
    job_status = os.environ.get("JOB_STATUS") or ""
    public_url = os.environ.get("PUBLIC_URL") or ""

    infra_details = {
        "provider": provider,
        "region": region,
        "namespace": namespace,
    }

    infra_raw = os.environ.get("INFRA_OUTPUTS_JSON")
    try:
        infra_outputs = json.loads(infra_raw) if infra_raw else {"endpoints": []}
    except Exception:
        infra_outputs = {"endpoints": []}

    db_config_raw = os.environ.get("DB_CONFIG_JSON")
    try:
        db_config = json.loads(db_config_raw) if db_config_raw else {}
    except Exception:
        db_config = {}

    deployment_details = {
        "project_name": project_name,
        "deployment_strategy": deployment_strategy,
        "environment": os.environ.get("ENVIRONMENT") or "",
        "commit_sha": commit_sha,
        "github_run_id": run_id,
    }
    deployment_outputs = {
        "public_url": public_url,
        "status": job_status,
        "db_config": db_config,
    }
    recorded_at = datetime.now(timezone.utc).isoformat()
    success_snapshot = build_success_snapshot(
        deployment_outputs, deployment_details, infra_details, recorded_at
    )

    try:
        import psycopg2

        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        sql = """
        INSERT INTO deployment_execution_outputs (
            job_id, infra_details, infra_outputs, deployment_details, deployment_outputs,
            last_successful_outputs, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (job_id) DO UPDATE SET
            infra_details = EXCLUDED.infra_details,
            infra_outputs = EXCLUDED.infra_outputs,
            deployment_details = EXCLUDED.deployment_details,
            deployment_outputs = EXCLUDED.deployment_outputs,
            last_successful_outputs = CASE
                WHEN EXCLUDED.last_successful_outputs IS NOT NULL
                THEN EXCLUDED.last_successful_outputs
                ELSE deployment_execution_outputs.last_successful_outputs
            END,
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
                json.dumps(success_snapshot) if success_snapshot is not None else None,
            ),
        )
        conn.commit()

        if success_snapshot is not None:
            try:
                update_req_sql = """
                UPDATE requests
                SET status = %s,
                    updated_at = NOW()
                WHERE request_id = %s OR id = %s;
                """
                cur.execute(update_req_sql, ("completed", job_id, job_id))
                conn.commit()
            except Exception:
                print("Warning: request status update failed after saving execution outputs.")

        cur.close()
        conn.close()
        print("Successfully saved deployment execution outputs directly to database.")
    except Exception:
        print("Required execution output write failed; deployment completion was not recorded.")
        raise SystemExit(1)

if __name__ == "__main__":
    main()

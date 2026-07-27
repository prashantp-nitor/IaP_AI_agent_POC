"""
Deployment Execution Outputs Saver
Reads environment variables provided by GitHub Actions runner and records
execution state into the primary database via psycopg2.
"""
import os
import json

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL secret is not set. Skipping direct DB update.")
        return

    job_id = os.environ.get("JOB_ID")
    provider = os.environ.get("PROVIDER") or "azure"
    region = os.environ.get("REGION") or ""
    namespace = os.environ.get("NAMESPACE") or "default"
    project_name = os.environ.get("PROJECT_NAME") or "default"
    deployment_strategy = os.environ.get("DEPLOYMENT_STRATEGY") or "canary"
    commit_sha = os.environ.get("COMMIT_SHA") or ""
    run_id = os.environ.get("RUN_ID") or ""
    job_status = os.environ.get("JOB_STATUS") or "completed"
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
        "commit_sha": commit_sha,
        "github_run_id": run_id,
    }
    deployment_outputs = {
        "public_url": public_url,
        "status": job_status,
        "db_config": db_config,
    }

    try:
        import psycopg2

        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        sql = """
        INSERT INTO deployment_execution_outputs (
            job_id, infra_details, infra_outputs, deployment_details, deployment_outputs, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (job_id) DO UPDATE SET
            infra_details = EXCLUDED.infra_details,
            infra_outputs = EXCLUDED.infra_outputs,
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

        if public_url and not public_url.startswith("http://<pending"):
            try:
                update_req_sql = """
                UPDATE requests
                SET status = %s,
                    updated_at = NOW()
                WHERE request_id = %s OR id = %s;
                """
                cur.execute(update_req_sql, ("completed", job_id, job_id))
                conn.commit()
            except Exception as req_e:
                print(f"Warning updating requests table: {req_e}")

        cur.close()
        conn.close()
        print(f"Successfully saved deployment execution outputs directly to database for job_id: {job_id}")
    except Exception as exc:
        print(f"Direct DB update error: {exc}")

if __name__ == "__main__":
    main()

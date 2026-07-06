#!/usr/bin/env python3
"""Database replication utility script executed in the GHA runner.

This script:
1. Reads db_replication_metadata.json from the current working directory.
2. Fetches the runner's public IP address.
3. For each database, temporarily creates Azure firewall rules allowing the runner's IP.
4. Executes the appropriate database export/import (sqlpackage, pg_dump/pg_restore, mysqldump/mysql).
5. Cleans up all firewall rules in a finally block to ensure security.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
import requests


def get_runner_ip() -> str:
    """Fetch the runner's public IP address via ipify."""
    print("Fetching runner public IP address...")
    response = requests.get("https://api.ipify.org", timeout=10)
    response.raise_for_status()
    ip = response.text.strip()
    print(f"Runner public IP: {ip}")
    return ip


def run_command(
    cmd: list[str],
    env: dict[str, str] | None = None,
    stdin_file=None,
    stdout_file=None,
) -> subprocess.CompletedProcess:
    """Run a subprocess command, redacting credentials from the logs."""
    safe_cmd = []
    for arg in cmd:
        if arg.startswith("/sp:"):
            safe_cmd.append("/sp:***")
        elif arg.startswith("/tp:"):
            safe_cmd.append("/tp:***")
        elif arg.startswith("-p") and len(arg) > 2:
            safe_cmd.append("-p***")
        else:
            safe_cmd.append(arg)

    print(f"Executing: {' '.join(safe_cmd)}")

    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    try:
        result = subprocess.run(
            cmd,
            env=run_env,
            stdin=stdin_file,
            stdout=stdout_file if stdout_file else subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        raise


def create_firewall_rule(
    db_type: str,
    rg: str,
    server: str,
    rule_name: str,
    ip: str,
) -> list[str]:
    """Generate and execute Azure CLI command to create a firewall rule."""
    if db_type == "sql_server":
        cmd = [
            "az", "sql", "server", "firewall-rule", "create",
            "--resource-group", rg,
            "--server", server,
            "--name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip,
        ]
    elif db_type == "postgresql":
        cmd = [
            "az", "postgres", "flexible-server", "firewall-rule", "create",
            "--resource-group", rg,
            "--server-name", server,
            "--name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip,
        ]
    elif db_type == "mysql":
        cmd = [
            "az", "mysql", "flexible-server", "firewall-rule", "create",
            "--resource-group", rg,
            "--server-name", server,
            "--name", rule_name,
            "--start-ip-address", ip,
            "--end-ip-address", ip,
        ]
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    run_command(cmd)
    return cmd


def delete_firewall_rule(
    db_type: str,
    rg: str,
    server: str,
    rule_name: str,
) -> list[str]:
    """Generate and execute Azure CLI command to delete a firewall rule."""
    if db_type == "sql_server":
        cmd = [
            "az", "sql", "server", "firewall-rule", "delete",
            "--resource-group", rg,
            "--server", server,
            "--name", rule_name,
            "--yes",
        ]
    elif db_type == "postgresql":
        cmd = [
            "az", "postgres", "flexible-server", "firewall-rule", "delete",
            "--resource-group", rg,
            "--server-name", server,
            "--name", rule_name,
            "--yes",
        ]
    elif db_type == "mysql":
        cmd = [
            "az", "mysql", "flexible-server", "firewall-rule", "delete",
            "--resource-group", rg,
            "--server-name", server,
            "--name", rule_name,
            "--yes",
        ]
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    run_command(cmd)
    return cmd


def replicate_sql_server(db: dict[str, str]) -> None:
    """Run export and import commands for SQL Server."""
    db_name = db["db_name"]
    source_server = db["source_server_name"]
    target_server = db["target_server_name"]
    source_user = db["source_admin_login"]
    source_pass = db["source_admin_password"]
    target_user = db["target_admin_login"]
    target_pass = db["target_admin_password"]
    bacpac_file = f"{db_name}.bacpac"

    export_cmd = [
        "sqlpackage",
        "/Action:Export",
        f"/ssn:{source_server}.database.windows.net",
        f"/sdn:{db_name}",
        f"/su:{source_user}",
        f"/sp:{source_pass}",
        f"/tf:{bacpac_file}",
    ]
    import_cmd = [
        "sqlpackage",
        "/Action:Import",
        f"/tsn:{target_server}.database.windows.net",
        f"/tdn:{db_name}",
        f"/tu:{target_user}",
        f"/tp:{target_pass}",
        f"/sf:{bacpac_file}",
    ]

    run_command(export_cmd)
    run_command(import_cmd)


def replicate_postgresql(db: dict[str, str]) -> None:
    """Run export and import commands for PostgreSQL flexible server."""
    db_name = db["db_name"]
    source_server = db["source_server_name"]
    target_server = db["target_server_name"]
    source_user = db["source_admin_login"]
    source_pass = db["source_admin_password"]
    target_user = db["target_admin_login"]
    target_pass = db["target_admin_password"]
    dump_file = f"{db_name}.dump"

    # Export
    export_cmd = [
        "pg_dump",
        "-h", f"{source_server}.postgres.database.azure.com",
        "-U", source_user,
        "-d", db_name,
        "-F", "c",
        "-b",
        "-f", dump_file,
    ]
    run_command(export_cmd, env={"PGPASSWORD": source_pass})

    # Check if target database exists, and create if it doesn't
    check_cmd = [
        "psql",
        "-h", f"{target_server}.postgres.database.azure.com",
        "-U", target_user,
        "-d", "postgres",
        "-tAc", f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
    ]
    check_res = run_command(check_cmd, env={"PGPASSWORD": target_pass})
    if "1" not in check_res.stdout:
        create_cmd = [
            "psql",
            "-h", f"{target_server}.postgres.database.azure.com",
            "-U", target_user,
            "-d", "postgres",
            "-c", f"CREATE DATABASE \"{db_name}\";",
        ]
        run_command(create_cmd, env={"PGPASSWORD": target_pass})

    # Import
    import_cmd = [
        "pg_restore",
        "-h", f"{target_server}.postgres.database.azure.com",
        "-U", target_user,
        "-d", db_name,
        dump_file,
    ]
    run_command(import_cmd, env={"PGPASSWORD": target_pass})


def replicate_mysql(db: dict[str, str]) -> None:
    """Run export and import commands for MySQL flexible server."""
    db_name = db["db_name"]
    source_server = db["source_server_name"]
    target_server = db["target_server_name"]
    source_user = db["source_admin_login"]
    source_pass = db["source_admin_password"]
    target_user = db["target_admin_login"]
    target_pass = db["target_admin_password"]
    sql_file = f"{db_name}.sql"

    # Export
    export_cmd = [
        "mysqldump",
        "-h", f"{source_server}.mysql.database.azure.com",
        "-u", source_user,
        f"-p{source_pass}",
        "--databases", db_name,
    ]
    with open(sql_file, "w", encoding="utf-8") as out_f:
        run_command(export_cmd, stdout_file=out_f)

    # Create target DB if not exists
    create_cmd = [
        "mysql",
        "-h", f"{target_server}.mysql.database.azure.com",
        "-u", target_user,
        f"-p{target_pass}",
        "-e", f"CREATE DATABASE IF NOT EXISTS `{db_name}`;",
    ]
    run_command(create_cmd)

    # Import
    import_cmd = [
        "mysql",
        "-h", f"{target_server}.mysql.database.azure.com",
        "-u", target_user,
        f"-p{target_pass}",
    ]
    with open(sql_file, "r", encoding="utf-8") as in_f:
        run_command(import_cmd, stdin_file=in_f)


def main() -> int:
    """Main execution entry point."""
    metadata_file = Path("db_replication_metadata.json")
    if not metadata_file.exists():
        print(f"Error: {metadata_file} not found in the current working directory.")
        return 1

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    source_rg = metadata.get("source_rg")
    target_rg = metadata.get("target_rg")
    databases = metadata.get("databases", [])

    if not source_rg or not target_rg:
        print("Error: 'source_rg' and 'target_rg' are required at the root level of metadata.")
        return 1

    if not databases:
        print("No databases to replicate.")
        return 0

    try:
        runner_ip = get_runner_ip()
    except Exception as e:
        print(f"Failed to fetch runner IP: {e}")
        return 1

    created_rules: list[dict[str, str]] = []
    exit_code = 0

    try:
        # Keep track of firewall rules we've already created to avoid duplication
        # Key: (db_type, rg, server_name)
        existing_rule_set: set[tuple[str, str, str]] = set()

        for db in databases:
            db_type = db["type"]
            db_name = db["db_name"]
            source_server = db["source_server_name"]
            target_server = db["target_server_name"]

            # Add source firewall rule
            source_key = (db_type, source_rg, source_server)
            if source_key not in existing_rule_set:
                rule_name = f"gha-src-{db_name}-{int(time.time())}"
                print(f"Creating source firewall rule '{rule_name}' on server '{source_server}'...")
                create_firewall_rule(db_type, source_rg, source_server, rule_name, runner_ip)
                created_rules.append({
                    "type": db_type,
                    "rg": source_rg,
                    "server": source_server,
                    "rule_name": rule_name,
                })
                existing_rule_set.add(source_key)

            # Add target firewall rule
            target_key = (db_type, target_rg, target_server)
            if target_key not in existing_rule_set:
                rule_name = f"gha-tgt-{db_name}-{int(time.time())}"
                print(f"Creating target firewall rule '{rule_name}' on server '{target_server}'...")
                create_firewall_rule(db_type, target_rg, target_server, rule_name, runner_ip)
                created_rules.append({
                    "type": db_type,
                    "rg": target_rg,
                    "server": target_server,
                    "rule_name": rule_name,
                })
                existing_rule_set.add(target_key)

            # Run replication
            print(f"Replicating database '{db_name}' ({db_type})...")
            if db_type == "sql_server":
                replicate_sql_server(db)
            elif db_type == "postgresql":
                replicate_postgresql(db)
            elif db_type == "mysql":
                replicate_mysql(db)
            else:
                print(f"Skipping unknown database type '{db_type}'")

            print(f"Successfully replicated database '{db_name}'.")

    except Exception as e:
        print(f"Error occurred during database replication: {e}")
        exit_code = 1
    finally:
        print("Cleaning up firewall rules...")
        # Clean up in reverse order
        for rule in reversed(created_rules):
            try:
                print(f"Deleting firewall rule '{rule['rule_name']}' on server '{rule['server']}'...")
                delete_firewall_rule(rule["type"], rule["rg"], rule["server"], rule["rule_name"])
            except Exception as cleanup_err:
                print(f"Warning: Failed to clean up firewall rule: {cleanup_err}")
                exit_code = 1  # If cleanup fails, we flag the error

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

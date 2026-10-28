#!/usr/bin/env python3
"""deploy_existing_helm.py — Runtime execution script for existing Helm deployments (Task T3).

Executes:
1. Dispatch and manifest parity validation.
2. Exact staging in isolated temp directory from manifest file membership.
3. Preflight StorageClass and pull secret setup.
4. Serial release deployment (database -> backend -> frontend) with strict rollout readiness checks.
5. Immediate abort on failure without uninstalling releases or deleting PVCs.
6. Bounded, privacy-preserving diagnostics collection on error.
7. Frontend endpoint polling and public URL resolution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

SAFE_ROLES_ORDER = ["database", "backend", "frontend"]


def _exec_command(bin_path: str, args: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Execute command safely via subprocess.run, supporting Python-based fake CLI scripts."""
    if bin_path.endswith(".py"):
        cmd = [sys.executable, bin_path, *args]
    else:
        cmd = [bin_path, *args]
    return subprocess.run(cmd, **kwargs)


def _check_safe_posix_path(path_str: str) -> None:
    """Validate relative POSIX path for security and traversal avoidance."""
    if not isinstance(path_str, str) or not path_str.strip():
        raise ValueError("Path must be a non-empty string")
    if "\\" in path_str:
        raise ValueError(f"Path contains backslash: {path_str}")
    if path_str.startswith("/"):
        raise ValueError(f"Path must be relative: {path_str}")
    if re.match(r"^[a-zA-Z]:", path_str):
        raise ValueError(f"Windows drive letters not permitted: {path_str}")
    parts = path_str.split("/")
    if any(p == ".." for p in parts):
        raise ValueError(f"Path traversal detected: {path_str}")


def _collect_bounded_diagnostics(kubectl_bin: str, namespace: str) -> dict[str, Any]:
    """Collect bounded, allow-listed diagnostics without exposing secrets, env vars, or logs."""
    diag: dict[str, Any] = {"resources": [], "events": []}
    try:
        proc = _exec_command(
            kubectl_bin,
            ["get", "pods,sts,deploy,svc,pvc", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout)
            for item in data.get("items", []):
                kind = item.get("kind", "Unknown")
                meta = item.get("metadata", {})
                status = item.get("status", {})
                entry: dict[str, Any] = {
                    "kind": kind,
                    "name": meta.get("name"),
                    "namespace": meta.get("namespace"),
                }
                if kind == "Pod":
                    entry["phase"] = status.get("phase")
                    container_statuses = []
                    for cs in status.get("containerStatuses", []):
                        cs_info = {
                            "name": cs.get("name"),
                            "ready": cs.get("ready"),
                            "restartCount": cs.get("restartCount"),
                        }
                        state = cs.get("state", {})
                        if "waiting" in state:
                            cs_info["waiting_reason"] = state["waiting"].get("reason")
                        if "terminated" in state:
                            cs_info["exit_code"] = state["terminated"].get("exitCode")
                            cs_info["terminated_reason"] = state["terminated"].get("reason")
                        container_statuses.append(cs_info)
                    entry["container_statuses"] = container_statuses
                elif kind == "PersistentVolumeClaim":
                    entry["phase"] = status.get("phase")
                elif kind in ("Deployment", "StatefulSet"):
                    entry["replicas"] = status.get("replicas")
                    entry["ready_replicas"] = status.get("readyReplicas")
                diag["resources"].append(entry)
    except Exception as exc:
        diag["resources_error"] = str(exc)

    try:
        evt_proc = _exec_command(
            kubectl_bin,
            ["get", "events", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if evt_proc.returncode == 0:
            evt_data = json.loads(evt_proc.stdout)
            for evt in evt_data.get("items", [])[:30]:
                diag["events"].append({
                    "reason": evt.get("reason"),
                    "message": str(evt.get("message", ""))[:256],
                    "type": evt.get("type"),
                })
    except Exception as exc:
        diag["events_error"] = str(exc)

    return diag


def parse_chart_dependencies(chart_yaml_path: Path) -> list[str]:
    """Extract declared chart dependency names from Chart.yaml without external dependencies."""
    deps: list[str] = []
    if not chart_yaml_path.exists():
        return deps
    text = chart_yaml_path.read_text(encoding="utf-8")
    in_deps = False
    for line in text.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("dependencies:"):
            in_deps = True
            continue
        if in_deps:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                # Exited dependencies block
                break
            if trimmed.startswith("- name:") or trimmed.startswith("name:"):
                name = trimmed.split(":", 1)[1].strip().strip('"').strip("'")
                if name:
                    deps.append(name)
    return deps


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy existing Helm releases to Kubernetes")
    parser.add_argument("--dispatch-file", default=".deploy/helm-release.json", help="Path to dispatch metadata JSON")
    parser.add_argument("--workspace", default=".", help="Checked-out repository root workspace directory")
    parser.add_argument("--output-file", default="/tmp/existing-helm-deploy-result.json", help="Path to write result JSON")
    parser.add_argument("--helm-bin", default="helm", help="Helm executable or wrapper script")
    parser.add_argument("--kubectl-bin", default="kubectl", help="Kubectl executable or wrapper script")
    parser.add_argument("--az-bin", default="az", help="Azure CLI executable")
    parser.add_argument("--endpoint-attempts", type=int, default=30, help="Max polling attempts for frontend endpoint")
    parser.add_argument("--endpoint-interval-seconds", type=float, default=10.0, help="Sleep interval between endpoint checks")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    dispatch_path = (workspace / args.dispatch_file).resolve() if not Path(args.dispatch_file).is_absolute() else Path(args.dispatch_file)

    def write_result(data: dict[str, Any]) -> None:
        out_p = Path(args.output_file)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    if not dispatch_path.exists():
        sys.stderr.write(f"Dispatch file not found: {dispatch_path}\n")
        write_result({
            "status": "failed",
            "error_message": f"Dispatch file not found: {dispatch_path}",
            "failed_step": "dispatch_read",
        })
        sys.exit(1)

    try:
        dispatch = json.loads(dispatch_path.read_text(encoding="utf-8"))
    except Exception as exc:
        sys.stderr.write(f"Failed to parse dispatch file: {exc}\n")
        write_result({
            "status": "failed",
            "error_message": f"Failed to parse dispatch file: {exc}",
            "failed_step": "dispatch_read",
        })
        sys.exit(1)

    manifest_rel = dispatch.get("manifest_path")
    if not manifest_rel:
        proj = dispatch.get("project_name", "app")
        manifest_rel = f"deployment-output/{proj}/.existing-helm-release.json"

    manifest_path = (workspace / manifest_rel).resolve() if not Path(manifest_rel).is_absolute() else Path(manifest_rel)
    if not manifest_path.exists():
        sys.stderr.write(f"Release manifest file not found: {manifest_path}\n")
        write_result({
            "status": "failed",
            "error_message": f"Release manifest file not found: {manifest_path}",
            "failed_step": "manifest_read",
            "job_id": dispatch.get("job_id"),
            "dispatch_id": dispatch.get("dispatch_id"),
        })
        sys.exit(1)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        sys.stderr.write(f"Failed to parse release manifest: {exc}\n")
        write_result({
            "status": "failed",
            "error_message": f"Failed to parse release manifest: {exc}",
            "failed_step": "manifest_read",
            "job_id": dispatch.get("job_id"),
            "dispatch_id": dispatch.get("dispatch_id"),
        })
        sys.exit(1)

    # Parity check between dispatch and manifest
    for key in ["schema_version", "job_id", "discovery_revision", "config_digest"]:
        if str(dispatch.get(key, "")) != str(manifest.get(key, "")):
            err = f"Dispatch/manifest parity failure on '{key}': {dispatch.get(key)} != {manifest.get(key)}"
            sys.stderr.write(f"{err}\n")
            write_result({
                "status": "failed",
                "error_message": err,
                "failed_step": "parity_validation",
                "job_id": dispatch.get("job_id"),
                "dispatch_id": dispatch.get("dispatch_id"),
            })
            sys.exit(1)

    namespace = dispatch.get("namespace") or manifest.get("namespace", "default")
    job_id = dispatch.get("job_id")
    dispatch_id = dispatch.get("dispatch_id")
    discovery_revision = dispatch.get("discovery_revision")
    config_digest = dispatch.get("config_digest")

    # Validate release roles and ordering
    releases = manifest.get("releases", [])
    actual_roles = [r.get("role") for r in releases if isinstance(r, dict)]
    if actual_roles != SAFE_ROLES_ORDER:
        err = f"Releases must strictly match order {SAFE_ROLES_ORDER}, got {actual_roles}"
        sys.stderr.write(f"{err}\n")
        write_result({
            "status": "failed",
            "error_message": err,
            "failed_step": "release_order_validation",
            "job_id": job_id,
            "dispatch_id": dispatch_id,
        })
        sys.exit(1)

    stage_dir = tempfile.mkdtemp(prefix="existing-helm-stage-")
    try:
        # 1. Exact Staging in Runner Temp Tree
        for rel in releases:
            role = rel["role"]
            chart_rel = rel["chart_path"]
            _check_safe_posix_path(chart_rel)
            chart_stage_dir = Path(stage_dir) / role
            chart_stage_dir.mkdir(parents=True, exist_ok=True)

            files = rel.get("files", [])
            if not files:
                raise ValueError(f"Release '{role}' has no files listed in manifest")

            for f_info in files:
                f_path = f_info["path"]
                pkg_path = f_info["package_path"]
                _check_safe_posix_path(f_path)
                _check_safe_posix_path(pkg_path)

                src_file = workspace / pkg_path
                if not src_file.exists() or not src_file.is_file() or src_file.is_symlink():
                    raise FileNotFoundError(f"Manifested file missing or symlink: {pkg_path}")

                b = src_file.read_bytes()
                if len(b) != f_info["size_bytes"]:
                    raise ValueError(f"Byte size mismatch for {pkg_path}: {len(b)} != {f_info['size_bytes']}")
                sha = hashlib.sha256(b).hexdigest()
                if sha != f_info["sha256"]:
                    raise ValueError(f"SHA-256 mismatch for {pkg_path}: {sha} != {f_info['sha256']}")

                # Relative position within chart tree
                inner_rel = Path(f_path).relative_to(Path(chart_rel))
                dst_file = chart_stage_dir / inner_rel
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                dst_file.write_bytes(b)

            chart_yaml = chart_stage_dir / "Chart.yaml"
            if not chart_yaml.exists():
                raise FileNotFoundError(f"Staged chart '{role}' missing Chart.yaml")

            # Check for declared dependencies and verify vendoring under charts/
            deps = parse_chart_dependencies(chart_yaml)
            for dep in deps:
                charts_sub = chart_stage_dir / "charts"
                dep_dir = charts_sub / dep
                dep_archive = charts_sub / f"{dep}.tgz"
                if not (dep_dir.exists() or dep_archive.exists()):
                    raise FileNotFoundError(
                        f"Unvendored chart dependency '{dep}' declared in Chart.yaml but missing from {charts_sub}"
                    )

        # 2. Cluster Preflight & Secret Setup
        # StorageClass check: managed-csi
        sc_proc = _exec_command(
            args.kubectl_bin,
            ["get", "storageclass", "managed-csi", "-o", "json"],
            capture_output=True,
            text=True,
        )
        if sc_proc.returncode != 0:
            err = f"StorageClass 'managed-csi' preflight check failed: {sc_proc.stderr.strip()}"
            sys.stderr.write(f"{err}\n")
            write_result({
                "status": "failed",
                "failed_step": "storageclass_preflight",
                "error_message": err,
                "job_id": job_id,
                "dispatch_id": dispatch_id,
                "discovery_revision": discovery_revision,
                "config_digest": config_digest,
            })
            sys.exit(1)

        # Ensure Namespace exists
        ns_proc = _exec_command(
            args.kubectl_bin,
            ["get", "namespace", namespace, "-o", "json"],
            capture_output=True,
            text=True,
        )
        if ns_proc.returncode != 0:
            _exec_command(
                args.kubectl_bin,
                ["create", "namespace", namespace],
                capture_output=True,
                text=True,
            )

        # ACR Pull Secret Setup
        pull_sec = manifest.get("pull_secret") or {}
        acr_registry = pull_sec.get("registry") or dispatch.get("acr_registry", "")
        secret_name = pull_sec.get("name", "acr-pull-secret")
        if acr_registry:
            acr_username = os.environ.get("ACR_USERNAME") or os.environ.get("REGISTRY_USERNAME")
            acr_password = os.environ.get("ACR_PASSWORD") or os.environ.get("REGISTRY_PASSWORD")
            if not acr_username or not acr_password:
                try:
                    acr_name = acr_registry.split(".")[0]
                    az_res = _exec_command(
                        args.az_bin,
                        ["acr", "login", "--name", acr_name, "--expose-token", "--output", "json"],
                        capture_output=True,
                        text=True,
                    )
                    if az_res.returncode == 0:
                        az_data = json.loads(az_res.stdout)
                        acr_username = "00000000-0000-0000-0000-000000000000"
                        acr_password = az_data.get("accessToken")
                except Exception:
                    pass

            if acr_username and acr_password:
                _exec_command(
                    args.kubectl_bin,
                    [
                        "create", "secret", "docker-registry", secret_name,
                        f"--namespace={namespace}",
                        f"--docker-server={acr_registry}",
                        f"--docker-username={acr_username}",
                        f"--docker-password={acr_password}",
                        "--dry-run=client", "-o", "yaml",
                    ],
                    capture_output=True,
                    text=True,
                )

        # 3. Serial Release Installation & Readiness
        completed_releases: list[str] = []
        releases_status: dict[str, Any] = {}

        for rel in releases:
            role = rel["role"]
            release_name = rel["release_name"]
            service_name = rel["service_name"]
            workload_kind = rel.get("workload_kind", "Deployment")
            staged_chart_dir = str(Path(stage_dir) / role)

            helm_cmd = [
                "upgrade", "--install",
                release_name,
                staged_chart_dir,
                "--namespace", namespace,
                "--create-namespace",
                "--wait",
                "--timeout", "5m0s",
                "--reset-values",
            ]
            helm_proc = _exec_command(args.helm_bin, helm_cmd, capture_output=True, text=True)
            if helm_proc.returncode != 0:
                err = f"Helm install failed for release '{release_name}': {helm_proc.stderr.strip()}"
                sys.stderr.write(f"{err}\n")
                diag = _collect_bounded_diagnostics(args.kubectl_bin, namespace)
                write_result({
                    "status": "failed",
                    "failed_release": role,
                    "failed_step": "helm_install",
                    "completed_releases": completed_releases,
                    "error_message": err,
                    "diagnostics": diag,
                    "job_id": job_id,
                    "dispatch_id": dispatch_id,
                    "discovery_revision": discovery_revision,
                    "config_digest": config_digest,
                })
                sys.exit(1)

            # Explicit workload readiness check
            if role == "database":
                # Check PVC bound status
                pvc_proc = _exec_command(
                    args.kubectl_bin,
                    ["get", "pvc", "-n", namespace, "-o", "json"],
                    capture_output=True,
                    text=True,
                )
                if pvc_proc.returncode == 0:
                    try:
                        pvc_data = json.loads(pvc_proc.stdout)
                        unbound = [
                            p.get("metadata", {}).get("name")
                            for p in pvc_data.get("items", [])
                            if p.get("status", {}).get("phase") != "Bound"
                        ]
                        if unbound:
                            err = f"Database PVCs not bound: {unbound}"
                            sys.stderr.write(f"{err}\n")
                            diag = _collect_bounded_diagnostics(args.kubectl_bin, namespace)
                            write_result({
                                "status": "failed",
                                "failed_release": role,
                                "failed_step": "pvc_readiness",
                                "completed_releases": completed_releases,
                                "error_message": err,
                                "diagnostics": diag,
                                "job_id": job_id,
                                "dispatch_id": dispatch_id,
                                "discovery_revision": discovery_revision,
                                "config_digest": config_digest,
                            })
                            sys.exit(1)
                    except Exception:
                        pass

                # Check StatefulSet rollout status
                sts_proc = _exec_command(
                    args.kubectl_bin,
                    ["rollout", "status", f"statefulset/{service_name}", "-n", namespace, "--timeout=300s"],
                    capture_output=True,
                    text=True,
                )
                if sts_proc.returncode != 0:
                    err = f"StatefulSet rollout failed for '{service_name}': {sts_proc.stderr.strip()}"
                    sys.stderr.write(f"{err}\n")
                    diag = _collect_bounded_diagnostics(args.kubectl_bin, namespace)
                    write_result({
                        "status": "failed",
                        "failed_release": role,
                        "failed_step": "statefulset_rollout",
                        "completed_releases": completed_releases,
                        "error_message": err,
                        "diagnostics": diag,
                        "job_id": job_id,
                        "dispatch_id": dispatch_id,
                        "discovery_revision": discovery_revision,
                        "config_digest": config_digest,
                    })
                    sys.exit(1)

            else:
                # Deployment rollout status check
                deploy_proc = _exec_command(
                    args.kubectl_bin,
                    ["rollout", "status", f"deployment/{service_name}", "-n", namespace, "--timeout=300s"],
                    capture_output=True,
                    text=True,
                )
                if deploy_proc.returncode != 0:
                    err = f"Deployment rollout failed for '{service_name}': {deploy_proc.stderr.strip()}"
                    sys.stderr.write(f"{err}\n")
                    diag = _collect_bounded_diagnostics(args.kubectl_bin, namespace)
                    write_result({
                        "status": "failed",
                        "failed_release": role,
                        "failed_step": "deployment_rollout",
                        "completed_releases": completed_releases,
                        "error_message": err,
                        "diagnostics": diag,
                        "job_id": job_id,
                        "dispatch_id": dispatch_id,
                        "discovery_revision": discovery_revision,
                        "config_digest": config_digest,
                    })
                    sys.exit(1)

            completed_releases.append(role)
            releases_status[role] = {
                "status": "succeeded",
                "release_name": release_name,
                "service_name": service_name,
            }

        # 4. Frontend Endpoint Lookup
        fe_endpoint = manifest.get("frontend_endpoint") or {}
        fe_service_name = fe_endpoint.get("service_name") or "frontend"
        fe_ns = fe_endpoint.get("namespace") or namespace
        fe_port = fe_endpoint.get("port", 80)
        fe_scheme = fe_endpoint.get("scheme", "http")

        public_url: str | None = None
        for attempt in range(args.endpoint_attempts):
            svc_proc = _exec_command(
                args.kubectl_bin,
                ["get", "service", fe_service_name, "-n", fe_ns, "-o", "json"],
                capture_output=True,
                text=True,
            )
            if svc_proc.returncode == 0:
                try:
                    svc_data = json.loads(svc_proc.stdout)
                    ingress = svc_data.get("status", {}).get("loadBalancer", {}).get("ingress", [])
                    if ingress and isinstance(ingress, list):
                        first = ingress[0]
                        address = first.get("ip") or first.get("hostname")
                        if address:
                            if (fe_port == 80 and fe_scheme == "http") or (fe_port == 443 and fe_scheme == "https"):
                                public_url = f"{fe_scheme}://{address}"
                            else:
                                public_url = f"{fe_scheme}://{address}:{fe_port}"
                            break
                except Exception:
                    pass
            time.sleep(args.endpoint_interval_seconds)

        if not public_url:
            err = f"Frontend LoadBalancer IP/hostname was not assigned after {args.endpoint_attempts} attempts"
            sys.stderr.write(f"{err}\n")
            diag = _collect_bounded_diagnostics(args.kubectl_bin, namespace)
            write_result({
                "status": "failed",
                "failed_step": "frontend_endpoint",
                "completed_releases": completed_releases,
                "error_message": err,
                "diagnostics": diag,
                "job_id": job_id,
                "dispatch_id": dispatch_id,
                "discovery_revision": discovery_revision,
                "config_digest": config_digest,
            })
            sys.exit(1)

        # Full Success
        write_result({
            "status": "succeeded",
            "job_id": job_id,
            "dispatch_id": dispatch_id,
            "discovery_revision": discovery_revision,
            "config_digest": config_digest,
            "releases": releases_status,
            "frontend_endpoint": fe_endpoint,
            "public_url": public_url,
        })
        sys.exit(0)

    except Exception as exc:
        sys.stderr.write(f"Unexpected deployment failure: {exc}\n")
        write_result({
            "status": "failed",
            "failed_step": "staging_or_runtime_error",
            "error_message": str(exc),
            "job_id": job_id,
            "dispatch_id": dispatch_id,
            "discovery_revision": discovery_revision,
            "config_digest": config_digest,
        })
        sys.exit(1)

    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)


if __name__ == "__main__":
    main()

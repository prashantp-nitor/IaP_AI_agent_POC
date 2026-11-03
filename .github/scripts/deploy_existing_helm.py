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
import base64
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

import yaml

SAFE_ROLES_ORDER = ["database", "backend", "frontend"]


def _ensure_acr_pull_secret(kubectl_bin: str, namespace: str, registry: str, name: str) -> None:
    username = os.environ.get("ACR_USERNAME") or os.environ.get("REGISTRY_USERNAME")
    password = os.environ.get("ACR_PASSWORD") or os.environ.get("REGISTRY_PASSWORD")
    if not registry or not username or not password:
        raise ValueError("ACR pull secret requires a registry and durable ACR_USERNAME/ACR_PASSWORD credentials in CD secrets")
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    config = json.dumps({"auths": {registry: {"username": username, "password": password, "auth": auth}}})
    secret = {
        "apiVersion": "v1", "kind": "Secret",
        "metadata": {"name": name, "namespace": namespace},
        "type": "kubernetes.io/dockerconfigjson",
        "data": {".dockerconfigjson": base64.b64encode(config.encode()).decode()},
    }
    try:
        result = _exec_command(kubectl_bin, ["apply", "-f", "-", "-n", namespace],
                               input=json.dumps(secret), capture_output=True, text=True)
    except Exception:
        raise RuntimeError("Failed to apply ACR pull secret before Helm installation") from None
    if result.returncode != 0:
        raise RuntimeError("Failed to apply ACR pull secret before Helm installation; check Kubernetes Secret permissions")


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


def _set_path(document: dict[str, Any], path: list[str], value: str) -> None:
    if not path or any(not isinstance(part, str) or not part for part in path):
        raise ValueError("Image value paths must be non-empty string segments")
    cursor = document
    for part in path[:-1]:
        child = cursor.setdefault(part, {})
        if not isinstance(child, dict):
            raise ValueError(f"Image value path crosses a non-mapping value at {part!r}")
        cursor = child
    cursor[path[-1]] = value


def _approved_rendered_prerequisites(manifest: dict[str, Any], release: dict[str, Any]) -> dict[str, Any]:
    validation = manifest.get("validation") or {}
    effective_values = validation.get("effective_values") or {}
    release_values = effective_values.get(release.get("release_name")) or {}
    approved = release_values.get("rendered_prerequisites")
    if not isinstance(approved, dict) or approved != release.get("rendered_prerequisites"):
        raise ValueError(f"Validated prerequisites for release {release.get('release_name')!r} are missing or differ from the approved render")
    storage_classes = approved.get("storage_classes", [])
    workloads = approved.get("workloads", [])
    if (not isinstance(storage_classes, list) or any(not isinstance(name, str) or not name for name in storage_classes)
            or not isinstance(workloads, list)):
        raise ValueError("Validated render prerequisites have an invalid shape")
    for workload in workloads:
        if not isinstance(workload, dict) or not isinstance(workload.get("namespace"), str):
            raise ValueError("Validated workload prerequisite has an invalid namespace")
        secrets = workload.get("image_pull_secrets", [])
        if not isinstance(secrets, list) or any(not isinstance(name, str) or not name for name in secrets):
            raise ValueError("Validated image pull Secret references are invalid")
    return approved


def _validate_application_prerequisites(manifest: dict[str, Any], releases: list[dict[str, Any]]) -> None:
    validation_values = (manifest.get("validation") or {}).get("effective_values") or {}
    releases_by_id = {release.get("id"): release for release in releases}
    for app in manifest.get("applications", []):
        release = releases_by_id.get(app.get("release_id"))
        if release is None:
            raise ValueError("Approved application maps to an unknown release")
        values = validation_values.get(release.get("release_name")) or {}
        targets = [item for item in values.get("rendered_images", [])
                   if item.get("release_id") == app.get("release_id")
                   and item.get("container") == app.get("container")]
        if len(targets) != 1:
            raise ValueError(f"Application {app.get('application_id')!r} has no unique approved rendered workload")
        target = targets[0]
        namespace = target.get("namespace") or release.get("namespace")
        if namespace != release.get("namespace"):
            raise ValueError("Approved application workload namespace differs from its release")
        prerequisites = _approved_rendered_prerequisites(manifest, release)
        workloads = [item for item in prerequisites["workloads"]
                     if item.get("name") == target.get("workload") and item.get("namespace") == namespace]
        if len(workloads) != 1:
            raise ValueError("Application workload has no unique rendered prerequisite record")
        expected_secrets = [{"name": name, "namespace": namespace}
                            for name in workloads[0].get("image_pull_secrets", [])]
        if app.get("namespace") != namespace or app.get("pull_secrets") != expected_secrets:
            raise ValueError(f"Application {app.get('application_id')!r} pull access differs from its validated render")


def deploy_onboarding_manifest(
    manifest: dict[str, Any], dispatch: dict[str, Any], workspace: Path,
    helm_bin: str, kubectl_bin: str, endpoint_attempts: int, endpoint_interval: float,
) -> dict[str, Any]:
    """Deploy an approved schema-v2 candidate without consulting the original chart tree."""
    releases = manifest.get("releases")
    if manifest.get("schema_version") != 2 or manifest.get("pipeline_mode") not in ("cd_only", "ci_then_cd"):
        raise ValueError("Unsupported approved onboarding manifest")
    if not isinstance(releases, list) or not releases:
        raise ValueError("Approved onboarding manifest has no releases")
    profile_order = manifest.get("profile_order")
    roles = [release.get("role") for release in releases]
    if manifest.get("profile") == "three_chart" and (profile_order != ["database", "backend", "frontend"] or roles != profile_order):
        raise ValueError("Three-chart releases must remain database, backend, frontend")
    if manifest.get("profile") == "single_chart" and len(releases) != 1:
        raise ValueError("Single-chart onboarding requires exactly one release")
    _validate_application_prerequisites(manifest, releases)

    approved = manifest.get("candidate_files")
    if not isinstance(approved, list) or not approved:
        raise ValueError("Approved candidate file inventory is required")
    if len({item.get("path") for item in approved}) != len(approved):
        raise ValueError("Approved candidate file inventory contains duplicate paths")
    expected_digest = hashlib.sha256("\n".join(
        f"{item['path']}\0{item['sha256']}" for item in sorted(approved, key=lambda f: f["path"])
    ).encode()).hexdigest()
    if expected_digest != manifest.get("candidate_inventory_sha256"):
        raise ValueError("Approved candidate inventory digest mismatch")
    staged_root = Path(tempfile.mkdtemp(prefix="existing-helm-onboarding-"))
    by_path = {}
    approved_by_path = {item["path"]: item for item in approved}
    try:
        for item in approved:
            rel = item["path"]
            pkg = item["package_path"]
            _check_safe_posix_path(rel)
            _check_safe_posix_path(pkg)
            source = workspace / pkg
            if not source.is_file() or source.is_symlink():
                raise FileNotFoundError(f"Approved candidate file missing: {pkg}")
            data = source.read_bytes()
            if len(data) != item["size_bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError(f"Approved candidate file integrity check failed: {rel}")
            by_path[rel] = data

        for release in releases:
            release_id = release.get("id")
            chart_path = release.get("chart_path")
            _check_safe_posix_path(chart_path or "")
            chart_dir = staged_root / str(release_id)
            files = release.get("files")
            if not isinstance(files, list) or not files:
                raise ValueError(f"Release {release_id!r} has no approved files")
            expected_chart_files = {path for path in by_path if Path(path).is_relative_to(Path(chart_path))}
            declared_chart_files = {item.get("path") for item in files}
            if declared_chart_files != expected_chart_files:
                raise ValueError(f"Release {release_id!r} file list does not match its approved candidate inventory")
            for item in files:
                rel = item["path"]
                _check_safe_posix_path(rel)
                if rel not in by_path or not Path(rel).is_relative_to(Path(chart_path)):
                    raise ValueError(f"Release file is outside the approved candidate inventory: {rel}")
                if any(item.get(key) != approved_by_path[rel].get(key) for key in ("sha256", "size_bytes", "package_path")):
                    raise ValueError(f"Release file metadata differs from the approved candidate inventory: {rel}")
                dst = chart_dir / Path(rel).relative_to(Path(chart_path))
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(by_path[rel])
            if not (chart_dir / "Chart.yaml").is_file():
                raise ValueError(f"Approved chart {release_id!r} is missing Chart.yaml")
            for dependency in parse_chart_dependencies(chart_dir / "Chart.yaml"):
                if not ((chart_dir / "charts" / dependency).exists() or (chart_dir / "charts" / f"{dependency}.tgz").exists()):
                    raise FileNotFoundError(f"Unvendored chart dependency {dependency!r}")

        namespaces = sorted({release.get("namespace") for release in releases if release.get("namespace")})
        if not namespaces:
            raise ValueError("Approved releases must identify their target namespaces")
        namespace = releases[0].get("namespace")
        for release_namespace in namespaces:
            ns = _exec_command(kubectl_bin, ["get", "namespace", release_namespace, "-o", "json"], capture_output=True, text=True)
            if ns.returncode != 0:
                _exec_command(kubectl_bin, ["create", "namespace", release_namespace], capture_output=True, text=True)

        checked_pull_secrets: set[tuple[str, str]] = set()
        for release in releases:
            prerequisites = _approved_rendered_prerequisites(manifest, release)
            for workload in prerequisites.get("workloads", []):
                workload_namespace = workload.get("namespace") or release.get("namespace")
                for secret_name in workload.get("image_pull_secrets", []):
                    key = (secret_name, workload_namespace)
                    if key in checked_pull_secrets:
                        continue
                    found = _exec_command(kubectl_bin, ["get", "secret", secret_name, "-n", workload_namespace, "-o", "json"], capture_output=True, text=True)
                    if found.returncode != 0:
                        raise RuntimeError(f"Approved image pull Secret {secret_name!r} is missing from namespace {workload_namespace!r}; provide AKS-managed registry access or an existing namespace-local pull Secret")
                    checked_pull_secrets.add(key)

        build_refs = dispatch.get("build_image_references", {})
        build_ids = {item.get("application_id") for item in manifest.get("build_services", [])}
        if not isinstance(build_refs, dict) or set(build_refs) - build_ids:
            raise ValueError("Runtime image references may only override approved build targets")
        if build_ids - set(build_refs):
            raise ValueError("Generated image references are required for every approved build target")
        for service in manifest.get("build_services", []):
            app_id = service.get("application_id")
            registry, repository = service.get("registry"), service.get("repo_name")
            if not registry or not repository:
                raise ValueError(f"Approved build target {app_id!r} has no image destination")
            image = build_refs[app_id]
            if not isinstance(image, str):
                raise ValueError(f"Generated image reference for {app_id!r} must be a string")
            image_path, separator, tag = image.rpartition(":")
            expected_path = f"{registry.rstrip('/')}/{repository}"
            if not separator or image_path != expected_path or "@" in image or not tag:
                raise ValueError(f"Generated image reference for {app_id!r} does not match its approved repository")
            job_id = str(dispatch.get("job_id", "")).replace("-", "")[:8]
            expected_tag = manifest.get("generated_image_tag") or (f"sha-{job_id}" if job_id else "")
            if expected_tag and tag != expected_tag:
                raise ValueError(f"Generated image reference for {app_id!r} does not use the current run tag")
        statuses = {}
        checked_storage_classes: set[str] = set()
        for release in releases:
            rel_apps = [app for app in manifest.get("applications", []) if app.get("release_id") == release.get("id")]
            overlay_path = staged_root / f"{release['id']}-images.yaml"
            overlay: dict[str, Any] = {}
            for app in rel_apps:
                reference = (build_refs[app["application_id"]] if app["application_id"] in build_ids
                             else app["image_reference"])
                if not isinstance(reference, str) or not reference:
                    raise ValueError("Application image reference is missing")
                bindings = app.get("image_bindings", [])
                paths = {tuple(path) for binding in bindings for path in binding.get("value_paths", [])}
                image_paths = app.get("image_value_paths", {})
                if image_paths.get("repository"):
                    paths.add(tuple(image_paths["repository"]))
                if image_paths.get("tag"):
                    paths.add(tuple(image_paths["tag"]))
                if not paths:
                    raise ValueError(f"Application {app.get('application_id')} has no approved image bindings")
                repository, separator, tag = reference.partition("@")
                if separator:
                    image_repo, image_tag = repository, separator + tag
                else:
                    image_repo, _, image_tag = repository.rpartition(":")
                for path in sorted(paths):
                    # Bindings identify repository/tag fields explicitly; digest refs bind as a full image string.
                    leaf = path[-1].lower()
                    value = image_repo if leaf in ("repository", "repo") else image_tag if leaf in ("tag", "digest") else reference
                    _set_path(overlay, list(path), value)
            if overlay:
                overlay_path.write_text(yaml.safe_dump(overlay, sort_keys=False), encoding="utf-8")
            for storage_class in _approved_rendered_prerequisites(manifest, release).get("storage_classes", []):
                if storage_class in checked_storage_classes:
                    continue
                preflight = _exec_command(kubectl_bin, ["get", "storageclass", storage_class, "-o", "json"], capture_output=True, text=True)
                if preflight.returncode != 0:
                    raise RuntimeError(f"Required StorageClass {storage_class!r} preflight failed: {preflight.stderr.strip()}")
                checked_storage_classes.add(storage_class)
            helm_cmd = ["upgrade", "--install", release["release_name"], str(staged_root / str(release["id"])),
                        "--namespace", release.get("namespace", namespace), "--create-namespace", "--wait",
                        "--timeout", "5m0s", "--reset-values"]
            chart_dir = staged_root / str(release["id"])
            for values_file in [*release.get("values_files", []), *release.get("overlays", [])]:
                _check_safe_posix_path(values_file)
                if not Path(values_file).is_relative_to(Path(release["chart_path"])):
                    raise ValueError(f"Approved values file is outside chart {release['chart_path']}: {values_file}")
                staged_values = chart_dir / Path(values_file).relative_to(Path(release["chart_path"]))
                if not staged_values.is_file():
                    raise FileNotFoundError(f"Approved values file missing from staged chart: {values_file}")
                helm_cmd.extend(["--values", str(staged_values)])
            if overlay:
                helm_cmd.extend(["--values", str(overlay_path)])
            result = _exec_command(helm_bin, helm_cmd, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f"Helm install failed for {release['release_name']}: {result.stderr.strip()[:2000]}")
            for workload in release.get("workloads", []):
                kind = workload.get("kind")
                if kind not in ("Deployment", "StatefulSet"):
                    raise ValueError(f"Unsupported readiness workload kind: {kind}")
                target = f"{kind.lower()}/{workload['name']}"
                ready = _exec_command(kubectl_bin, ["rollout", "status", target, "-n", workload.get("namespace", namespace), "--timeout=300s"], capture_output=True, text=True)
                if ready.returncode:
                    raise RuntimeError(f"{kind} rollout failed for {workload['name']}: {ready.stderr.strip()[:2000]}")
            statuses[release["id"]] = {"status": "succeeded", "release_name": release["release_name"]}

        endpoint = manifest.get("endpoint") or {}
        protocol = endpoint.get("protocol", "http")
        if endpoint.get("kind") == "Ingress":
            result = _exec_command(kubectl_bin, ["get", "ingress", endpoint.get("name"), "-n", endpoint.get("namespace", namespace), "-o", "json"], capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f"Selected Ingress endpoint {endpoint.get('name')!r} was not found")
            rules = json.loads(result.stdout).get("spec", {}).get("rules", [])
            host = next((rule.get("host") for rule in rules if rule.get("host")), None)
            if not host:
                raise ValueError("Selected Ingress has no rendered host")
            public_url = f"{protocol}://{host}"
        else:
            service_name = endpoint.get("name")
            public_url = None
            for _ in range(endpoint_attempts):
                result = _exec_command(kubectl_bin, ["get", "service", service_name, "-n", endpoint.get("namespace", namespace), "-o", "json"], capture_output=True, text=True)
                if result.returncode == 0:
                    try:
                        ingress = json.loads(result.stdout).get("status", {}).get("loadBalancer", {}).get("ingress", [])
                        if ingress:
                            host = ingress[0].get("ip") or ingress[0].get("hostname")
                            if host:
                                port = endpoint.get("port")
                                suffix = f":{port}" if port and not (port == 80 and protocol == "http") and not (port == 443 and protocol == "https") else ""
                                public_url = f"{protocol}://{host}{suffix}"
                                break
                    except (ValueError, TypeError):
                        pass
                time.sleep(endpoint_interval)
            if not public_url:
                raise RuntimeError(f"Selected Service endpoint {service_name!r} did not receive a LoadBalancer address")
        return {"status": "succeeded", "releases": statuses, "endpoint": endpoint, "public_url": public_url}
    finally:
        shutil.rmtree(staged_root, ignore_errors=True)


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

    if manifest.get("schema_version") == 2:
        for key in ("candidate_revision", "candidate_inventory_sha256", "validation_identity", "pipeline_mode"):
            if key in dispatch and dispatch.get(key) != manifest.get(key):
                err = f"Dispatch/manifest parity failure on '{key}'"
                sys.stderr.write(f"{err}\n")
                write_result({"status": "failed", "failed_step": "parity_validation", "error_message": err,
                              "job_id": dispatch.get("job_id"), "dispatch_id": dispatch.get("dispatch_id")})
                sys.exit(1)
        try:
            result = deploy_onboarding_manifest(
                manifest, dispatch, workspace, args.helm_bin, args.kubectl_bin,
                args.endpoint_attempts, args.endpoint_interval_seconds,
            )
            result.update({"job_id": dispatch.get("job_id"), "dispatch_id": dispatch.get("dispatch_id"),
                           "discovery_revision": dispatch.get("discovery_revision"),
                           "config_digest": dispatch.get("config_digest")})
            write_result(result)
            sys.exit(0)
        except Exception as exc:
            err = str(exc)
            sys.stderr.write(f"Existing Helm onboarding deployment failed: {err}\n")
            diagnostics = _collect_bounded_diagnostics(args.kubectl_bin, dispatch.get("namespace", "default"))
            write_result({"status": "failed", "failed_step": "onboarding_deploy", "error_message": err,
                          "diagnostics": diagnostics,
                          "job_id": dispatch.get("job_id"), "dispatch_id": dispatch.get("dispatch_id"),
                          "discovery_revision": dispatch.get("discovery_revision"),
                          "config_digest": dispatch.get("config_digest")})
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
        _ensure_acr_pull_secret(args.kubectl_bin, namespace, acr_registry, secret_name)

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
            if role in ("backend", "frontend") and rel.get("image_repository_override"):
                helm_cmd.extend(["--set-string", f"image.repository={rel['image_repository_override']}"])
            if role in ("backend", "frontend"):
                helm_cmd.extend(["--set-string", f"imagePullSecret={secret_name}",
                                 "--set-json", "imagePullSecrets=" + json.dumps([{"name": secret_name}])])
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

                # Follow the database chart's workload kind without rewriting its templates.
                sts_proc = _exec_command(
                    args.kubectl_bin,
                    ["rollout", "status", f"{workload_kind.lower()}/{service_name}", "-n", namespace, "--timeout=300s"],
                    capture_output=True,
                    text=True,
                )
                if sts_proc.returncode != 0:
                    err = f"{workload_kind} rollout failed for '{service_name}': {sts_proc.stderr.strip()}"
                    sys.stderr.write(f"{err}\n")
                    diag = _collect_bounded_diagnostics(args.kubectl_bin, namespace)
                    write_result({
                        "status": "failed",
                        "failed_release": role,
                        "failed_step": f"{workload_kind.lower()}_rollout",
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

#!/usr/bin/env python3
"""
Classifies changed Terraform directories in iaap-output/ and derives
dynamic metadata: provider, resource category, backend type, region, stage, and state key.
"""
import os
import sys
import glob
import json
import re
import subprocess

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def get_changed_tf_directories(repo_root):
    event_name = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
    iaap_root = os.path.join(repo_root, "iaap-output")
    
    if not os.path.exists(iaap_root):
        return []

    # If manual dispatch, find all directories containing *.tf files
    if event_name == "workflow_dispatch":
        tf_files = glob.glob(os.path.join(iaap_root, "**", "*.tf"), recursive=True)
        dirs = sorted(list(set(os.path.dirname(f) for f in tf_files)))
        return dirs

    # Push event: find changed files using git diff
    before = os.environ.get("GITHUB_EVENT_BEFORE", "")
    after = os.environ.get("GITHUB_SHA", "HEAD")

    # If before is all zeroes (new branch) or empty, diff against HEAD~1
    if not before or set(before) == {"0"}:
        diff_cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
    else:
        diff_cmd = ["git", "diff", "--name-only", before, after]

    diff_out = run_cmd(diff_cmd)
    changed_lines = [line.strip() for line in diff_out.splitlines() if line.strip()]

    # Filter to iaap-output changes
    changed_dirs = set()
    for path in changed_lines:
        if path.startswith("iaap-output/"):
            full_path = os.path.join(repo_root, path)
            target_dir = os.path.dirname(full_path) if not os.path.isdir(full_path) else full_path
            
            # Find closest directory that contains .tf files
            if os.path.isdir(target_dir):
                if any(f.endswith(".tf") for f in os.listdir(target_dir)):
                    changed_dirs.add(target_dir)
                else:
                    # check subdirectories if a top-level project folder changed
                    sub_tfs = glob.glob(os.path.join(target_dir, "**", "*.tf"), recursive=True)
                    for stf in sub_tfs:
                        changed_dirs.add(os.path.dirname(stf))

    if not changed_dirs:
        # Fallback if git diff was empty (e.g. initial checkout)
        tf_files = glob.glob(os.path.join(iaap_root, "**", "*.tf"), recursive=True)
        if tf_files:
            tf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            changed_dirs.add(os.path.dirname(tf_files[0]))

    return sorted(list(changed_dirs))

def inspect_directory(dir_path, repo_root):
    rel_dir = os.path.relpath(dir_path, os.path.join(repo_root, "iaap-output")).replace("\\", "/")
    dir_basename = os.path.basename(dir_path).lower()
    
    # Read policy_input.json if present
    policy_path = os.path.join(dir_path, "policy_input.json")
    policy = {}
    if os.path.isfile(policy_path):
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                policy = json.load(f)
        except Exception:
            pass

    # Read all tf file contents in directory for pattern matching
    tf_contents = ""
    for tf_file in glob.glob(os.path.join(dir_path, "*.tf")):
        try:
            with open(tf_file, "r", encoding="utf-8", errors="ignore") as tf:
                tf_contents += "\n" + tf.read()
        except Exception:
            pass

    # 1. Determine Cloud Provider
    provider = policy.get("_provider")
    if not provider:
        if re.search(r'hashicorp/aws|provider\s+"aws"', tf_contents, re.IGNORECASE):
            provider = "aws"
        elif re.search(r'hashicorp/google|provider\s+"google"', tf_contents, re.IGNORECASE):
            provider = "gcp"
        elif re.search(r'hashicorp/azurerm|provider\s+"azurerm"', tf_contents, re.IGNORECASE):
            provider = "azure"
        else:
            provider = "azure"

    # 2. Determine Backend Type
    backend_type = "azurerm"
    backend_file = os.path.join(dir_path, "backend.tf")
    if os.path.isfile(backend_file):
        try:
            with open(backend_file, "r", encoding="utf-8", errors="ignore") as bf:
                btext = bf.read()
                if 'backend "s3"' in btext:
                    backend_type = "s3"
                elif 'backend "gcs"' in btext:
                    backend_type = "gcs"
                elif 'backend "azurerm"' in btext:
                    backend_type = "azurerm"
        except Exception:
            pass
    elif provider == "aws":
        backend_type = "s3"

    # 3. Determine Region
    region = policy.get("region", "")
    if not region:
        reg_match = re.search(r'(?:region|location)\s*=\s*"([^"]+)"', tf_contents)
        if reg_match:
            region = reg_match.group(1)
        else:
            region = "us-east-1" if provider == "aws" else "eastus"

    # 4. Determine Resource Category & Type
    res_type = policy.get("_resource_type", "").lower()
    rel_lower = rel_dir.lower()

    category = "general"
    stage = 2

    # High-priority: explicit resource_type from policy
    if res_type in ["vpc", "vnet"]:
        category = "networking"
        stage = 1
    elif res_type in ["eks_cluster", "kubernetes_service", "kubernetes_cluster", "gke"]:
        category = "kubernetes"
        stage = 2
    elif res_type in ["postgresql_flexible_server", "rds_instance", "elasticache_redis", "redis_cache"]:
        category = "database"
        stage = 2
    elif res_type in ["storage_account", "s3_bucket"]:
        category = "storage"
        stage = 2
    elif res_type in ["ec2_instance", "virtual_machine"]:
        category = "compute"
        stage = 2
    # Medium-priority: directory subfolder naming convention
    elif dir_basename in ["kubernetes_service"] or "kubernetes" in dir_basename:
        category = "kubernetes"
        stage = 2
    elif dir_basename in ["postgresql_flexible_server", "rds_instance", "redis_cache", "elasticache_redis"]:
        category = "database"
        stage = 2
    elif dir_basename in ["storage_account"]:
        category = "storage"
        stage = 2
    elif dir_basename in ["virtual_machine", "ec2_instance"]:
        category = "compute"
        stage = 2
    elif dir_basename.endswith("-vpc") or dir_basename.endswith("-vnet") or dir_basename in ["vpc", "vnet"]:
        category = "networking"
        stage = 1
    # Check actual Terraform resource / module definitions
    elif re.search(r'resource\s+"(?:azurerm_virtual_network|aws_vpc)"', tf_contents):
        category = "networking"
        stage = 1
    elif re.search(r'resource\s+"(?:azurerm_kubernetes_cluster|aws_eks_cluster)"|module\s+"(?:aks|eks)"', tf_contents):
        category = "kubernetes"
        stage = 2
    elif re.search(r'resource\s+"(?:azurerm_postgresql_flexible_server|aws_db_instance|aws_elasticache_cluster)"|module\s+"(?:postgresql|rds)"', tf_contents):
        category = "database"
        stage = 2
    elif re.search(r'resource\s+"(?:azurerm_storage_account|aws_s3_bucket)"', tf_contents):
        category = "storage"
        stage = 2
    elif re.search(r'resource\s+"(?:azurerm_linux_virtual_machine|aws_instance)"', tf_contents):
        category = "compute"
        stage = 2
    # Fallback to root directory patterns
    elif "-vpc" in rel_lower or "-vnet" in rel_lower:
        category = "networking"
        stage = 1
    elif any(k in rel_lower for k in ["aks", "eks", "gke", "cluster"]):
        category = "kubernetes"
        stage = 2
    elif any(k in rel_lower for k in ["postgres", "rds", "redis", "db"]):
        category = "database"
        stage = 2

    # 5. Derive State Key
    if "/" in rel_dir:
        state_key = f"{rel_dir.split('/')[0]}/terraform.tfstate"
    else:
        state_key = f"{rel_dir}/terraform.tfstate"

    # 6. Extract Job ID if present
    job_id = ""
    tags = policy.get("tags", {})
    if isinstance(tags, dict):
        job_id = tags.get("job_id", "")
    if not job_id:
        job_id = rel_dir

    return {
        "directory": rel_dir,
        "provider": provider,
        "region": region,
        "resource_category": category,
        "resource_type": res_type,
        "backend_type": backend_type,
        "state_key": state_key,
        "job_id": job_id,
        "stage": stage
    }

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dirs = get_changed_tf_directories(repo_root)

    items = [inspect_directory(d, repo_root) for d in dirs]
    stage1 = [i for i in items if i["stage"] == 1]
    stage2 = [i for i in items if i["stage"] == 2]

    print(f"Discovered {len(items)} target directories:")
    for it in items:
        print(f" - [{it['provider']}] [{it['resource_category']}] iaap-output/{it['directory']} (Stage {it['stage']})")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as gh:
            gh.write(f"stage1_network={json.dumps(stage1)}\n")
            gh.write(f"stage2_workload={json.dumps(stage2)}\n")
            gh.write(f"has_stage1={'true' if stage1 else 'false'}\n")
            gh.write(f"has_stage2={'true' if stage2 else 'false'}\n")
            gh.write(f"total_count={len(items)}\n")
    else:
        print(f"\nStage 1 (Networking): {len(stage1)} directories")
        print(f"Stage 2 (Workloads): {len(stage2)} directories")

if __name__ == "__main__":
    main()

region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "helm-only-deploy"
  job_id = "04c4d593-9a8e-4203-a5da-f9caedfc0bcf"
  project_folder = "helm-only-deploy-04c4d5"
}
vnet_name = "helm-only-depl-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "helm-only-depl-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "helm-only-depl-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "helm-only-depl-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "kK9v%GL2FAl8t0rb"
postgres_database_name = "appdb"
acr_name = "helmonlydeplacr04c4d5"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "helm-only-depl-kv-04c4d5"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

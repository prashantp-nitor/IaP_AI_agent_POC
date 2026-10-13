region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "qwertfit"
  job_id = "36521f5a-f04c-4909-b224-a8e7a3defbad"
  project_folder = "qwertfit-36521f"
}
vnet_name = "qwertfit-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "qwertfit-aks"
kubernetes_version = "1.34.4"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "qwertfit-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "qwertfit-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_admin_username = "pgadmin"
postgres_admin_password = "fkXs*vN8=7&MUrN9"
postgres_database_name = "appdb"
acr_name = "qwertfitacr36521f"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "qwertfitkv-36521f"
key_vault_sku = "standard"

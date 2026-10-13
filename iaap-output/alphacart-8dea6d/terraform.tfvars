region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "alphacart"
  job_id = "8dea6de9-c06a-4ae7-873f-a89234f7d486"
  project_folder = "alphacart-8dea6d"
}
vnet_name = "alphacart-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "alphacart-aks"
kubernetes_version = "1.34.4"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "alphacart-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "alphacart-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_admin_username = "pgadmin"
postgres_admin_password = "QX&r29uE&iZylXLB"
postgres_database_name = "appdb"
acr_name = "alphacartacr8dea6d"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "alphacartkv-8dea6d"
key_vault_sku = "standard"

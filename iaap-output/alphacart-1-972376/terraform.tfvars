region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "alphacart-1"
  job_id = "97237681-f6c8-4648-b987-740faeb5099b"
  project_folder = "alphacart-1-972376"
}
vnet_name = "alphacart-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "alphacart-1-aks"
kubernetes_version = "1.34.4"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "alphacart-1-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "alphacart-1-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_admin_username = "pgadmin"
postgres_admin_password = "lYLN8uJ7_K1&Bukf"
postgres_database_name = "appdb"
acr_name = "alphacartacr972376"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "alphacart-kv-972376"
key_vault_sku = "standard"

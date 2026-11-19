region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "three-tier-angular-dotnet"
  job_id = "028afec8-20df-4391-8cdb-1da5bb9adc1d"
  project_folder = "three-tier-angular-dotnet-028afe"
}
vnet_name = "three-tier-ang-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "three-tier-ang-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "three-tier-ang-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "three-tier-ang-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "HC%GusyBxO8cf-n4"
postgres_database_name = "appdb"
acr_name = "threetierangacr028afe"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "three-tier-ang-kv-028afe"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

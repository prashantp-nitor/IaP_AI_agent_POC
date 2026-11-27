region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "3-tier-app-fitcart"
  job_id = "5d805e0b-7240-415e-a107-2afa3ff1b6a7"
  project_folder = "3-tier-app-fitcart-5d805e"
}
vnet_name = "3-tier-app-fitcart-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "aks-3-tier-app-fitcart-aks"
kubernetes_version = "1.34"
node_count = 3
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "aks-3-tier-app-fitcart-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "3-tier-app-fitcart-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "y-Tech+c1G7!WnJ+"
postgres_database_name = "appdb"
acr_name = "3tierappfitcartacr5d805e"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "kv-3-tier-app-fit-5d805e"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

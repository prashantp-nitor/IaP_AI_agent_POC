region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "fitcart-app-test"
  job_id = "b43f6669-0ad7-4492-9b01-f1d8799cd6bd"
  project_folder = "fitcart-app-test-b43f66"
}
vnet_name = "fitcart-app-te-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "fitcart-app-te-aks"
kubernetes_version = "1.34"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "fitcart-app-te-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "fitcart-app-te-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "Bg=7fKa32n_Vl5VS"
postgres_database_name = "appdb"
acr_name = "fitcartappteacrb43f66"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "fitcart-app-te-kv-b43f66"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "python-fitcart-app-test"
  job_id = "111ccf33-e459-4020-9b7f-a7663784e84b"
  project_folder = "python-fitcart-app-test-111ccf"
}
vnet_name = "python-fitcart-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "python-fitcart-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "python-fitcart-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "python-fitcart-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "67EEx5!n!-YRLLyW"
postgres_database_name = "appdb"
acr_name = "pythonfitcartacr111ccf"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "python-fitcart-kv-111ccf"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

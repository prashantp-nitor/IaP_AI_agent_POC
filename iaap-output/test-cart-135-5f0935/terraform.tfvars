region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-cart-135"
  job_id = "5f0935e8-ee84-4e1d-8fd1-c77b7b19e0ba"
  project_folder = "test-cart-135-5f0935"
}
vnet_name = "test-cart-135-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-cart-135-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-cart-135-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-cart-135-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "WPsRsAD&&ao3h8s%"
postgres_database_name = "appdb"
acr_name = "testcart135acr5f0935"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-cart-135-kv-5f0935"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

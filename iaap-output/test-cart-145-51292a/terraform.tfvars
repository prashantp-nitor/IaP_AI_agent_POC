region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-cart-145"
  job_id = "51292ab9-04a6-4897-9401-b5c1d51f521d"
  project_folder = "test-cart-145-51292a"
}
vnet_name = "test-cart-145-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-cart-145-aks"
kubernetes_version = "1.34"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-cart-145-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-cart-145-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "dpe=FeD%O246qVHr"
postgres_database_name = "appdb"
acr_name = "testcart145acr51292a"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-cart-145-kv-51292a"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

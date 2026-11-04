region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-demo-4"
  job_id = "382563c8-ecb0-48e1-95ac-2f6560fcab7c"
  project_folder = "test-demo-4-382563"
}
vnet_name = "test-demo-4-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-demo-4-aks"
kubernetes_version = "1.34"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-demo-4-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-demo-4-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "e2OID@z-8VmPG8dr"
postgres_database_name = "appdb"
acr_name = "testdemo4acr382563"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-demo-4-kv-382563"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

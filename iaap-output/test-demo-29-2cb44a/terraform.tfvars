region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-demo-29"
  job_id = "2cb44a1b-55c7-467d-8071-61d0c5a1fe7b"
  project_folder = "test-demo-29-2cb44a"
}
vnet_name = "test-demo-29-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-demo-29-aks"
kubernetes_version = "1.34"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-demo-29-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-demo-29-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "l7wVd2ph&I63hrHW"
postgres_database_name = "appdb"
acr_name = "testdemo29acr2cb44a"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-demo-29-kv-2cb44a"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

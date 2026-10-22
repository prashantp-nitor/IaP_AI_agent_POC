region = "westus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-demo-22"
  job_id = "d3c09b76-a7fe-4111-9bd9-4ceb8751c56d"
  project_folder = "test-demo-22-d3c09b"
}
vnet_name = "test-demo-22-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-demo-22-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-demo-22-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-demo-22-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "b22yHVR_%3*JhfUV"
postgres_database_name = "appdb"
acr_name = "testdemo22acrd3c09b"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-demo-22-kv-d3c09b"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

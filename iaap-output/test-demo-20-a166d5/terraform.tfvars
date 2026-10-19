region = "westus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-demo-20"
  job_id = "a166d5f9-7cc7-47ff-b57f-d51cd184f532"
  project_folder = "test-demo-20-a166d5"
}
vnet_name = "test-demo-20-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-demo-20-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-demo-20-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-demo-20-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "*&u1jb+%ln3QW&1m"
postgres_database_name = "appdb"
acr_name = "testdemo20acra166d5"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-demo-20-kv-a166d5"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

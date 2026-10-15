region = "westus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-demo-17"
  job_id = "37af5aed-d1b6-4e00-856b-8e75e5c1314b"
  project_folder = "test-demo-17-37af5a"
}
vnet_name = "test-demo-17-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-demo-17-aks"
kubernetes_version = "1.34.4"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-demo-17-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-demo-17-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_admin_username = "pgadmin"
postgres_admin_password = "YFV03bhQ2+ht*5al"
postgres_database_name = "appdb"
acr_name = "testdemo17acr37af5a"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "test-demo-17-kv-37af5a"
key_vault_sku = "standard"

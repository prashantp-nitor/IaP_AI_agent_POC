region = "eastus2"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "test-demo-19"
  job_id = "b1bc1de1-496e-49a2-adab-bb4e986efc57"
  project_folder = "test-demo-19-b1bc1d"
}
vnet_name = "test-demo-19-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "test-demo-19-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "test-demo-19-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "test-demo-19-db"
postgres_sku_name = "B_Standard_B2s"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "O=vhav#JENjio4Q6"
postgres_database_name = "appdb"
acr_name = "testdemo19acrb1bc1d"
acr_sku = "Standard"
acr_admin_enabled = true
acr_zone_redundancy_enabled = false
key_vault_name = "test-demo-19-kv-b1bc1d"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

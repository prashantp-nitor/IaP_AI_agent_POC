region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "python-app-test"
  job_id = "5500de78-d722-42eb-8ca5-e1f6a9d1bbc2"
  project_folder = "python-app-test-5500de"
}
vnet_name = "python-app-tes-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "python-app-tes-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "python-app-tes-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "python-app-tes-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "k-Jd3+&6EtA_KZtU"
postgres_database_name = "appdb"
acr_name = "pythonapptesacr5500de"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "python-app-tes-kv-5500de"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

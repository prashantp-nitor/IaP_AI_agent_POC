region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "newdeply29-10"
  job_id = "367ea818-9af2-417b-b2ca-326ad5c806bd"
  project_folder = "newdeply29-10-367ea8"
}
vnet_name = "newdeply29-10-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "newdeply29-10-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "newdeply29-10-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "newdeply29-10-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "kk8S&kKWmxTo8BGG"
postgres_database_name = "appdb"
acr_name = "newdeply2910acr367ea8"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "newdeply29-10-kv-367ea8"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

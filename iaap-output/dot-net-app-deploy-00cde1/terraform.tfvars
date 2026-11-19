region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "dot-net-app-deploy"
  job_id = "00cde140-58b8-46c9-b547-7f100c45d5c1"
  project_folder = "dot-net-app-deploy-00cde1"
}
vnet_name = "dot-net-app-de-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "dot-net-app-de-aks"
kubernetes_version = "1.34"
node_count = 1
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "dot-net-app-de-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "dot-net-app-de-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "Nz1I!NWgZAtZAA8a"
postgres_database_name = "appdb"
acr_name = "dotnetappdeacr00cde1"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "dot-net-app-de-kv-00cde1"
key_vault_sku = "standard"
key_vault_soft_delete_retention_days = 90

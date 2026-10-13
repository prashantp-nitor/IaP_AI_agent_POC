region = "westeurope"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "tyuiocart"
  job_id = "653f34e6-e18b-4f49-8673-0b414d1c357f"
  project_folder = "tyuiocart-653f34"
}
vnet_name = "tyuiocart-network"
address_space = [
  "10.0.0.0/16",
]
cluster_name = "tyuiocart-aks"
kubernetes_version = "1.34.4"
node_count = 2
node_vm_size = "Standard_D2s_v3"
network_plugin = "azure"
network_policy = "azure"
dns_prefix = "tyuiocart-aks"
enable_rbac = true
os_disk_size_gb = 30
postgres_server_name = "tyuiocart-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_admin_username = "pgadmin"
postgres_admin_password = "QqMSuvzUuw%_4b3X"
postgres_database_name = "appdb"
acr_name = "tyuiocartacr653f34"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "tyuiocartkv-653f34"
key_vault_sku = "standard"

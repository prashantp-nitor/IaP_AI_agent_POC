region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "3-tier-app-fitcart"
  job_id = "471670d7-f56f-42a4-b9c6-9a1a98617582"
  project_folder = "3-tier-app-fitcart-471670"
}
vnet_name = "3-tier-app-fitcart-network"
address_space = [
  "10.0.0.0/16",
]
postgres_server_name = "3-tier-app-fit-dbnew161026"
postgres_sku_name = "B_Standard_B2s"
postgres_version = "15"
postgres_storage_mb = 32768
postgres_backup_retention_days = 14
postgres_admin_username = "pgadmin"
postgres_admin_password = "_*nPNZv%F0nMXfCA"
postgres_database_name = "appdb"

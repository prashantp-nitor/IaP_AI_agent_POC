region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "3-tier-app-fitcart"
  job_id = "4491784c-8e67-4f50-932e-af079e8e2d73"
  project_folder = "3-tier-app-fitcart-449178"
}
vnet_name = "testnw1151026"
address_space = [
  "10.0.0.0/16",
]
postgres_server_name = "3-tier-app-fitcart-db"
postgres_sku_name = "B_Standard_B1ms"
postgres_version = "14"
postgres_storage_mb = 32768
postgres_backup_retention_days = 7
postgres_admin_username = "pgadmin"
postgres_admin_password = "Uc40p#h08*+feo%N"
postgres_database_name = "appdb"
acr_name = "testacr151026449178"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false
key_vault_name = "testkv151026-449178"
key_vault_sku = "standard"

# --- Database (PostgreSQL Flexible Server Module) ---

module "postgres" {
  source  = "Azure/avm-res-dbforpostgresql-flexibleserver/azurerm"
  version = "0.2.3"

  name = var.postgres_server_name
  resource_group_name = data.azurerm_resource_group.rg.name
  location = var.region
  sku_name = var.postgres_sku_name
  server_version = var.postgres_version
  storage_mb = var.postgres_storage_mb
  backup_retention_days = var.postgres_backup_retention_days
  administrator_login = var.postgres_admin_username
  administrator_password = var.postgres_admin_password
  enable_telemetry = false
  tags = merge({ ManagedBy = "IAAP" }, var.extra_tags)
  public_network_access_enabled = true
}

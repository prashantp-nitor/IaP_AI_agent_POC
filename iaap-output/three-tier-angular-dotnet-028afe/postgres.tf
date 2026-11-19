# --- Database (PostgreSQL Flexible Server Module) ---

resource "azurerm_private_dns_zone" "postgres" {
  name                = "${var.postgres_server_name}.private.postgres.database.azure.com"
  resource_group_name = data.azurerm_resource_group.rg.name
  tags                = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "${var.postgres_server_name}-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  resource_group_name   = data.azurerm_resource_group.rg.name
  virtual_network_id    = module.vnet.resource_id
  tags                  = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

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
  high_availability = null
  delegated_subnet_id = module.vnet.subnets["postgres_subnet"].resource_id
  public_network_access_enabled = false
  private_dns_zone_id = azurerm_private_dns_zone.postgres.id
  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
}

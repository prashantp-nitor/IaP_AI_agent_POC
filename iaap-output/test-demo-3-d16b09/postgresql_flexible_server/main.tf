data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

module "postgresql" {
  source  = "Azure/avm-res-dbforpostgresql-flexibleserver/azurerm"
  version = "0.2.3"

  name = var.server_name
  resource_group_name = data.azurerm_resource_group.rg.name
  location = data.azurerm_resource_group.rg.location
  sku_name = var.sku_name
  server_version = var.pg_version
  storage_mb = var.storage_mb
  backup_retention_days = var.backup_retention_days
  administrator_login = var.administrator_login
  administrator_password = var.administrator_password
  public_network_access_enabled = true
  enable_telemetry = false
  tags = merge({
    ManagedBy = "IAAP"
    environment = "prod"
    owner = "admin@example.com"
    project = "test-demo-3"
    job_id = "d16b097a-347d-4e1d-b260-53c78fb0db35"
    project_folder = "test-demo-3-d16b09"
  }, var.extra_tags)
}

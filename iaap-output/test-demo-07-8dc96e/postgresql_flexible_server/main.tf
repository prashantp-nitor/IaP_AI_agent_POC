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
    project = "test-demo-07"
    job_id = "8dc96e2c-d9c2-44e2-96f6-35fb60b598d8"
    project_folder = "test-demo-07-8dc96e"
  }, var.extra_tags)
}

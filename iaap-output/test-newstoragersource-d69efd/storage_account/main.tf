data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

module "storage" {
  source  = "Azure/avm-res-storage-storageaccount/azurerm"
  version = "0.10.0"

  name = var.account_name
  parent_id = data.azurerm_resource_group.rg.id
  location = data.azurerm_resource_group.rg.location
  account_tier = var.account_tier
  account_replication_type = var.replication
  account_sku_name = "${var.account_tier}_${var.replication}"
  min_tls_version = "TLS1_2"
  https_traffic_only_enabled = true
  allow_nested_items_to_be_public = false
  enable_telemetry = false
  tags = merge({
    ManagedBy = "IAAP"
    environment = "prod"
    owner = "admin@example.com"
    project = "test-newstoragersource"
    job_id = "d69efde4-fb2c-4f1e-829a-79a57aafb3e1"
    project_folder = "test-newstoragersource-d69efd"
  }, var.extra_tags)
  access_tier = var.access_tier
}

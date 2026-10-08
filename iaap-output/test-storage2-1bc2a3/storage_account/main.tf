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
  min_tls_version = "TLS1_2"
  https_traffic_only_enabled = true
  allow_nested_items_to_be_public = false
  enable_telemetry = false
  tags = merge({
    ManagedBy = "IAAP"
    environment = "prod"
    owner = "admin@example.com"
    project = "test-storage2"
    job_id = "1bc2a356-276f-4b3e-a0c1-0bbab076f159"
    project_folder = "test-storage2-1bc2a3"
  }, var.extra_tags)
  access_tier = var.access_tier
}

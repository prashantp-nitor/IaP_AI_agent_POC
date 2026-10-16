# --- Azure Storage Account ---

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
    owner = "user@company.com"
    project = "3-tier-app-fitcart"
    job_id = "20d70859-4937-4279-88de-b6570ec0cfc7"
    project_folder = "3-tier-app-fitcart-20d708"
  }, var.extra_tags)
  access_tier = var.access_tier
}

# --- Container Registry (ACR Module) ---

module "acr" {
  source  = "Azure/avm-res-containerregistry-registry/azurerm"
  version = "0.8.0"

  name = var.acr_name
  location = var.region
  resource_group_name = data.azurerm_resource_group.rg.name
  sku = var.acr_sku
  admin_enabled = var.acr_admin_enabled
  zone_redundancy_enabled = var.acr_sku == "Premium" ? var.acr_zone_redundancy_enabled : false
  enable_telemetry = false
  tags = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

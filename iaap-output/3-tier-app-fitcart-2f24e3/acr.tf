# --- Container Registry (ACR Module) ---

module "acr" {
  source  = "Azure/avm-res-containerregistry-registry/azurerm"
  version = "0.8.0"

  name = var.acr_name
  location = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  sku = var.acr_sku
  admin_enabled = var.acr_admin_enabled
  enable_telemetry = false
  tags = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

# --- Grant AKS Kubelet Identity AcrPull Permission on ACR ---
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = module.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = module.acr.resource_id
  skip_service_principal_aad_check = true
}

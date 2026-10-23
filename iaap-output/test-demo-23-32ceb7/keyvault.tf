# --- Key Vault Module ---

data "azurerm_client_config" "current" {}

resource "azurerm_private_dns_zone" "keyvault" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = data.azurerm_resource_group.rg.name
  tags                = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

resource "azurerm_private_dns_zone_virtual_network_link" "keyvault" {
  name                  = "${var.key_vault_name}-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.keyvault.name
  resource_group_name   = data.azurerm_resource_group.rg.name
  virtual_network_id    = module.vnet.resource_id
  tags                  = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

module "key_vault" {
  source  = "Azure/avm-res-keyvault-vault/azurerm"
  version = "0.10.2"

  name = var.key_vault_name
  location = var.region
  resource_group_name = data.azurerm_resource_group.rg.name
  tenant_id = data.azurerm_client_config.current.tenant_id
  sku_name = var.key_vault_sku
  soft_delete_retention_days = var.key_vault_soft_delete_retention_days
  purge_protection_enabled = false
  enable_telemetry = false
  tags = merge({ ManagedBy = "IAAP" }, var.extra_tags)
  public_network_access_enabled = false
  private_endpoints = {
    primary = {
      name = "${var.key_vault_name}-pe"
      subnet_resource_id = module.vnet.subnets["aks_subnet"].resource_id
      private_dns_zone_resource_ids = [azurerm_private_dns_zone.keyvault.id]
    }
  }
}

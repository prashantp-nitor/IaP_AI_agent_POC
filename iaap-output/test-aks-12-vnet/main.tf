data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

module "vnet" {
  source  = "Azure/avm-res-network-virtualnetwork/azurerm"
  version = "0.14.1"

  name = var.vnet_name
  parent_id = data.azurerm_resource_group.rg.id
  location = data.azurerm_resource_group.rg.location
  address_space = var.address_space
  subnets = {
    subnet_3 = {
      name = "subnet-3"
      address_prefixes = [
        "10.0.3.0/24",
      ]
    }
  }
  enable_telemetry = false
  tags = merge({
    ManagedBy = "IAAP"
  }, var.extra_tags)
}

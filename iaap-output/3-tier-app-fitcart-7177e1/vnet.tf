# --- Networking (VNet Module) ---

module "vnet" {
  source  = "Azure/avm-res-network-virtualnetwork/azurerm"
  version = "0.14.1"

  name = var.vnet_name
  parent_id = data.azurerm_resource_group.rg.id
  location = var.region
  address_space = var.address_space
  subnets = {
    app_subnet = {
      name = "app-subnet"
      address_prefixes = [
        "10.0.1.0/24",
      ]
    }
    db_subnet = {
      name = "db-subnet"
      address_prefixes = [
        "10.0.2.0/24",
      ]
    }
    ingress_subnet = {
      name = "ingress-subnet"
      address_prefixes = [
        "10.0.3.0/24",
      ]
    }
  }
  enable_telemetry = false
  tags = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

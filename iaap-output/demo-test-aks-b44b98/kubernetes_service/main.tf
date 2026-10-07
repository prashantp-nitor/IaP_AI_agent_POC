data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# --- Networking ---

resource "azurerm_virtual_network" "aks_vnet" {
  name                = "aks-cluster-2-vnet"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-cluster-2-subnet"
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.aks_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

module "aks" {
  source  = "Azure/avm-res-containerservice-managedcluster/azurerm"
  version = "0.8.3"

  name = var.cluster_name
  parent_id = data.azurerm_resource_group.rg.id
  location = data.azurerm_resource_group.rg.location
  dns_prefix = var.dns_prefix
  kubernetes_version = var.kubernetes_version
  default_agent_pool = {
    name = "default"
    vm_size = var.node_vm_size
    node_count = var.node_count
    os_disk_size_gb = var.os_disk_size_gb
    vnet_subnet_id = azurerm_subnet.aks_subnet.id
  }
  network_profile = {
    network_plugin = var.network_plugin
    network_policy = var.network_policy
    load_balancer_sku = "standard"
    service_cidr = "10.2.0.0/24"
    dns_service_ip = "10.2.0.10"
  }
  oidc_issuer_profile = {
    enabled = true
  }
  managed_identities = {
    system_assigned = true
  }
  enable_rbac = var.enable_rbac
  enable_telemetry = false
  tags = merge({
    ManagedBy = "IAAP"
    environment = "prod"
    owner = "admin@example.com"
    project = "demo-test-aks"
    job_id = "b44b9885-3b89-47d7-87f6-aaa639a1f2f0"
    project_folder = "demo-test-aks-b44b98"
  }, var.extra_tags)
}

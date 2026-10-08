data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# --- Existing Networking Reference ---

data "azurerm_virtual_network" "aks_vnet" {
  name                = "production-network"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_subnet" "aks_subnet" {
  name                 = "frontend-subnet"
  virtual_network_name = data.azurerm_virtual_network.aks_vnet.name
  resource_group_name  = data.azurerm_resource_group.rg.name
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
    vnet_subnet_id = data.azurerm_subnet.aks_subnet.id
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
    project = "daas-aks"
    job_id = "ebe33385-d97c-4dc1-8e5b-d0577cadda16"
    project_folder = "daas-aks-ebe333"
  }, var.extra_tags)
}

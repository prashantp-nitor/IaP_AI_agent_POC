# --- Kubernetes Service (AKS Module) ---

data "azurerm_virtual_network" "aks_vnet" {
  name                = "asdfg-fitcart-network"
  resource_group_name = "AZET-RG-Daas-Platform"
}

data "azurerm_subnet" "aks_subnet" {
  name                 = "app-subnet"
  virtual_network_name = data.azurerm_virtual_network.aks_vnet.name
  resource_group_name  = "AZET-RG-Daas-Platform"
}

module "aks" {
  source  = "Azure/avm-res-containerservice-managedcluster/azurerm"
  version = "0.6.6"

  name = var.cluster_name
  parent_id = data.azurerm_resource_group.rg.id
  location = var.region
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
  tags = merge({ ManagedBy = "IAAP" }, var.extra_tags)
}

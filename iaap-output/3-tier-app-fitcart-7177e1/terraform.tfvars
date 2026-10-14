region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "3-tier-app-fitcart"
  job_id = "7177e142-8755-45bc-b775-eb21e6901d95"
  project_folder = "3-tier-app-fitcart-7177e1"
}
vnet_name = "3-tier-app-fitcart-network"
address_space = [
  "10.0.0.0/16",
]
acr_name = "3tierappfitcartacr7177e1"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false

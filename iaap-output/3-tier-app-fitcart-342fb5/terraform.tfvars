region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "3-tier-app-fitcart"
  job_id = "342fb5d9-762a-4842-a1c3-5cd840651a28"
  project_folder = "3-tier-app-fitcart-342fb5"
}
vnet_name = "3-tier-app-fitcart-network"
address_space = [
  "10.0.0.0/16",
]
acr_name = "3tierappfitcartacr342fb5"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false

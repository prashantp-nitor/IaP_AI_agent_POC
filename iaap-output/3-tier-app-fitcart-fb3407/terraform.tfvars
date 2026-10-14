region = "eastus"
resource_group_name = "AZET-RG-Daas-Platform"
extra_tags = {
  ManagedBy = "IAAP"
  environment = "prod"
  owner = "user@company.com"
  project = "3-tier-app-fitcart"
  job_id = "fb3407db-94ce-4409-ae32-572a45f75bf1"
  project_folder = "3-tier-app-fitcart-fb3407"
}
vnet_name = "3-tier-app-fitcart-network"
address_space = [
  "10.0.0.0/16",
]
acr_name = "3tierappfitcartacrfb3407"
acr_sku = "Standard"
acr_admin_enabled = false
acr_zone_redundancy_enabled = false

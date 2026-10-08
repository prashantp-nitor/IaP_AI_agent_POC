variable "region" {
  description = "Azure region for all resources"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "AZET-RG-Daas-Platform"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "aks-cluster-1"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the AKS cluster"
  type        = string
  default     = "1.34.4"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 3
}

variable "node_vm_size" {
  description = "VM size for default node pool nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "network_plugin" {
  description = "Network plugin (azure or kubenet)"
  type        = string
  default     = "azure"
}

variable "network_policy" {
  description = "Network policy enforcement engine (azure or calico, empty to disable)"
  type        = string
  default     = "azure"
}

variable "dns_prefix" {
  description = "DNS prefix for the AKS cluster"
  type        = string
  default     = "aks-cluster-1"
}

variable "enable_rbac" {
  description = "Enable Kubernetes RBAC"
  type        = bool
  default     = true
}

variable "os_disk_size_gb" {
  description = "OS disk size in GB for each node in the default node pool"
  type        = number
  default     = 128
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}

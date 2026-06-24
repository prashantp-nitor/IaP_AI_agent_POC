variable "project_id" {
  description = "GCP project ID — override via TF_VAR_project_id env var"
  type        = string
  default     = "demo-project"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "demo-gke"
}

variable "node_machine_type" {
  description = "Machine type for cluster nodes"
  type        = string
  default     = "e2-medium"
}

variable "node_count" {
  description = "Number of nodes per zone"
  type        = number
  default     = 2
}

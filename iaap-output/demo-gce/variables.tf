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

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "instance_name" {
  description = "Compute Engine instance name"
  type        = string
  default     = "demo-gce"
}

variable "machine_type" {
  description = "Machine type"
  type        = string
  default     = "e2-medium"
}

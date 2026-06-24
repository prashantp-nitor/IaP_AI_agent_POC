            terraform {
              required_providers {
                google = {
                  source  = "hashicorp/google"
                  version = "~> 5.0"
                }
              }
              backend "s3" {}
            }

            provider "google" {
              project = var.project_id
              region  = var.region
            }

            resource "google_container_cluster" "this" {
              name     = var.cluster_name
              location = var.region

              remove_default_node_pool = true
  initial_node_count       = 1

              release_channel {
                channel = "STABLE"
              }

              resource_labels = {
                managed_by = "iaap"

              }

              deletion_protection = false
            }

            resource "google_container_node_pool" "default" {
  name       = "default"
  cluster    = google_container_cluster.this.id
  node_count = var.node_count

  node_config {
    machine_type = var.node_machine_type
    disk_type    = "pd-ssd"
    disk_size_gb = 50

    labels = {
      managed_by = "iaap"
    }
  }
}


            output "cluster_name" {
              value = google_container_cluster.this.name
            }

            output "cluster_endpoint" {
              value     = google_container_cluster.this.endpoint
              sensitive = true
            }

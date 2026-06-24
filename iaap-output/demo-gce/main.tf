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
              zone    = var.zone
            }

            resource "google_compute_instance" "this" {
              name         = var.instance_name
              machine_type = var.machine_type
              zone         = var.zone



              boot_disk {
                initialize_params {
                  image = "debian-cloud/debian-12"
                  size  = 20
                  type  = "pd-ssd"
                }
              }

            network_interface {
  network = "default"
  access_config {}
}

              labels = {
                managed_by = "iaap"

              }
            }

            output "instance_id" {
              value = google_compute_instance.this.id
            }

            output "external_ip" {
  value = google_compute_instance.this.network_interface[0].access_config[0].nat_ip
}


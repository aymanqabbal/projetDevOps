terraform {
  required_version = ">= 1.0.0"
  required_providers {
    virtualbox = {
      source  = "terra-farm/virtualbox"
      version = "~> 0.2.2"
    }
  }
}

provider "virtualbox" {}

resource "virtualbox_vm" "jenkins" {
  name   = var.jenkins_vm_name
  cpus   = var.jenkins_cpus
  memory = var.jenkins_memory
}

resource "virtualbox_vm" "kubernetes" {
  name   = var.k8s_vm_name
  cpus   = var.k8s_cpus
  memory = var.k8s_memory
}
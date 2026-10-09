variable "jenkins_vm_name" {
  description = "Nom de la machine virtuelle Jenkins"
  type        = string
  default     = "jenkins-server"
}

variable "jenkins_cpus" {
  description = "Nombre de vCPUs alloués au serveur Jenkins"
  type        = number
  default     = 2
}

variable "jenkins_memory" {
  description = "Mémoire allouée au serveur Jenkins (en mib)"
  type        = string
  default     = "4096 mib"
}

variable "k8s_vm_name" {
  description = "Nom de la machine virtuelle du cluster Kubernetes"
  type        = string
  default     = "k8s-node"
}

variable "k8s_cpus" {
  description = "Nombre de vCPUs alloués au nœud Kubernetes"
  type        = number
  default     = 4
}

variable "k8s_memory" {
  description = "Mémoire allouée au nœud Kubernetes (en mib)"
  type        = string
  default     = "6144 mib"
}

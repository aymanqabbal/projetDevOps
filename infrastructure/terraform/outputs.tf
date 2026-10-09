output "jenkins_vm_details" {
  description = "Informations sur la VM Jenkins"
  value = {
    name   = virtualbox_vm.jenkins.name
    cpus   = virtualbox_vm.jenkins.cpus
    memory = virtualbox_vm.jenkins.memory
  }
}

output "kubernetes_vm_details" {
  description = "Informations sur la VM Kubernetes"
  value = {
    name   = virtualbox_vm.kubernetes.name
    cpus   = virtualbox_vm.kubernetes.cpus
    memory = virtualbox_vm.kubernetes.memory
  }
}

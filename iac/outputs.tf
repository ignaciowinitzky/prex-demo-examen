
output "project_name" {
  description = "Nombre del proyecto"
  value       = var.project_name
}

output "environment" {
  description = "Entorno (dev/qa/pre/prod)"
  value       = var.environment
}

output "product" {
  description = "Nombre del Producto"
  value       = var.product
}

output "cluster_name" {
  description = "Nombre del cluster EKS"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint del cluster EKS"
  value       = module.eks.cluster_endpoint
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "prex-demo"
}

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Entorno (dev/qa/pre/prod)"
  type        = string
  default     = "dev"
}

variable "product" {
  description = "Nombre del Producto"
  type        = string
  default     = "prex-demo"
}

variable "cidr" {
  description = "CIDR principal de la VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "Lista de subnets privadas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnets" {
  description = "Lista de subnets publicas"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "enable_nat_gateway" {
  description = "Habilitar NAT Gateway"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Usar un solo NAT Gateway"
  type        = bool
  default     = true
}

variable "cluster_version" {
  description = "Versión de Kubernetes para el cluster EKS"
  type        = string
  default     = "1.30"
}

variable "cluster_endpoint_public_access" {
  description = "Habilitar acceso publico al endpoint del cluster"
  type        = bool
  default     = true
}

variable "cluster_endpoint_private_access" {
  description = "Habilitar acceso privado al endpoint del cluster"
  type        = bool
  default     = true
}

variable "enable_irsa" {
  description = "Habilitar IAM Roles for Service Accounts"
  type        = bool
  default     = true
}

variable "min_size" {
  description = "Tamaño mínimo del node group"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Tamaño máximo del node group"
  type        = number
  default     = 4
}

variable "desired_size" {
  description = "Tamaño deseado del node group"
  type        = number
  default     = 2
}

variable "instance_types" {
  description = "Lista de tipos de instancia para el node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "aws_auth_users" {
  description = "Lista de usuarios IAM para acceder al cluster"
  type = list(object({
    userarn  = string
    username = string
    groups   = list(string)
  }))
  default = []
}

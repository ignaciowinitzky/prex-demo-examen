# PREX Demo – Examen Técnico

## Infraestructura + Aplicación (FastAPI + Frontend) con Terraform y Kubernetes

Este repositorio contiene mi solución al examen técnico de PREX. La solución incluye:

- Infraestructura en AWS creada con Terraform (VPC, EKS y dependencias).
- Aplicación Backend (FastAPI) y Frontend (Nginx).
- Despliegue en Kubernetes con Deployments, Services, HPA e Ingress.

---

## REQUISITOS

1. Contar con una cuenta de AWS con permisos AdministratorAccess.
2. Utilizar un IDE como Visual Studio Code, Cursor u otro similar.
3. Tener instalado Terraform (versión recomendada >= 1.3).
4. Tener configurado AWS CLI con un usuario válido.

---

## INFRAESTRUCTURA (TERRAFORM)

Toda la infraestructura se encuentra dentro de la carpeta "iac".

Incluye:

- VPC con subnets públicas y privadas.
- NAT Gateway para salida a internet.
- Cluster EKS en subnets privadas.
- Roles de IAM, IRSA y Load Balancer Controller.
- Configuración de acceso al cluster mediante aws-auth.

---

1. Configurar usuarios de acceso (aws_auth_users)

---

Editar el archivo:

iac/terraform.tfvars

Y agregar:

```hcl
aws_auth_users = [
  {
    userarn  = "arn:aws:iam::<account-id>:user/<tu-usuario>"
    username = "admin"
    groups   = ["system:masters"]
  }
]
```

---

2. Inicializar y aplicar Terraform

---

cd iac/
terraform init
terraform plan
terraform apply

Esto creará toda la infraestructura en AWS.

---

3. Conectarse al cluster

---

Ejecutar:

aws eks update-kubeconfig --name <cluster-name>

Listo, ya puedes ejecutar comandos kubectl.

---

## KUBERNETES (DEPLOY DE APPS)

Aquí se despliega:

- Backend (FastAPI)
- Frontend (Nginx)

Cada uno incluye:

- Deployment
- Service
- HorizontalPodAutoscaler (HPA)

---

1. Estructura del proyecto

---

kubernetes/
backend/
deployment.yaml
service.yaml
hpa.yaml
frontend/
deployment.yaml
service.yaml
hpa.yaml
namespace.yaml
ingress.yaml

---

2. Construcción y push de imágenes a ECR

---

docker build -t <your-ecr>/backend:1.0 ./backend
docker push <your-ecr>/backend:1.0

docker build -t <your-ecr>/frontend:1.0 ./frontend
docker push <your-ecr>/frontend:1.0

Luego actualizar las imágenes en los manifiestos de Kubernetes.

---

3. Crear namespace

---

kubectl apply -f kubernetes/namespace.yaml

---

4. Desplegar Backend

---

cd kubernetes/backend/
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

---

5. Desplegar Frontend

---

cd kubernetes/frontend/
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

---

## INGRESS Y ACCESO A LA APLICACION

Aplicar el ingress:

kubectl apply -f kubernetes/ingress.yaml

Obtener la URL pública:

kubectl get ingress -n prex-demo

El frontend responde en la URL principal.
El backend está disponible en /api/message.

---

## ESTRUCTURA GENERAL DEL PROYECTO

prex-demo-examen/
README.md
iac/
main.tf
variables.tf
terraform.tfvars
policies/
aws-load-balancer-controller.json
kubernetes/
backend/
frontend/
namespace.yaml
ingress.yaml

---

## RESULTADO FINAL

La solución contiene:

- Infraestructura como código con Terraform.
- Cluster EKS totalmente funcional en subnets privadas.
- Backend y Frontend desplegados en Kubernetes.
- Autoscaling por HPA.
- Ingress con AWS Load Balancer Controller.

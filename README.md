# PREX Demo – Examen Técnico

<div align="center">
  <img src="https://media.licdn.com/dms/image/v2/C4E16AQG_Cer9jZ5EqQ/profile-displaybackgroundimage-shrink_200_800/profile-displaybackgroundimage-shrink_200_800/0/1624549486857?e=2147483647&v=beta&t=LGl7g3mg2rteghcTrPmrRzm8Rc7l8bcSh43PV-fzm4I" alt="PREX Logo" width="600">
</div>

Este repositorio contiene mi solución al examen de PREX. La solución incluye:

- Infraestructura en AWS creada con Terraform (VPC, EKS y dependencias)
- Aplicación Backend (FastAPI) y Frontend (HTML)
- Despliegue en Kubernetes con Deployments, Services, HPA e Ingress

---

## Requisitos

Antes de comenzar, asegúrate de tener:

1. Una cuenta de AWS con permisos `AdministratorAccess`
2. Un IDE como Visual Studio Code, Cursor u otro similar
3. Terraform instalado (versión recomendada >= 1.5)
4. AWS CLI configurado con un usuario válido

---

## Infraestructura (Terraform)

Toda la infraestructura se encuentra dentro de la carpeta `iac/`.

### Componentes incluidos:

- VPC con subnets públicas y privadas
- NAT Gateway para salida a internet
- Cluster EKS en subnets privadas
- Roles de IAM, IRSA y Load Balancer Controller
- Configuración de acceso al cluster mediante aws-auth

### 1. Configurar usuarios de acceso (aws_auth_users)

Edita el archivo `iac/terraform.tfvars` y agrega:

```hcl
aws_auth_users = [
  {
    userarn  = "arn:aws:iam::<account-id>:user/<tu-usuario>"
    username = "admin"
    groups   = ["system:masters"]
  }
]
```

### 2. Inicializar y aplicar Terraform

```bash
cd iac/
terraform init
terraform plan
terraform apply
```

> **Nota:** Esto creará toda la infraestructura en AWS. El proceso puede tardar varios minutos.

### 3. Conectarse al cluster

Una vez que la infraestructura esté lista, ejecuta:

```bash
aws eks update-kubeconfig --name <cluster-name>
```

> Listo, ya puedes ejecutar comandos `kubectl`.

---

## Kubernetes (Deploy de Apps)

Aquí se despliega:

- **Backend** (FastAPI)
- **Frontend** (HTML)

Cada uno incluye:

- Deployment
- Service
- HorizontalPodAutoscaler (HPA)

### 1. Estructura del proyecto

```
kubernetes/
├── backend/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── frontend/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── namespace.yaml
└── ingress.yaml
```

### 2. Construcción y push de imágenes a ECR

```bash
# Backend
docker build -t <your-ecr>/backend:1.0 ./apps/backend
docker push <your-ecr>/backend:1.0

# Frontend
docker build -t <your-ecr>/frontend:1.0 ./apps/frontend
docker push <your-ecr>/frontend:1.0
```

> **Importante:** Luego actualiza las imágenes en los manifiestos de Kubernetes.

**Antes de desplegar, actualiza las imágenes en los archivos de deployment:**

- En `kubernetes/backend/deployment.yaml`, reemplaza `<IMAGEN EN ECR BUILDEADA BACKEND>` por la imagen que acabas de construir y pushear a ECR (ej: `123456789012.dkr.ecr.us-east-1.amazonaws.com/backend:1.0`)
- En `kubernetes/frontend/deployment.yaml`, reemplaza `<IMAGEN EN ECR BUILDEADA FRONTEND>` por la imagen que acabas de construir y pushear a ECR (ej: `123456789012.dkr.ecr.us-east-1.amazonaws.com/frontend:1.0`)

### 3. Crear namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

### 4. Desplegar Backend

```bash
cd kubernetes/backend/
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

### 5. Desplegar Frontend

```bash
cd kubernetes/frontend/
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

---

## Ingress y Acceso a la Aplicación

### Crear certificado ACM en AWS

Antes de aplicar el Ingress, necesitas crear un certificado SSL/TLS en AWS Certificate Manager (ACM):

1. Ve a la consola de AWS Certificate Manager
2. Solicita un certificado público para tu dominio
3. Valida el certificado (por DNS o email)
4. Copia el ARN del certificado (ej: `arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012`)

**Importante:** El certificado debe estar en la misma región donde está tu cluster EKS.

### Configurar el Ingress

Edita el archivo `kubernetes/ingress.yaml` y reemplaza `<Certificado ACM en AWS>` por el ARN del certificado que acabas de crear:

```yaml
alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012
```

### Aplicar el Ingress

```bash
kubectl apply -f kubernetes/ingress.yaml
```

### Obtener la URL pública

```bash
kubectl get ingress -n prex-demo
```

### Endpoints disponibles

- **Frontend:** URL principal (raíz `/`)
- **Backend:** `/api/message`

---

## Estructura General del Proyecto

```
prex-demo-examen/
├── README.md
├── iac/
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfvars
├── policies/
│   └── aws-load-balancer-controller.json
├── kubernetes/
│   ├── backend/
│   ├── frontend/
│   ├── namespace.yaml
│   └── ingress.yaml
└── apps/
    ├── backend/
    └── frontend/
```

---

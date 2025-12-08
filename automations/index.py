import sys
import time
from pathlib import Path
from src.terraform.terraform import terraform_deploy
from src.kubernetes.kubernetes import update_deployment_image
from src.kubernetes.kubernetes import update_ingress_certificate
from src.kubernetes.kubernetes import kubectl_apply_all
from src.ecr.ecr import ecr_login
from src.ecr.ecr import ensure_ecr_repo
from src.ecr.ecr import build_and_push_image
from src.acm.acm import create_acm_certificate
from src.addons.addons import addons
from src.utils.utils import run_cmd
from src.utils.utils import ensure_region
from src.utils.utils import print_requisitos

REPO_ROOT = Path(__file__).resolve().parents[1]
backend_dir = REPO_ROOT / "apps" / "backend"
frontend_dir = REPO_ROOT / "apps" / "frontend"
backend_deploy_yaml = REPO_ROOT / "kubernetes" / "backend" / "deployment.yaml"   

def main():
    print_requisitos()
    account_id = input("Ingresa el ID de la cuenta de AWS: ").strip()
    if not account_id.isdigit():
        print("El ID de cuenta de AWS debe ser numérico (ej: 123456789012).")
        sys.exit(1)
    domain = input("Ingresa el dominio para el certificado ACM: ").strip()
    if not domain:
        print("Debes especificar un dominio válido.")
        sys.exit(1)
    region = ensure_region()

    print(f"\n Iniciando creación de infra en Terraform")
    terraform_deploy()

    print(f"\n Iniciando buildeo y pusheo de apps")
    ecr_login(account_id, region)
    ensure_ecr_repo("backend", region)
    ensure_ecr_repo("frontend", region)
    backend_local_tag = "backend:1.0"
    frontend_local_tag = "frontend:1.0"
    backend_ecr = f"{account_id}.dkr.ecr.{region}.amazonaws.com/backend:1.0"
    frontend_ecr = f"{account_id}.dkr.ecr.{region}.amazonaws.com/frontend:1.0"
    backend_dir = REPO_ROOT / "apps" / "backend"
    frontend_dir = REPO_ROOT / "apps" / "frontend"
    build_and_push_image(backend_dir, backend_local_tag, backend_ecr)
    build_and_push_image(frontend_dir, frontend_local_tag, frontend_ecr)

    print(f"\n Conectando computadora al cluster")
    run_cmd(["aws", "eks", "update-kubeconfig", "--name", "demo", "--alias", "prex-demo"])
    
    print(f"\n Instalando addons")
    vpc_id = input("Ingresa el ID de la VPC de AWS: ").strip()
    addons(account_id, region, vpc_id)
    time.sleep(60)   
 
    print(f"\n Update de imagenes de ECR a los YAMLs kubernetes")
    backend_deploy_yaml = REPO_ROOT / "kubernetes" / "backend" / "deployment.yaml"
    frontend_deploy_yaml = REPO_ROOT / "kubernetes" / "frontend" / "deployment.yaml"
    update_deployment_image(backend_deploy_yaml, backend_ecr)
    update_deployment_image(frontend_deploy_yaml, frontend_ecr)

    print(f"\n Aplicando YAMLs de kubernetes")
    kubectl_apply_all()

    print(f"\n Aplicando YAMLs de ingress publico")
    ingress_yaml = REPO_ROOT / "kubernetes" / "kubernetes" / "ingress.yaml"
    if not ingress_yaml.is_file():
        ingress_yaml = REPO_ROOT / "kubernetes" / "ingress.yaml"
    cert_arn = create_acm_certificate(domain, region)
    update_ingress_certificate(ingress_yaml, cert_arn)

    print("\n ======= Proceso completado =======")

if __name__ == "__main__":
    main()


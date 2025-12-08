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


def main():
    REPO_ROOT = Path(__file__).resolve().parents[1]
    backend_dir = REPO_ROOT / "apps" / "backend"
    frontend_dir = REPO_ROOT / "apps" / "frontend"
    backend_deploy_yaml = REPO_ROOT / "kubernetes" / "backend" / "deployment.yaml"   

    print_requisitos()
    account_id = input("Ingresa el ID de la cuenta de AWS (ej. 12345678): ").strip()
    domain = input("Ingresa el dominio para el certificado ACM (ej. test.com): ").strip()
    region = ensure_region()

    print(f"\Iniciando creación de infra en Terraform")
    terraform_deploy()

    print(f"\Iniciando buildeo y pusheo de apps")
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

    print(f"\Conectando computadora al cluster")
    run_cmd(["aws", "eks", "update-kubeconfig", "--name", "demo"])

    
    print(f"\Instalando addOns")
    vpc_id = input("Ingresa el ID de la VPC de AWS: ").strip()
    addons(account_id, region, vpc_id)

    print(f"\Update de imagenes de ECR a los YAMLs kubernetes")
    backend_deploy_yaml = REPO_ROOT / "kubernetes" / "backend" / "deployment.yaml"
    frontend_deploy_yaml = REPO_ROOT / "kubernetes" / "frontend" / "deployment.yaml"
    update_deployment_image(backend_deploy_yaml, backend_ecr)
    update_deployment_image(frontend_deploy_yaml, frontend_ecr)

    print(f"\Aplicando YAMLs de kubernetes")
    kubectl_apply_all()

    print(f"\Aplicando YAMLs de ingress publico")
    ingress_yaml = REPO_ROOT / "kubernetes" / "kubernetes" / "ingress.yaml"
    if not ingress_yaml.is_file():
        ingress_yaml = REPO_ROOT / "kubernetes" / "ingress.yaml"
    cert_arn = create_acm_certificate(domain, region)
    update_ingress_certificate(ingress_yaml, cert_arn)

    print("\n======= Proceso completado =======")

if __name__ == "__main__":
    main()

import sys
from pathlib import Path
from src.utils.utils import run_cmd

REPO_ROOT = Path(__file__).resolve().parents[3]

def update_deployment_image(deployment_path, image_uri):
    if not deployment_path.is_file():
        print(f"No se encontró el archivo {deployment_path}")
        sys.exit(1)
    yq_cmd = (
        f'yq e -i \'.spec.template.spec.containers[0].image = "{image_uri}"\' '
        f'"{deployment_path}"'
    )
    run_cmd(yq_cmd)

def update_ingress_certificate(ingress_path, cert_arn):
    if not ingress_path.is_file():
        print(f"No se encontró el archivo {ingress_path}")
        sys.exit(1)

    yq_cmd = (
        'yq e -i '
        f'".metadata.annotations.\\"alb.ingress.kubernetes.io/certificate-arn\\" = \\"{cert_arn}\\"" '
        f'"{ingress_path}"'
    )
    run_cmd(yq_cmd)

def kubectl_apply_all():
    manifests = [
        ["kubectl", "apply", "-f", "kubernetes/namespace.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/frontend/deployment.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/frontend/service.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/frontend/hpa.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/backend/deployment.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/backend/service.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/backend/hpa.yaml"],
        ["kubectl", "apply", "-f", "kubernetes/ingress.yaml"],
    ]

    for cmd in manifests:
        run_cmd(cmd, cwd=REPO_ROOT)

    print("Todos los manifests de Kubernetes fueron aplicados.")


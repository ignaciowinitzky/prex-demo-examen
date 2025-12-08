import sys
import json
import tempfile
from pathlib import Path
from src.utils.utils import run_cmd


def addons(account_id, region, vpc_id):
    policy_name = "AWSLoadBalancerControllerIAMPolicy"
    role_name = "demo-aws-lb-controller"
    policy_file = Path(__file__).resolve().parent / "aws-load-balancer-controller.json"

    print("\nInstalación de AWS Load Balancer Controller")

    # -------------------------------------------------------------------------
    # 1) Verificar / crear IAM Policy desde tu JSON
    # -------------------------------------------------------------------------
    if not policy_file.is_file():
        print(f"No se encontró el archivo de policy: {policy_file}")
        sys.exit(1)

    out = run_cmd(
        [
            "aws", "iam", "list-policies",
            "--scope", "Local",
            "--query", f"Policies[?PolicyName==`{policy_name}`].Arn",
            "--output", "text",
        ],
        capture_output=True,
    )

    policy_arn = out.strip() if out else ""
    if not policy_arn:
        print(f"Policy '{policy_name}' no existe. Creándola desde {policy_file}...")
        out = run_cmd(
            [
                "aws",
                "iam",
                "create-policy",
                "--policy-name",
                policy_name,
                "--policy-document",
                f"file://{policy_file}",
                "--output",
                "json",
            ],
            capture_output=True,
        )
        data = json.loads(out)
        policy_arn = data["Policy"]["Arn"]
        print(f"Policy creada: {policy_arn}")
    else:
        print(f"Policy ya existe: {policy_arn}")

    # -------------------------------------------------------------------------
    # 2) Verificar / actualizar IAM Role con trust policy IRSA
    # -------------------------------------------------------------------------
    role_exists = True
    try:
        run_cmd(
            ["aws", "iam", "get-role", "--role-name", role_name],
            capture_output=True,
        )
        print(f"Rol IAM encontrado: {role_name}")
    except SystemExit:
        role_exists = False
        print(f"'{role_name}' no existe. Lo creamos")

    oidc_issuer = run_cmd(
        [
            "aws",
            "eks",
            "describe-cluster",
            "--name",
            "demo",
            "--region",
            region,
            "--query",
            "cluster.identity.oidc.issuer",
            "--output",
            "text",
        ],
        capture_output=True,
    ).strip()

    if oidc_issuer.startswith("https://"):
        oidc_issuer = oidc_issuer[len("https://") :]

    oidc_provider_arn = f"arn:aws:iam::{account_id}:oidc-provider/{oidc_issuer}"

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Federated": oidc_provider_arn},
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        f"{oidc_issuer}:aud": "sts.amazonaws.com",
                        f"{oidc_issuer}:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller",
                    }
                },
            }
        ],
    }

    # Guardamos trust policy en un archivo temporal
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        json.dump(trust_policy, f)
        trust_path = f.name

    if not role_exists:
        run_cmd(
            [
                "aws",
                "iam",
                "create-role",
                "--role-name",
                role_name,
                "--assume-role-policy-document",
                f"file://{trust_path}",
            ]
        )
        print(f"Rol IAM creado: {role_name}")
    else:
        run_cmd(
            [
                "aws",
                "iam",
                "update-assume-role-policy",
                "--role-name",
                role_name,
                "--policy-document",
                f"file://{trust_path}",
            ]
        )
        print(f"Trust policy del rol '{role_name}' actualizada.")

    try:
        run_cmd(
            [
                "aws",
                "iam",
                "attach-role-policy",
                "--role-name",
                role_name,
                "--policy-arn",
                policy_arn,
            ]
        )
        print("Policy adjuntada al rol.")
    except SystemExit:
        print("No se pudo adjuntar la policy (posiblemente ya esté adjunta). Continuando...")

    sa_cmd = (
        "kubectl get sa aws-load-balancer-controller -n kube-system || "
        "kubectl create serviceaccount aws-load-balancer-controller -n kube-system"
    )
    run_cmd(sa_cmd)
    annotate_cmd = (
        "kubectl annotate serviceaccount aws-load-balancer-controller "
        "-n kube-system "
        f"eks.amazonaws.com/role-arn=$(aws iam get-role --role-name {role_name} "
        "--query 'Role.Arn' --output text) "
        "--overwrite"
    )
    run_cmd(annotate_cmd)
    run_cmd(["helm", "repo", "add", "eks", "https://aws.github.io/eks-charts"])
    run_cmd(["helm", "repo", "update"])
    run_cmd(
        [
            "helm",
            "upgrade",
            "--install",
            "aws-load-balancer-controller",
            "eks/aws-load-balancer-controller",
            "-n",
            "kube-system",
            "--set",
            "clusterName=demo",
            "--set",
            "serviceAccount.create=false",
            "--set",
            "serviceAccount.name=aws-load-balancer-controller",
            "--set",
            f"region={region}",
            "--set",
            f"vpcId={vpc_id}",
        ]
    )
    run_cmd(
        [
            "kubectl",
            "rollout",
            "restart",
            "deployment/aws-load-balancer-controller",
            "-n",
            "kube-system",
        ]
    )
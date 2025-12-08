import sys
import json
from pathlib import Path
from src.utils.utils import run_cmd

REPO_ROOT = Path(__file__).resolve().parents[3]

def create_acm_certificate(domain, region):
    print("\n Creando certificado ACM ")
    cmd = [
        "aws",
        "acm",
        "request-certificate",
        "--domain-name",
        domain,
        "--validation-method",
        "DNS",
        "--region",
        region,
        "--output",
        "json",
    ]
    output = run_cmd(cmd, capture_output=True)
    try:
        data = json.loads(output)
        cert_arn = data["CertificateArn"]
    except Exception as e:
        print("Error:")
        print(e)
        sys.exit(1)

    return cert_arn


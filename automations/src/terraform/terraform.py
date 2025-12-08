import sys
from pathlib import Path
from src.utils.utils import run_cmd

REPO_ROOT = Path(__file__).resolve().parents[3]

def terraform_deploy():
    iac_dir = REPO_ROOT / "iac"
    if not iac_dir.is_dir():
        print(f"No se encontró la carpeta {iac_dir}")
        sys.exit(1)

    run_cmd(["terraform", "init"], cwd=iac_dir)
    run_cmd(["terraform", "plan"], cwd=iac_dir)
    run_cmd(["terraform", "apply", "-auto-approve"], cwd=iac_dir)
    print("Terraform apply completado.")
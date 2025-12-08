import sys
from src.utils.utils import run_cmd

def ecr_login(account_id, region):
    login_cmd = (
        f"aws ecr get-login-password --region {region} | "
        f"docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
    )
    run_cmd(login_cmd)


def ensure_ecr_repo(repo_name, region):
    describe_cmd = [
        "aws",
        "ecr",
        "describe-repositories",
        "--repository-names",
        repo_name,
        "--region",
        region,
    ]
    try:
        run_cmd(describe_cmd, capture_output=True)
    except SystemExit:
        create_cmd = [
            "aws",
            "ecr",
            "create-repository",
            "--repository-name",
            repo_name,
            "--region",
            region,
        ]
        run_cmd(create_cmd)

def build_and_push_image(app_dir, local_tag, ecr_tag):
    if not app_dir.is_dir():
        print(f"No existe la carpeta {app_dir}")
        sys.exit(1)
    run_cmd(["docker", "build", "--platform", "linux/amd64" ,"-t", local_tag, "."], cwd=app_dir)
    run_cmd(["docker", "tag", local_tag, ecr_tag])
    run_cmd(["docker", "push", ecr_tag])
    return ecr_tag
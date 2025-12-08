import sys
import subprocess

def print_requisitos():
    print("=======" * 80)
    print("REQUISITOS PARA EJECUTAR ESTE SCRIPT")
    print("=======" * 80)
    print("1) Cuenta de AWS con permisos AdministratorAccess")
    print("2) AWS CLI configurado (aws configure)")
    print("3) Terraform instalado (>= 1.5)")
    print("4) kubectl instalado y en el PATH")
    print("5) Helm instalado y en el PATH")
    print("6) Docker instalado, iniciado y logueado localmente")
    print("7) yq instalado")
    print("=" * 80)

def ensure_region():
    try:
        result = subprocess.run(
            ["aws", "configure", "get", "region"],
            capture_output=True,
            text=True,
            check=True,
        )
        region = result.stdout.strip()
        if region:
            return region
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    region = input("Ingresa la región de AWS: ").strip()
    if not region:
        print("Debes especificar una región válida.")
        sys.exit(1)
    return region

def run_cmd(cmd, cwd=None, capture_output=False):
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                shell=isinstance(cmd, str),
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return result.stdout.strip()
        else:
            subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                shell=isinstance(cmd, str),
                check=True,
            )
            return ""
    except subprocess.CalledProcessError as e:
        print("\nError ejecutando comando:")
        print(e)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(1)
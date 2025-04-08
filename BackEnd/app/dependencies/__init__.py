import subprocess
import sys

# Lista de pacotes necessários com versões específicas
REQUIRED_PACKAGES = [
    "blinker==1.9.0",
    "cffi==1.17.1",
    "click==8.1.8",
    "colorama==0.4.6",
    "cryptography==44.0.2",
    "Flask==3.1.0",
    "Flask-SQLAlchemy==3.1.1",
    "greenlet==3.1.1",
    "itsdangerous==2.2.0",
    "Jinja2==3.1.6",
    "MarkupSafe==3.0.2",
    "psycopg2-binary==2.9.10",
    "pycparser==2.22",
    "PyMySQL==1.1.1",
    "SQLAlchemy==2.0.40",
    "typing_extensions==4.13.1",
    "Werkzeug==3.1.3",
    "flask-swagger-ui",
    "flask",
    "re"
]

def install_missing_packages():
    """Verifica e instala pacotes necessários automaticamente."""
    for package in REQUIRED_PACKAGES:
        try:
            package_name = package.split("==")[0] if "==" in package else package
            if package_name == "re":
                continue  # 're' é do Python, não precisa instalar
            __import__(package_name)
        except ImportError:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Instala os pacotes ao rodar o script
if __name__ == "__main__":
    install_missing_packages()

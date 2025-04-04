from flask import Flask
from app.controllers.usuarioContrroller import usuario_bp
from config.database import init_db
from app.dependencies import install_missing_packages

# Instala pacotes necessários
install_missing_packages()

app = Flask(__name__)

# Inicializar banco de dados
init_db(app)

# Registrar os controllers
app.register_blueprint(usuario_bp)

if __name__ == "__main__":
    app.run(debug=True)

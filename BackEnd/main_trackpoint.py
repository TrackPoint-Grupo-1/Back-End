import os
from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import secrets
import config
from app.controllers.atestadoController import atestado_bp
from app.controllers.usuarioContrroller import usuario_bp
from app.dependencies import install_missing_packages
from config.database import init_db

print("secrets.token_hex(32)" + secrets.token_hex(32))
# Instala pacotes necessários
install_missing_packages()
app = Flask(__name__)
#app.config.from_object(config.config_email)
app.config['JSON_AS_ASCII'] = False
SWAGGER_URL = "/docs"
API_URL = "/swagger.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # URL da interface Swagger
    API_URL,      # Caminho para seu arquivo swagger.yaml
    config={"app_name": "TrackPoint API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.yaml")
def send_swagger():
    return send_from_directory(os.path.join("swagger"), "swagger_config.yaml")

# Inicializar banco de dados
init_db(app)

# Registrar os controllers
app.register_blueprint(usuario_bp)
app.register_blueprint(atestado_bp)

if __name__ == "__main__":
    app.run(debug=True)

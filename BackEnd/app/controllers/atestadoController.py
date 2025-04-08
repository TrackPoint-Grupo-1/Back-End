from flask import Blueprint, request, jsonify

from app.services.atestadoService import criar_atestado_service, listar_todos_atestados, mudar_status_atestado_por_id

atestado_bp = Blueprint("atestado_bp", __name__)

@atestado_bp.route("/atestados/criar", methods=["POST"])
def criar_atestado_controller():
    dados = request.json
    return criar_atestado_service(dados)


@atestado_bp.route("/atestados", methods=["GET"])
def listar_atestados():
    atestados = listar_todos_atestados()
    return jsonify(atestados), 200

@atestado_bp.route("/atestados/<int:id_atestado>/status", methods=["PATCH"])
def alterar_status(id_atestado):
    dados = request.json
    novo_status = dados.get("status")

    if not novo_status:
        return jsonify({"error": "Campo 'status' é obrigatório"}), 400

    atestado, erro = mudar_status_atestado_por_id(id_atestado, novo_status)

    if erro:
        return jsonify({"error": erro}), 404

    return jsonify({"message": f"Status foi atualizado para '{novo_status}'"}), 200

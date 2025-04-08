from flask import Blueprint, request, jsonify

from app.models.atestado import Atestado
from app.services.atestadoService import criar_atestado_service, listar_todos_atestados, mudar_status_atestado_por_id
from app.utils.email_utils import enviar_email
from config.database import db

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

@atestado_bp.route('/atestados/paginado', methods=['GET'])
def listar_atestados_paginado():
    status = request.args.get('status')  # pendente, aprovado, rejeitado
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    query = Atestado.query

    if status:
        query = query.filter_by(status=status.capitalize())  # ou upper() se vc usar em CAPS

    total = query.count()
    atestados = query.offset(offset).limit(limit).all()

    resultado = []
    for atestado in atestados:
        resultado.append({
            "id": atestado.id,
            "email": atestado.usuario.email,
            "cid": atestado.cid,
            "texto_capturado": atestado.texto_capturado,
            "status": atestado.status,
            "data_envio": atestado.data_envio.strftime('%d/%m/%Y %H:%M'),
        })

    return jsonify({
        "total": total,
        "page": page,
        "limit": limit,
        "results": resultado
    })


@atestado_bp.route('/atestados/<int:id>/aprovar', methods=['PATCH'])
def aprovar_atestado(id):
    atestado = Atestado.query.get_or_404(id)

    if not request.is_json:
        return jsonify({"error": "Requisição precisa estar em JSON."}), 400

    usuario_logado_email = request.json.get("email_usuario_logado")
    if not usuario_logado_email:
        return jsonify({"error": "Email do usuário logado é obrigatório."}), 400

    if atestado.usuario.email == usuario_logado_email:
        return jsonify({"error": "Você não pode rejeitar seu próprio atestado."}), 403

    atestado.status = "Aprovado"
    db.session.commit()

    # Enviar e-mail
    assunto = "📄 Atestado Aprovado"
    mensagem = f"Olá, {atestado.usuario.nome},\n\nSeu atestado foi aprovado com sucesso! ✅"
    enviar_email(atestado.usuario.email, assunto, mensagem)

    return jsonify({"message": "Atestado aprovado com sucesso."}), 200


@atestado_bp.route('/atestados/<int:id>/rejeitar', methods=['PATCH'])
def rejeitar_atestado(id):
    atestado = Atestado.query.get_or_404(id)

    if not request.is_json:
        return jsonify({"error": "Requisição precisa estar em JSON."}), 400

    usuario_logado_email = request.json.get("email_usuario_logado")
    if not usuario_logado_email:
        return jsonify({"error": "Email do usuário logado é obrigatório."}), 400

    if atestado.usuario.email == usuario_logado_email:
        return jsonify({"error": "Você não pode rejeitar seu próprio atestado."}), 403

    atestado.status = "Rejeitado"
    db.session.commit()

    # Enviar e-mail
    assunto = "📄 Atestado Rejeitado"
    mensagem = f"Olá, {atestado.usuario.nome},\n\nSeu atestado foi rejeitado. ❌\nSe houver dúvidas, entre em contato com o RH."
    enviar_email(atestado.usuario.email, assunto, mensagem)

    return jsonify({"message": "Atestado rejeitado com sucesso."}), 200

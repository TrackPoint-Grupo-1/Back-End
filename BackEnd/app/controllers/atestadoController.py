from datetime import datetime

from flask import Blueprint, request, jsonify

from app.models.atestado import Atestado
from app.services.atestadoService import criar_atestado_service, listar_todos_atestados, mudar_status_atestado_por_id
from app.utils.email_utils import enviar_email
from config.database import db

from BackEnd.app.utils.PipefyConnector import criar_card_pipefy, mover_card_para_aprovado, buscar_card_por_id_atestado, \
    mover_card_para_reprovado

atestado_bp = Blueprint("atestado_bp", __name__)


@atestado_bp.route("/atestados/criar", methods=["POST"])
def criar_atestado_controller():
    dados = request.json

    nome = f"Novo Atestado - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    email = dados.get("email_usuario") or dados.get("email")
    descricao = dados.get("texto_capturado") or dados.get("descricao")

    # Cria o atestado no sistema
    response = criar_atestado_service(dados)
    if response[1] != 201:
        return response  # Retorna erro se falhar na criação do atestado

    id = response[0].get_json().get("id")

    try:
        card = criar_card_pipefy(nome=nome, email=email, descricao=descricao, id=id)
        print(f"✅ Card criado no Pipefy: ID {card.get('id')}, Título {nome}")
    except Exception as e:
        print(f"❌ Erro ao criar card no Pipefy: {e}")

    return response  # Retorna a resposta da criação do atestado


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

    # Atualiza o status no banco
    atestado.status = "Aprovado"
    db.session.commit()

    # Envia email de confirmação
    assunto = "📄 Atestado Aprovado"
    mensagem = f"Olá, {atestado.usuario.nome},\n\nSeu atestado foi aprovado com sucesso! ✅"
    enviar_email(atestado.usuario.email, assunto, mensagem)

    # ✅ Mover no Pipefy - corrige aqui
    card = buscar_card_por_id_atestado(atestado.id)
    if card:
        mover_card_para_aprovado(card["id"])
    else:
        print(f"Card Pipefy para atestado {atestado.id} não encontrado.")

    return jsonify({"message": "Atestado aprovado com sucesso."}), 200



@atestado_bp.route('/atestados/<int:id>/rejeitar', methods=['PATCH'])
def rejeitar_atestado(id):
    atestado = Atestado.query.get_or_404(id)

    if not request.is_json:
        return jsonify({"error": "Requisição precisa estar em JSON."}), 400

    # Atualiza o status no banco
    atestado.status = "Rejeitado"
    db.session.commit()

    # Envia email de confirmação
    assunto = "📄 Atestado Rejeitado"
    mensagem = f"Olá, {atestado.usuario.nome},\n\nSeu atestado foi rejeitado. ❌\nSe houver dúvidas, entre em contato com o RH."
    enviar_email(atestado.usuario.email, assunto, mensagem)

    # ❌ Mover no Pipefy - corrige aqui
    card = buscar_card_por_id_atestado(atestado.id)
    if card:
        mover_card_para_reprovado(card["id"])
    else:
        print(f"Card Pipefy para atestado {atestado.id} não encontrado.")

    return jsonify({"message": "Atestado rejeitado com sucesso."}), 200

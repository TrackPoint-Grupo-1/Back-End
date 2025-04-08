from flask import jsonify
from app.models.usuario import Usuario
from app.models.atestado import Atestado
from app.repositories.atestadoRepository import buscar_atestados_por_usuario

from config.database import db


from flask import jsonify
from app.utils.email_utils import enviar_email  # Certifique-se de importar corretamente
from config.config_email import config_email

def criar_atestado_service(dados):
    email = dados.get("email")
    if not email:
        return jsonify({"error": "Email não fornecido"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    if usuario.ativo != "Ativo":
        return jsonify({"error": "Usuário inativo"}), 403

    if not usuario.logado:
        return jsonify({"error": "Usuário não está logado"}), 401

    novo_atestado = Atestado(
        cid=dados.get("cid"),
        texto_capturado=dados.get("texto_capturado"),
        usuario=usuario
    )

    db.session.add(novo_atestado)
    db.session.commit()

    # Enviar email após o commit
    try:
        assunto = "📄 Atestado enviado com sucesso"
        corpo = f"""
Olá, {usuario.nome},

Seu atestado foi recebido com sucesso no sistema e está aguardando análise.

📅 Data de envio: {novo_atestado.data_envio.strftime('%d/%m/%Y %H:%M')}
📌 Status: Pendente

Você será notificado assim que for analisado.

Atenciosamente,
Equipe RH
        """
        enviar_email(destinatario=email, assunto=assunto, corpo=corpo)

    except Exception as e:
        print(f"[Erro ao enviar e-mail] {e}")

    return jsonify({"message": "Atestado enviado com sucesso!"}), 201


def listar_todos_atestados():
    atestados = Atestado.query.all()
    return [atestado_to_dict(atestado) for atestado in atestados]

def atestado_to_dict(atestado):
    return {
        "id": atestado.id,
        "cid": atestado.cid,
        "texto_capturado": atestado.texto_capturado,
        "data_envio": atestado.data_envio.strftime('%d/%m/%Y %H:%M:%S'),
        "usuario": {
            "nome": atestado.usuario.nome,
            "email": atestado.usuario.email
        },
        "status": atestado.status
    }

def mudar_status_atestado_por_id(id_atestado, novo_status):
    atestado = Atestado.query.get(id_atestado)

    if not atestado:
        return None, "Atestado não encontrado"

    atestado.status = novo_status

    try:
        db.session.commit()
        return atestado, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

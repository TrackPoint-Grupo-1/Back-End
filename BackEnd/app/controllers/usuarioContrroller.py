from flask import Blueprint, jsonify, request

from app.services.usuarioService import criar_usuario, buscar_usuarios, buscar_usuario_por_email, \
    atualizar_usuario_por_email
from flask import Blueprint, jsonify, request

from app.services.usuarioService import criar_usuario, buscar_usuarios, buscar_usuario_por_email, \
    atualizar_usuario_por_email

usuario_bp = Blueprint('usuario_bp', __name__)

BLACKLIST = set()

@usuario_bp.route("/usuarios", methods=["POST"])
def criar():
    dados = request.json

    # Verifica se todos os campos obrigatórios estão presentes
    if not all(k in dados for k in ["nome", "email", "senha", "cargo"]):
        return jsonify({"error": "Nome, e-mail, senha e cargo são obrigatórios"}), 400

    try:
        # Verifica se já existe um usuário com o e-mail fornecido
        if buscar_usuario_por_email(dados["email"]):  # Corrigido para passar apenas o e-mail
            return jsonify({"error": "E-mail já está em uso"}), 400

        # Criar usuário com os dados fornecidos
        usuario = criar_usuario(dados["nome"], dados["email"], dados["senha"], dados["cargo"])

        return jsonify({
            "message": "Usuário criado!",
            "usuario": {
                "nome": usuario.nome,
                "email": usuario.email,
                "cargo": usuario.cargo.value  # Certificando-se de retornar a string do Enum Cargo
            }
        }), 201  # Código 201 indica criação bem-sucedida

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Retorna erro caso algo dê errado


@usuario_bp.route("/usuarios/ativos", methods=["GET"])
def listar_ativos():
    usuarios = buscar_usuarios()
    usuarios_ativos = [u for u in usuarios if u.ativo == "Ativo"]

    if not usuarios_ativos:
        return jsonify({"message": "Nenhum usuário ativo encontrado."}), 404

    return jsonify([
        {
            "nome": u.nome,
            "email": u.email,
            "cargo": u.cargo.value,
            "ativo": u.ativo,
            "logado": u.logado,
            "data_criacao": u.data_criacao.strftime("%d/%m/%Y %H:%M:%S") if u.data_criacao else None,
            "data_atualizacao": u.data_atualizacao.strftime("%d/%m/%Y %H:%M:%S") if u.data_atualizacao else None,
            **({"data_ultimo_login": u.data_ultimo_login.strftime("%d/%m/%Y %H:%M:%S")} if u.data_ultimo_login and not u.logado else {})
        }
        for u in usuarios_ativos
    ])

@usuario_bp.route("/usuarios/inativos", methods=["GET"])
def listar_inativos():
    usuarios = buscar_usuarios()
    usuarios_inativos = [u for u in usuarios if u.ativo == "Inativo"]

    if not usuarios_inativos:
        return jsonify({"message": "Nenhum usuário inativo encontrado."}), 404

    return jsonify([
        {
            "nome": u.nome,
            "email": u.email,
            "cargo": u.cargo.value,
            "ativo": u.ativo,
            "logado": u.logado,
            "data_criacao": u.data_criacao.strftime("%d/%m/%Y %H:%M:%S") if u.data_criacao else None,
            "data_atualizacao": u.data_atualizacao.strftime("%d/%m/%Y %H:%M:%S") if u.data_atualizacao else None,
            **({"data_ultimo_login": u.data_ultimo_login.strftime("%d/%m/%Y %H:%M:%S")} if u.data_ultimo_login and not u.logado else {})
        }
        for u in usuarios_inativos
    ])

@usuario_bp.route("/usuarios/listar-nome-ou-email", methods=["GET"])
def listar_por_nome_ou_email():
    nome = request.args.get("nome")
    email = request.args.get("email")

    if not nome and not email:
        return jsonify({"error": "Nome ou e-mail devem ser fornecidos"}), 400

    usuarios = buscar_usuarios() or []

    usuarios_filtrados = [
        {
            "nome": u.nome,
            "email": u.email,
            "cargo": u.cargo.value,
            "logado": u.logado,
            "data_criacao": u.data_criacao.strftime("%d/%m/%Y %H:%M:%S") if u.data_criacao else None,
            "data_atualizacao": u.data_atualizacao.strftime("%d/%m/%Y %H:%M:%S") if u.data_atualizacao else None,
            "data_ultimo_login": u.data_ultimo_login.strftime("%d/%m/%Y %H:%M:%S") if not u.logado else None
        }
        for u in usuarios
        if (nome and u.nome and nome.lower() in u.nome.lower()) or (email and u.email and email.lower() in u.email.lower())
    ]

    # Se a lista estiver vazia, retorna um erro 404
    if not usuarios_filtrados:
        return jsonify({"error": "Nenhum usuário encontrado com o nome ou e-mail informado."}), 404

    return jsonify(usuarios_filtrados)


from datetime import datetime
from config.database import db


@usuario_bp.route("/usuarios/login", methods=["POST"])
def login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    usuario = buscar_usuario_por_email(email)
    if not usuario or not usuario.check_senha(senha):
        return jsonify({"error": "E-mail ou senha inválidos"}), 401

    usuario.logado = True
    usuario.data_ultimo_login = datetime.utcnow()

    try:
        db.session.commit()  # Salva as alterações no banco
        return jsonify({"message": "Login realizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()  # Desfaz em caso de erro
        return jsonify({"error": str(e)}), 500


@usuario_bp.route("/usuarios/logout", methods=["POST"])
def logout():
    dados = request.json
    email = dados.get("email")

    usuario = buscar_usuario_por_email(email)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    usuario.logado = False  # Define como deslogado
    db.session.commit()  # Salva as alterações no banco

    return jsonify({"message": "Logout realizado com sucesso"}), 200

@usuario_bp.route("/usuarios/atualizar", methods=["PATCH"])
def atualizar_usuario():
    dados = request.json
    email = dados.get("email")

    if not email:
        return jsonify({"error": "E-mail é obrigatório"}), 400

    dados["data_atualizacao"] = datetime.utcnow()
    response, status = atualizar_usuario_por_email(email, dados)

    if status == 200:
        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    else:
        return jsonify(response), status

@usuario_bp.route("/usuarios/desativar", methods=["PATCH"])
def desativar_usuario_por_email():
    dados = request.json
    email = dados.get("email")

    if not email:
        return jsonify({"error": "E-mail é obrigatório"}), 400

    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    usuario.ativo = "Inativo"
    db.session.commit()

    return jsonify({"message": f"Usuário {usuario.nome} desativado com sucesso!"}), 200




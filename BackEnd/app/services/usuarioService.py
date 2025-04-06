from datetime import datetime

from app.models.cargos import Cargo
from app.repositories.usuarioRepository import salvar_usuario, listar_usuarios
from app.models.usuario import Usuario
from config.database import db
import re

def criar_usuario(nome, email, senha, cargo):
    usuario = Usuario(nome=nome, email=email, cargo=cargo)
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario

def buscar_usuarios():
    return listar_usuarios()

def buscar_usuario_por_email(email):
    return Usuario.query.filter_by(email=email).first()

def buscar_usuario_por_id(id):
    return Usuario.query.filter_by(id=id).first()

@staticmethod
def atualizar_usuario_por_email(email, dados):
    usuario = buscar_usuario_por_email(email)
    if not usuario:
        return {"error": "Usuário não encontrado"}, 404

    if "nome" in dados:
        usuario.nome = dados["nome"]

    # Impede a atualização dos campos 'ativo' e 'logado'
    if "ativo" in dados or "logado" in dados:
        return {"error": "Não é permitido alterar os campos 'ativo' e 'logado'"}, 400

    # db.session.commit()  # Descomente se estiver usando um ORM

    # Retorna os dados atualizados
    usuario_atualizado = {
        "nome": usuario.nome,
        "email": usuario.email,
        "cargo": usuario.cargo.value,
        "logado": usuario.logado,
        "data_criacao": usuario.data_criacao.strftime("%d/%m/%Y %H:%M:%S") if usuario.data_criacao else None,
        "data_atualizacao": usuario.data_atualizacao.strftime("%d/%m/%Y %H:%M:%S") if usuario.data_atualizacao else None,
        "data_ultimo_login": usuario.data_ultimo_login.strftime("%d/%m/%Y %H:%M:%S") if usuario.data_ultimo_login and not usuario.logado else None
    }

    return usuario_atualizado, 200


def validar_e_atualizar_usuario(email, dados):
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return {"error": "Usuário não encontrado"}, 404

    if usuario.ativo == "Inativo":
        return {"error": "Não é possível atualizar informações de usuários inativos"}, 400

    campos_validos = ["nome", "email", "senha", "cargo", "novo_email"]
    for campo in dados:
        if campo not in campos_validos:
            return {"error": f"Campo inválido: {campo}"}, 400

    for campo, valor in dados.items():
        if campo == "email" or campo == "novo_email":
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", valor):
                return {"error": f"E-mail inválido: {valor}"}, 400

        if campo == "senha":
            if len(valor) < 6:
                return {"error": "A senha deve ter no mínimo 6 caracteres"}, 400
            usuario.set_senha(valor)
            continue

        setattr(usuario, campo, valor)

    usuario.data_atualizacao = datetime.utcnow()
    return usuario, 200

def validar_email(email):
    # Regex básica para validar email com @ e domínio
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(padrao, email) is not None

def validar_senha(senha):
    # Verifica se a senha tem pelo menos 6 caracteres
    return len(senha) >= 6

def validar_cargo(cargo):
    try:
        Cargo[cargo]
        return True
    except KeyError:
        return False

def validar_nome(nome):
    padrao = r"^[a-zA-ZÀ-ÿ\s]+$"
    return re.match(padrao, nome) is not None and len(nome) >= 3

def autenticar_usuario(email, senha):
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.check_senha(senha):
        return {"error": "E-mail ou senha inválidos"}, 401

    if usuario.ativo != "Ativo":
        return {"error": "Usuário inativo. Acesso negado."}, 403

    usuario.logado = True
    usuario.data_ultimo_login = datetime.utcnow()

    try:
        db.session.commit()
        return {"message": "Login realizado com sucesso!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


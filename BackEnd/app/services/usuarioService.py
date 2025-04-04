from app.repositories.usuarioRepository import salvar_usuario, listar_usuarios
from app.models.usuario import Usuario
from config.database import db

def criar_usuario(nome, email, senha, cargo):
    usuario = Usuario(nome=nome, email=email, cargo=cargo)
    usuario.set_senha(senha)  # Chama o método para criptografar a senha
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
    if "logado" in dados:
        usuario.logado = dados["logado"]

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
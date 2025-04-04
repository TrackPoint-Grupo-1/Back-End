from app.models.usuario import db, Usuario

def salvar_usuario(usuario):
    db.session.add(usuario)
    db.session.commit()
    return usuario

def listar_usuarios():
    return Usuario.query.all()

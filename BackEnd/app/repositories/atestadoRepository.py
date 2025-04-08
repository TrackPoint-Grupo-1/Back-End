from app.models.atestado import Atestado
from config.database import db

def salvar_atestado(atestado):
    db.session.add(atestado)
    db.session.commit()
    return atestado

def buscar_atestados_por_usuario(id_usuario):
    return Atestado.query.filter_by(id_usuario=id_usuario).all()

def buscar_atestado_por_id(id_atestado):
    return Atestado.query.get(id_atestado)

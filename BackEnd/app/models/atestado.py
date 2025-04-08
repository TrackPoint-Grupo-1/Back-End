from config.database import db

class Atestado(db.Model):
    __tablename__ = "atestados"

    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String(20), nullable=False)
    texto_capturado = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('Pendente', 'Aprovado', 'Rejeitado'), default='Pendente')

    # Relacionamento com o usuário
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship("Usuario", backref=db.backref("atestados", lazy=True))

    data_envio = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Atestado {self.usuario.nome} - {self.cid}>"

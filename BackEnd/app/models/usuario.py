from config.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from .cargos import Cargo

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(500), nullable=False)
    logado = db.Column(db.Boolean, default=False)
    cargo = db.Column(db.Enum(Cargo), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_atualizacao = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    data_ultimo_login = db.Column(db.DateTime, default=db.func.current_timestamp())
    ativo = db.Column(db.Enum('Ativo', 'Inativo'), default='Ativo')

    def set_senha(self, senha):
        if len(senha) < 6:
            raise ValueError("A senha deve ter no mínimo 6 caracteres")
        self.senha = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha, senha)

    def __repr__(self):
        return f"<Usuario {self.nome}>"

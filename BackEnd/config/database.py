from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///TrackPoint.db"  # SQLite local
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Evita warnings
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:urubu100@localhost/TrackPoint"
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Criação automática das tabelas

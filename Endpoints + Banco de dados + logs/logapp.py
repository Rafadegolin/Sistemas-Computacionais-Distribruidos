from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy

servidor = Flask(__name__)
servidor.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///log.db"

contexto = SQLAlchemy()

contexto.init_app(servidor)

class Log(contexto.Model):
    id = contexto.Column(contexto.Integer, autoincrement=True, primary_key=True)
    mensagem = contexto.Column(contexto.String)

@servidor.route("/log", methods=['POST'])
async def gravar_log():
    dados = json.loads(request.data)

    log = Log(
        mensagem = dados['mensagem']
    )

    contexto.session.add(log)
    contexto.session.commit()

    return "OK", 201

with servidor.app_context():
    contexto.create_all()

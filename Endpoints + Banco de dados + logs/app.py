from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import asyncio
import logHelper
#from string import lower
servidor = Flask(__name__)
servidor.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db-orm.db"

orm = SQLAlchemy()

ad = orm.Table('ad',
orm.Column('aluno_id',orm.Integer, orm.ForeignKey('aluno.id'), primary_key = True),
orm.Column('disciplina_id',orm.Integer, orm.ForeignKey('disciplina.id'), primary_key = True)
)

##Criando nossa classe de modelo
##Essa classe é baseada no paradigma POO,
##e o nosso ORM vai mapear essa classe e criar sua representação
##relacional no banco de dados
class Aluno(orm.Model) :
    id = orm.Column(orm.Integer, primary_key = True, autoincrement = True)
    nome = orm.Column(orm.String, nullable = False)
    email = orm.Column(orm.String)
    ra = orm.Column(orm.Integer, nullable = False)
    data_criacao = orm.Column(orm.String)
    data_atualizacao = orm.Column(orm.String)
    endereco = orm.relationship('Endereco', backref='aluno', lazy =True)
    ad = orm.relationship('Disciplina', secondary=ad, lazy='subquery',
                                   backref=orm.backref('alunos', lazy=True))

class Disciplina(orm.Model):
    id = orm.Column(orm.Integer, primary_key = True, autoincrement = True)
    nome = orm.Column(orm.String, nullable = False)
    carga_horaria = orm.Column(orm.Integer, nullable = False)
    data_criacao = orm.Column(orm.String)
    data_atualizacao = orm.Column(orm.String)

class Endereco(orm.Model):
    id = orm.Column(orm.Integer, primary_key = True, autoincrement = True)
    logradouro = orm.Column(orm.String, nullable = False)
    cep = orm.Column(orm.String, nullable = False)
    cidade = orm.Column(orm.String, nullable = False)
    aluno_id = orm.Column(orm.Integer, orm.ForeignKey('aluno.id'))





orm.init_app(servidor)

@servidor.route("/")
def home() :
    return "Servidor executando com Flask SQLAlchemy ORM", 200

@servidor.route("/escola/<string:geral>", methods=['POST'])
async def cadastrar(geral) :
    geral = geral.lower()
    #resgatamos os dados do corpo da req
    dados = request.get_json()
    #criamos nosso objeto Aluno
    #que contém interfaces/metodos com o ORM
    if geral == 'aluno':
        aluno = Aluno (
            nome = dados['nome'],
            email = dados['email'],
            ra = dados['ra'],
            data_criacao = datetime.now(),
            data_atualizacao = ""
        )
        try:
            #insert into aluno ...
            #através da sessão com o banco de dados
            #disponibilizada pelo nosso ORM
            orm.session.add(aluno)
            orm.session.commit()
            orm.session.refresh(aluno)

            response = { "aluno_id": aluno.id }, 201
        except:
            response = { "mensagem": "error"}, 500

        await asyncio.create_task(logHelper.gravarCadastro_log(aluno))

        return response
    elif geral == 'disciplina':
        disciplina = Disciplina (
            nome = dados['nome'],
            carga_horaria = dados['carga_horaria'],
            data_criacao = datetime.now(),
            data_atualizacao = ""
        )
        try:
            #insert into aluno ...
            #através da sessão com o banco de dados
            #disponibilizada pelo nosso ORM
            orm.session.add(disciplina)
            orm.session.commit()
            orm.session.refresh(disciplina)

            response = { "disciplina_id": disciplina.id }, 201
        except:
            response = { "mensagem": "error"}, 500

        await asyncio.create_task(logHelper.gravarCadastro_log(disciplina))

        return response
    elif geral == 'endereco':
        endereco = Endereco (
            logradouro = dados['logradouro'],
            cep = dados['cep'],
            cidade = dados['cidade'],
            aluno_id = dados['aluno_id']
        )
        try:
            #insert into aluno ...
            #através da sessão com o banco de dados
            #disponibilizada pelo nosso ORM
            orm.session.add(endereco)
            orm.session.commit()
            orm.session.refresh(endereco)

            response = { "endereco_id": endereco.id }, 201
        except:
            response = { "mensagem": "error"}, 500

        await asyncio.create_task(logHelper.gravarCadastro_log(endereco))

        return response

@servidor.route("/escola/<string:geral>/<int:id>")
async def consultar(geral,id):
    geral = geral.lower()
    if geral == 'aluno':
        aluno = Aluno.query.get(id)

        response = {
            "id" : aluno.id,
            "nome" : aluno.nome,
            "email" : aluno.email,
            "ra" : aluno.ra,
            "data_criacao": aluno.data_criacao,
            "data_atualizacao" : aluno.data_atualizacao,
        }, 200

        return response
    elif geral == 'disciplina':
        disciplina = Disciplina.query.get(id)

        response = {
            "id" : disciplina.id,
            "nome" : disciplina.nome,
            "carga_horaria" : disciplina.carga_horaria,
            "data_criacao": disciplina.data_criacao,
            "data_atualizacao" : disciplina.data_atualizacao,
        }, 200

        return response
    elif geral == 'endereco':
        endereco = Endereco.query.get(id)

        response = {
            "id" : endereco.id,
            "logradouro" : endereco.logradouro,
            "cep" : endereco.cep,
            "cidade" : endereco.cidade,
            "aluno_id": endereco.aluno_id,
        }, 200

        return response

@servidor.route("/escola/<string:geral>", methods=['PUT'])
def atualizar(geral) :
    dados = request.get_json()
    geral = geral.lower()

    if geral == 'aluno':
        try:
            aluno = Aluno.query.get(dados['id']) #resgatamos os dados do aluno
                                                #da base de dados
            if aluno:
                #atualizamos as props
                aluno.nome = dados['nome']
                aluno.email = dados['email']
                aluno.ra = dados['ra']
                aluno.data_atualizacao = datetime.now()

                orm.session.commit()
                response = {"mensagem": "aluno atualizado"}, 200
            else:
                response = {"mensagem": "aluno não encontrado"}, 200
        except Exception as e:
            response = {"mensagem": str(e)}, 500
        
        return response
    elif geral == 'disciplina':
        try:
            disciplina = Disciplina.query.get(dados['id']) #resgatamos os dados do aluno
                                                #da base de dados
            if disciplina:
                #atualizamos as props
                disciplina.nome = dados['nome']
                disciplina.carga_horaria = dados['carga_horaria']
                disciplina.data_atualizacao = datetime.now()
                
                orm.session.commit()
                response = {"mensagem": "disciplina atualizada"}, 200
            else:
                response = {"mensagem": "disciplina não encontrado"}, 200
        except Exception as e:
            response = {"mensagem": str(e)}, 500
        
        return response

    elif geral == 'endereco':
        try:
            endereco = Endereco.query.get(dados['id']) #resgatamos os dados do aluno
                                                #da base de dados
            if endereco:
                #atualizamos as props
                endereco.logradouro = dados['logradouro']
                endereco.cep = dados['cep']
                endereco.cidade = dados['cidade']
                
                orm.session.commit()
                response = {"mensagem": "endereco atualizada"}, 200
            else:
                response = {"mensagem": "endereco não encontrado"}, 200
        except Exception as e:
            response = {"mensagem": str(e)}, 500
        
        return response

@servidor.route("/escola/<string:geral>/<int:id>", methods=['DELETE'])
def deletar(geral,id) :
    geral = geral.lower()
    if geral == 'aluno':
        try:
            aluno = Aluno.query.get(id)
            
            orm.session.delete(aluno)
            orm.session.commit()

            response = {"mensagem":"aluno deletado"},200
        except:
            response = {"mensagem":"erro de servidor"}, 500
        
        return response
    elif geral == 'disciplina':
        try:
            disciplina = Disciplina.query.get(id)
            
            orm.session.delete(disciplina)
            orm.session.commit()

            response = {"mensagem":"disciplina deletada"},200
        except:
            response = {"mensagem":"erro de servidor"}, 500
        
        return response

    elif geral == 'endereco':
        try:
            endereco = Endereco.query.get(id)
            
            orm.session.delete(endereco)
            orm.session.commit()

            response = {"mensagem":"endereco deletado"},200
        except:
            response = {"mensagem":"erro de servidor"}, 500
        
        return response

@servidor.route("/escola/matricular", methods=['POST'])
async def matricular_aluno():
    dados = request.get_json()
    
    aluno_id = dados['aluno_id']
    disciplina_id = dados['disciplina_id']
    
    try:
        aluno = Aluno.query.get(aluno_id)
        disciplina = Disciplina.query.get(disciplina_id)
        
        if aluno and disciplina:
            aluno.ad.append(disciplina)
            orm.session.commit()
            
            response = {"mensagem": "Aluno matriculado na disciplina"}, 200
        else:
            response = {"mensagem": "Aluno ou disciplina não encontrados"}, 500
    except Exception as e:
        response = {"mensagem": str(e)}, 500
    
    return response


with servidor.app_context() :
    orm.create_all() #vai verificar quais classes não 
                     #possuem tabelas e criá-las

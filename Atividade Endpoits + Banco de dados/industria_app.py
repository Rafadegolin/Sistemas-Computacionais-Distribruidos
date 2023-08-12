from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

servidor = Flask(__name__)
servidor.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db-orm.db"
orm = SQLAlchemy()

class Catalogo(orm.Model):
    id = orm.Column(orm.Integer, primary_key = True, autoincrement = True) # id automatico no banco
    codigo = orm.Column(orm.Integer, nullable = False) # codigo para dividir as areas 
    area = orm.Column(orm.String, nullable = False) # industria / inovação / infraestrutura
    nome = orm.Column(orm.String, nullable = False) # nome 
    especificacao = orm.Column(orm.String, nullable = False) # exemplo
    score = orm.Column(orm.Integer)

orm.init_app(servidor)

# home da pagina de catalogo
@servidor.route("/home")
def home():
    return "Servidor executando normalmente!", 200

@servidor.route("/cadastro", methods = ['POST'])
def cadastrar_no_catalogo():
    # resgatamos os dados do corpo da requisição
    dados = request.get_json()

    # criamos o objeto Catalogo que contem interfaces/metodos com o ORM
    catalogo = Catalogo (
        codigo = dados['codigo'],
        area = dados['area'],
        nome = dados['nome'],
        especificacao = dados['especificacao'],
        score = dados['score']
    )

    try:
        # atraves da sessão do banco de dados disponibilizada pelo nosso ORM
        orm.session.add(catalogo)
        orm.session.commit()
        orm.session.refresh(catalogo)

        response = { "catalogo_id" : catalogo.id}, 201
    except:
        response = { "mensagem" : "Erro na adição ao banco" }, 500

    return response

@servidor.route("/catalogo/<int:id>")
def consultar_catalogo_id(id): # consulta por ID
    catalogo = Catalogo.query.get(id)

    response = {
        "id" : catalogo.id,
        "codigo" : catalogo.codigo,
        "area" : catalogo.area,
        "nome" : catalogo.nome,
        "especificacao" : catalogo.especificacao,
        "score" : catalogo.score
    }, 200

    return response

@servidor.route("/catalogo/consultarnome/<string:nome>")
def consultar_catalogo_nome(nome): # consulta por nome
 
    # filtro via nome se existir IDENTICO
    # alunos = Aluno.query.filter_by(nome = nome).all()

    # filtro por nome parecido
    nome = f'%{nome}%'

    catalogos = Catalogo.query \
                  .filter(Catalogo.nome.like(nome)) \
                  .all() # resgata todos os registros da tebela
                         # que contenham substring que veio da URL (contains)

    response = [{
        "catalogo_id" : catalogo.id,
        "codigo" : catalogo.codigo,
        "area" : catalogo.area,
        "nome" : catalogo.nome,
        "especificacao" : catalogo.especificacao,
        "score" : catalogo.score
    } for catalogo in catalogos ]

    return response, 200

@servidor.route("/catalogo")
def listar_catalogo_todo():
    catalogos = Catalogo.query.all() # resgata todos os registros da tabela

    response = [{
        "catalogo_id" : catalogo.id,
        "codigo" : catalogo.codigo,
        "area" : catalogo.area,
        "nome" : catalogo.nome,
        "especificacao" : catalogo.especificacao,
        "score" : catalogo.score
    } for catalogo in catalogos ]

    return response, 200

@servidor.route("/catalogo", methods = ['PUT'])
def atualizar_aluno(): # atualizar registro dentro do catalogo
    dados = request.get_json()

    try:
        catalogo = Catalogo.query.get(dados['id'])

        if catalogo:
            # atualizamos as props
            catalogo.codigo = dados['codigo']
            catalogo.area = dados['area']
            catalogo.nome = dados['nome']
            catalogo.especificacao = dados['especificacao']
            catalogo.score = dados['score']

            orm.session.commit()
            response = { "mensagem" : "Item atualizado" }, 200
        else:
            response = { "mensagem" : "Item não encontrado" }, 200
    except:
        response = { "mensagem" : "erro ao atualizar!" }, 500

    return response

@servidor.route("/catalogo/<int:id>", methods = ['DELETE'])
def deletar_catalogo(id):
    try:
        catalogo = Catalogo.query.get(id)
        
        orm.session.delete(catalogo)
        orm.session.commit()
        
        response = { "mensagem" : "Item deletado" }, 200
    except:
        response = { "mensagem" : "Erro de servidor" }, 500
    
    return response

@servidor.route("/networking")
def juntar_especilidades():
    items_relacionar = Catalogo.query.filter(Catalogo == 'inovacao' or Catalogo == 'infraestrutura').order_by(Catalogo.score.desc()).all()
    items_industria = Catalogo.query.filter(Catalogo == 'industria').all()
    items_relacionados = []

    for item_relacionar in items_relacionar:
        for item_industria in items_industria:
            if item_relacionar.especificacao in item_industria.especificacao:
                items_relacionados.append({'inovacao': {'area': item_relacionar.area, 'especificacao': item_relacionar.especificacao, 'score': item_relacionar.score}, 'industria': {'area': item_industria.area, 'especificacao': item_industria.especificacao, 'score': item_industria.score}})
    return jsonify({ 'Itens relacionados' : items_relacionados })


@servidor.route("/score/<int:id>", methods = ['PUT']) # adicionar score a itens
def adiciona_score(id):
    dados = request.get_json()

    try:
        catalogo = Catalogo.query.get(id)

        if catalogo:
            # atualizamos as props
            catalogo.score = dados['score']

            orm.session.commit()
            response = { "mensagem" : "Score do item atualizado" }, 200
        else:
            response = { "mensagem" : "Item não encontrado" }, 200
    except:
        response = { "mensagem" : "Erro ao atualizar o score" }, 500

    return response


@servidor.route("/ranking") # rankeamento das empresas
def print_ranking_empresas():
    ranking = Catalogo.query.order_by(Catalogo.score.desc()).all()

    response = [{
        "catalogo_id" : catalogo.id,
        "codigo" : catalogo.codigo,
        "area" : catalogo.area,
        "nome" : catalogo.nome,
        "especificacao" : catalogo.especificacao,
        "score" : catalogo.score
    } for catalogo in ranking ]

    return response, 200
    

@servidor.route("/busca/<int:score>") # aqui as empresas vao buscar pelas inovacoes com melhor score
def busca(score):
    scores = Catalogo.query.filter(Catalogo.score >= score, Catalogo.area == "inovacao").order_by(Catalogo.score.desc()).all()

    response = [{
        "catalogo_id" : catalogo.id,
        "codigo" : catalogo.codigo,
        "area" : catalogo.area,
        "nome" : catalogo.nome,
        "especificacao" : catalogo.especificacao,
        "score" : catalogo.score
    } for catalogo in scores ]

    return response, 200   
    
with servidor.app_context():
    orm.create_all() # vai verificar quais classes não possuem tabelas e cria-las
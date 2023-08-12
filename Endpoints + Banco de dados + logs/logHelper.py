import json
import requests_async as req_async

async def gravarCadastro_log(aluno):
    try:
        await req_async.post("http://127.0.0.1:3000/log", 
                                    data = json.dumps({
                                        "mensagem" : f"entidade add com sucesso! - Id:{aluno.id}"
                                }))
    except Exception as e:
        print(str(e))

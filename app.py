from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import unicodedata
import json
import os

app = Flask(__name__)
CORS(app)

def carregar_catalogo():
    with open('catalogo.json', 'r', encoding='utf-8') as f:
        return json.load(f)
def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()



@app.route('/buscar')
def buscar():
    termo = request.args.get('titulo', '').strip()
    termo_normalizado = normalizar(termo)
    catalogo = carregar_catalogo()

    # Busca parcial (contendo o termo em qualquer parte do título)
    livros_encontrados = [
        livro for livro in catalogo
        if termo_normalizado in normalizar(livro.get('titulo', ''))
    ]

    if livros_encontrados:
        # Sempre retorna lista se mais de um resultado for compatível
        if len(livros_encontrados) == 1:
            livro = livros_encontrados[0]
            imagem = f"/imagens/{livro['titulo']}.png"
            return jsonify({
                "tipo": "livro",
                "titulo": livro['titulo'],
                "autor": livro['autor'],
                "sinopse": livro.get('sinopse', ''),
                "disponivel": livro.get('disponivel', False),
                "imagem": imagem
            })
        else:
            return jsonify({
                "tipo": "lista",
                "termo": termo,
                "livros": sorted([
                    {
                        "titulo": livro['titulo'],
                        "autor": livro['autor'],
                        "disponivel": livro.get('disponivel', False)
                    }
                    for livro in livros_encontrados
                ], key=lambda l: l['titulo'])  # ordena alfabeticamente
            })

    # Busca por autor
    livros_do_autor = [
        {
            "titulo": livro['titulo'],
            "autor": livro['autor'],
            "disponivel": livro.get('disponivel', False)
        }
        for livro in catalogo
        if termo_normalizado in normalizar(livro.get('autor', ''))
    ]

    if livros_do_autor:
        return jsonify({
            "tipo": "autor",
            "autor": termo,
            "livros": livros_do_autor
        })

    return jsonify({"erro": "Nenhum resultado encontrado"}), 404

@app.route('/imagens/<path:filename>')
def imagens(filename):
    return send_from_directory(os.path.join(app.root_path, 'imagens'), filename)

@app.route('/contar')
def contar_disponiveis():
    catalogo = carregar_catalogo()
    total_disponiveis = sum(1 for livro in catalogo if livro.get('disponivel', False))
    return jsonify({"total_disponiveis": total_disponiveis})

@app.route('/catalogo')
def obter_catalogo():
    catalogo = carregar_catalogo()
    return jsonify(catalogo)

@app.route('/todos', methods=['GET'])
def listar_todos():
    catalogo = carregar_catalogo()
    return jsonify(catalogo)

@app.route('/atualizar', methods=['POST'])
def atualizar_livro():
    data = request.get_json()
    if not data or 'titulo' not in data:
        return jsonify({'erro': 'Requisição inválida'}), 400

    catalogo = carregar_catalogo()

    titulo_normalizado = normalizar(data['titulo'])
    atualizado = False

    for i, livro in enumerate(catalogo):
        if normalizar(livro.get('titulo', '')) == titulo_normalizado:
            catalogo[i] = data
            atualizado = True
            break

    if not atualizado:
        return jsonify({'erro': 'Livro não encontrado'}), 404

    with open('catalogo.json', 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)

    return jsonify({'mensagem': 'Livro atualizado com sucesso'})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

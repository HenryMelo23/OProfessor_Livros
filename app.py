from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

def carregar_catalogo():
    with open('catalogo.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/buscar')
def buscar():
    titulo = request.args.get('titulo', '').lower()
    catalogo = carregar_catalogo()
    for livro in catalogo:
        if titulo in livro['titulo'].lower():
            imagem = f"/imagens/{livro['titulo']}.png"
            return jsonify({
                "titulo": livro['titulo'],
                "autor": livro['autor'],
                "sinopse": livro['sinopse'],
                "disponivel": livro['disponivel'],
                "imagem": imagem
            })
    return jsonify({"disponivel": False})

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

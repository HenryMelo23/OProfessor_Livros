from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json

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
def imagem(filename):
    return send_from_directory('imagens', filename)

if __name__ == '__main__':
    app.run(debug=True)

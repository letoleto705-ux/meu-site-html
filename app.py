import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
# Libera totalmente o acesso para o GitHub Pages e qualquer navegador
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError('A variável DATABASE_URL não está configurada')
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'online', 'mensagem': 'API CMV Food ativa!'}), 200

@app.route('/api/leads', methods=['POST'])
def salvar_lead():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum dado enviado'}), 400

    nome = data.get('nome')
    whatsapp = data.get('whatsapp')
    produto_interesse = data.get('produto_interesse')

    if not isinstance(nome, str) or not nome.strip() or not isinstance(whatsapp, str) or not whatsapp.strip():
        return jsonify({'status': 'erro', 'mensagem': 'Nome e WhatsApp são obrigatórios'}), 400

    nome = nome.strip()
    whatsapp = whatsapp.strip()
    if len(nome) > 255 or len(whatsapp) > 50:
        return jsonify({'status': 'erro', 'mensagem': 'Nome ou WhatsApp excede o tamanho permitido'}), 400
    if produto_interesse is not None and (
        not isinstance(produto_interesse, str) or len(produto_interesse) > 100
    ):
        return jsonify({'status': 'erro', 'mensagem': 'Produto de interesse inválido'}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO leads_cmv_food (nome, whatsapp, produto_interesse)
                    VALUES (%s, %s, %s);
                    """,
                    (nome, whatsapp, produto_interesse)
                )

        return jsonify({'status': 'sucesso', 'mensagem': 'Lead cadastrado com sucesso!'}), 201

    except Exception:
        app.logger.exception('Erro ao salvar lead no banco de dados')
        return jsonify({'status': 'erro', 'mensagem': 'Não foi possível salvar o cadastro'}), 500
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
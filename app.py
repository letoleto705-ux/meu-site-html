import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'online', 'mensagem': 'API CMV Food ativa!'}), 200

@app.route('/api/leads', methods=['POST'])
def salvar_lead():
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum dado enviado'}), 400

    nome = data.get('nome')
    whatsapp = data.get('whatsapp')
    produto_interesse = data.get('produto_interesse')

    if not nome or not whatsapp:
        return jsonify({'status': 'erro', 'mensagem': 'Nome e WhatsApp são obrigatórios'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            INSERT INTO leads_cmv_food (nome, whatsapp, produto_interesse)
            VALUES (%s, %s, %s);
            """,
            (nome, whatsapp, produto_interesse)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'status': 'sucesso', 'mensagem': 'Lead cadastrado com sucesso!'}), 201

    except Exception as e:
        print(f"Erro ao salvar no Neon: {e}")
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
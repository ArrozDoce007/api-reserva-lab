from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="contatosdb.czgi8q4wyk3b.sa-east-1.rds.amazonaws.com",
            user="admin",
            password="26042004",
            database="contatos_db"  # Certifique-se de ter um banco de dados criado com esse nome
        )
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return connection

@app.route('/', methods=['GET'])
def helo():
    html = "hello"
    return html

# Rota para obter todos os contatos
@app.route('/contatos', methods=['GET'])
def get_contatos():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contatos")
    rows = cursor.fetchall()
    return jsonify(rows), 200

# Rota para criar um novo contato
@app.route('/contatos/novo', methods=['POST'])
def novo_contato():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    numero = data.get('numero')
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO contatos (nome, email, numero) VALUES (%s, %s, %s)", (nome, email, numero))
    connection.commit()
    return jsonify({'message': 'Contato criado com sucesso!'}), 200

# Rota para atualizar um contato existente
@app.route('/contatos/editar/<int:id>', methods=['PUT'])
def editar_contato(id):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    numero = data.get('numero')
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE contatos SET nome = %s, email = %s, numero = %s WHERE id = %s", (nome, email, numero, id))
    connection.commit()
    return jsonify({'message': 'Contato atualizado com sucesso!'}), 200

# Rota para deletar um contato
@app.route('/contatos/delete/<int:id>', methods=['DELETE'])
def deletar_contato(id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM contatos WHERE id = %s", (id,))
    connection.commit()
    return jsonify({'message': 'Contato deletado com sucesso!'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' port=5000)

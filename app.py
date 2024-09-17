from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Conexão com o banco de dados MySQL
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="lab_reserva",
        database="lab_reservation"
    )
    cursor = db.cursor(dictionary=True)
except mysql.connector.Error as err:
    print(f"Erro ao conectar ao banco de dados: {err}")
    exit(1)

# Rota para logar na pagina inicial
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    matricula = data.get('matricula')
    senha = data.get('senha')

    cursor.execute('SELECT nome, matricula, tipo_usuario FROM usuarios WHERE matricula = %s AND senha = %s', (matricula, senha))
    user = cursor.fetchone()

    if user:
        return jsonify({
            'success': True,
            'nome': user['nome'],
            'matricula': user['matricula'],
            'tipo_usuario': user['tipo_usuario']
        })
    else:
        return jsonify({'success': False, 'message': 'Matrícula ou senha inválidos'}), 401

# Rota para fazer a reserva
@app.route('/reserve', methods=['POST'])
def reservas_lab():
    try:
        # Recebe os dados do formulário
        data = request.json
        lab_name = data.get('labName')
        date = data.get('date')
        time = data.get('time')
        time_fim = data.get('time_fim')  # Adiciona o campo time_fim
        purpose = data.get('purpose')
        nome = data.get('userName')
        matricula = data.get('userMatricula')

        # Insere a reserva no banco de dados
        insert_query = """
        INSERT INTO reservas (lab_name, date, time, time_fim, purpose, nome, matricula, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (lab_name, date, time, time_fim, purpose, nome, matricula, "pendente"))
        db.commit()

        return "", 204

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": "Erro ao processar a reserva"}), 500

# Rota para obter o reserva geral
@app.route('/reserve/status/geral', methods=['GET'])
def get_reservas_geral():
    try:
        # Consulta as reservas
        query = "SELECT id, lab_name, date, time, time_fim, purpose, status, nome, matricula FROM reservas"
        cursor.execute(query)
        reservations = cursor.fetchall()

        return jsonify(reservations)

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": "Erro ao recuperar as reservas"}), 500
    
# Rota para obter reserva por matricula
@app.route('/reserve/status', methods=['GET'])
def get_reservas_por_matricula():
    try:
        # Consulta as reservas com os campos necessários, incluindo a matrícula
        query = "SELECT id, lab_name, date, time, time_fim, purpose, status, nome, matricula FROM reservas"
        cursor.execute(query)
        reservations = cursor.fetchall()

        # Formatação das reservas em um formato de lista de dicionários
        reservations_list = []
        for reservation in reservations:
            reservations_list.append({
                'id': reservation['id'],
                'lab_name': reservation['lab_name'],
                'date': reservation['date'],
                'time': reservation['time'],
                'time_fim': reservation['time_fim'],
                'purpose': reservation['purpose'],
                'status': reservation['status'],
                'user_name': reservation['nome'],  # Renomeando para o front-end
                'user_matricula': reservation['matricula']  # Renomeando para o front-end
            })

        return jsonify(reservations_list)

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": "Erro ao recuperar as reservas"}), 500

# Rota para cancelar solicitação
@app.route('/reserve/<int:id>', methods=['PUT'])
def update_reservas(id):
    try:
        data = request.json
        new_status = data.get('status')

        if new_status not in ['pendente', 'aprovado', 'cancelado']:
            return jsonify({"error": "Status inválido"}), 400

        update_query = "UPDATE reservas SET status = %s WHERE id = %s"
        cursor.execute(update_query, (new_status, id))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Reserva não encontrada"}), 404

        return jsonify({"message": "Status da reserva atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar a reserva: {str(e)}"}), 500
   
# Rota para aprovar ou rejeitar 
@app.route('/reserve/pedido/<int:id>', methods=['PUT'])
def update_reservas_aprj(id):
    try:
        data = request.json
        new_status = data.get('status')

        if new_status not in ['pendente', 'aprovado', 'rejeitado']:
            return jsonify({"error": "Status inválido"}), 400

        update_query = "UPDATE reservas SET status = %s WHERE id = %s"
        cursor.execute(update_query, (new_status, id))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Reserva não encontrada"}), 404

        return jsonify({"message": "Status da reserva atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar a reserva: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

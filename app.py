from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(host='localhost', user='root', password='', database='turnos_saas')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (data['email'], data['password']))
    user = cursor.fetchone()
    conn.close()
    if user: return jsonify({"id": user['id'], "negocio": user['nombre_negocio']})
    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/api/clientes', methods=['GET', 'POST'])
def clientes():
    usuario_id = request.headers.get('User-ID')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM clientes WHERE usuario_id=%s ORDER BY id DESC", (usuario_id,))
        res = cursor.fetchall()
        conn.close()
        return jsonify(res)

    if request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO clientes (usuario_id, nombre, telefono) VALUES (%s, %s, %s)",
                       (usuario_id, data['nombre'], data['telefono']))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Cliente guardado"})

@app.route('/api/turnos', methods=['GET', 'POST'])
def turnos():
    usuario_id = request.headers.get('User-ID')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        # Traemos los turnos ordenados por fecha (los más nuevos primero)
        query = """
            SELECT t.id, t.fecha, t.detalle, t.estado, c.nombre as cliente
            FROM turnos t
            JOIN clientes c ON t.cliente_id = c.id
            WHERE t.usuario_id = %s
            ORDER BY t.fecha DESC
        """
        cursor.execute(query, (usuario_id,))
        res = cursor.fetchall()
        conn.close()
        return jsonify(res)

    if request.method == 'POST':
        data = request.json
        query = "INSERT INTO turnos (usuario_id, cliente_id, fecha, detalle) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (usuario_id, data['cliente_id'], data['fecha'], data['detalle']))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Turno agendado"})

@app.route('/api/turnos/<int:id>/finalizar', methods=['PUT'])
def finalizar_turno(id):
    usuario_id = request.headers.get('User-ID')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE turnos SET estado='finalizado' WHERE id=%s AND usuario_id=%s", (id, usuario_id))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Turno finalizado"})

# --- NUEVA RUTA: CANCELAR TURNO ---
@app.route('/api/turnos/<int:id>/cancelar', methods=['PUT'])
def cancelar_turno(id):
    usuario_id = request.headers.get('User-ID')
    conn = get_db()
    cursor = conn.cursor()
    
    # Solo cancela si el turno pertenece al usuario logueado
    cursor.execute("UPDATE turnos SET estado='cancelado' WHERE id=%s AND usuario_id=%s", (id, usuario_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "No se pudo cancelar"}), 404
        
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Turno cancelado"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
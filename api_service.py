import os
import mysql.connector 
from flask import Flask, request, jsonify 
from datetime import datetime
import socket

app = Flask(__name__) 

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS', 'root_password'),
    'database': os.environ.get('DB_NAME', 'notifyhub_db')
}

def get_db_connection():
    """Crea y retorna una conexión a MySQL."""
    return mysql.connector.connect(**DB_CONFIG)

def setup_db():
    """Inicializa la tabla de logs en MySQL si no existe."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                balancer_id VARCHAR(50),
                api_instance VARCHAR(50),
                queue_used VARCHAR(50),
                worker_id VARCHAR(50),
                notification_type VARCHAR(10) NOT NULL,
                recipient VARCHAR(100) NOT NULL,
                status VARCHAR(50),
                processed_at VARCHAR(50)
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"ERROR: Falló la conexión/setup de MySQL: {e}")
        exit(1)

setup_db() 


def log_notification(data):
    """Registra la trazabilidad en MySQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    API_INSTANCE_ID = socket.gethostname() 
    
    try:
        sql = """
            INSERT INTO logs (
                balancer_id, api_instance, queue_used, worker_id, 
                notification_type, recipient, status, processed_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            'NGINX_PROXY_SIMULADO',
            API_INSTANCE_ID,
            'NONE_SIMULADO',
            'API_DIRECTO',
            data['type'].upper(),
            data['recipient'],
            'REGISTRADO_DIRECTO',
            datetime.now().isoformat()
        )
        cursor.execute(sql, values)
        conn.commit()
    except Exception as e:
        print(f"Error al registrar en BD: {e}")
        return False
    finally:
        conn.close()
    return True
    

@app.get("/health")
def health():
    """Ruta de salud del servicio y prueba de conexión a MySQL."""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "ok", "db_status": "MySQL connected"}), 200
    except Exception as e:
        return bad_request(f"Error al conectar con la BD MySQL: {str(e)}", 503)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
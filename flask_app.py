from flask import Flask, jsonify
import sqlite3
from datetime import datetime, date
import json
import locale
import os

# 1. Creación de la instancia de la aplicación fuera del bloque if __name__ == '__main__':
app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chequera.db')

def get_db_connection():
    # Función de ayuda para conectar a la DB
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

def set_spanish_locale():
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'es')
            except locale.Error:
                pass 

# Ruta para la API lectura_anual
@app.route('/api/lectura_anual', methods=['GET'])
def obtener_lectura_anual():
    # Obtener el número del día actual en el año
    dia_actual = datetime.now().timetuple().tm_yday

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT dia, sabiduria, nuevo_testamento, antiguo_testamento
        FROM lectura_anual
        WHERE dia = ?
    ''', (dia_actual,))

    resultado = cursor.fetchone()

    # Cerrar la conexión a la base de datos
    conn.close()

    # Verificar si se encontraron datos para el día actual
    if resultado:
        datos = {
            "dia": resultado[0],
            "sabiduria": resultado[1],
            "nuevo_testamento": resultado[2],
            "antiguo_testamento": resultado[3]
        }
        return jsonify(datos), 200
    else:
        return jsonify({"mensaje": "No se encontraron datos para el día actual"}), 404

# Ruta para la API chequera
@app.route('/api/chequera', methods=['GET'])
def obtener_chequera():
    # Establecer la configuración regional a español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    # Obtener el día y el mes actual
    dia_actual = date.today().day
    mes_actual_espanol = datetime.now().strftime("%B").capitalize()  # Obtener el nombre del mes en español

    # Conectar a la base de datos
    conn = sqlite3.connect('chequera.db')
    cursor = conn.cursor()

    # Obtener todos los registros de la tabla 'chequera' para el día y el mes actual
    cursor.execute('SELECT * FROM chequera WHERE dia_del_mes = ? AND mes = ?', (dia_actual, mes_actual_espanol))
    registros = cursor.fetchall()

    # Verificar si hay registros para el día y el mes actual
    if registros:
        # Obtener los datos del primer registro (puedes ajustar según tu lógica)
        dia_registro = registros[0][1]
        mes_registro = registros[0][2]
        versiculo_registro = registros[0][3]
        devocional_registro = registros[0][4]

        # Devolver los datos en formato JSON con el orden especificado
        return jsonify({
            'dia': dia_registro,
            'mes': mes_registro,
            'versiculo': versiculo_registro,
            'devocional': devocional_registro
        })
    else:
        return jsonify({'mensaje': 'No hay devocional disponible para el día y el mes actual'})

    # Cerrar la conexión a la base de datos
    conn.close()

# Health check route
@app.route('/ping', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "API is running"}), 200

# 3. Eliminar el bloque if __name__ == '__main__':
# Vercel no lo ejecuta, ya que importa la variable `app`.
# if __name__ == '__main__':
# 	app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
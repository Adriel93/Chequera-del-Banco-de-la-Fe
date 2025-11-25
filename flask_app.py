from flask import Flask, jsonify
import sqlite3
from datetime import datetime, date
import json
import locale
import os
from flask import send_from_directory


# 1. Creación de la instancia de la aplicación fuera del bloque if __name__ == '__main__':
app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chequera.db')

MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}



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
@app.route('/lectura_anual', methods=['GET'])
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
@app.route('/chequera', methods=['GET'])
def obtener_chequera():

    # Día y mes actual
    dia_actual = date.today().day
    mes_actual = datetime.now().month
    mes_actual_espanol = MESES_ES[mes_actual]

    # Conectar DB
    conn = sqlite3.connect('chequera.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM chequera WHERE dia_del_mes = ? AND mes = ?',
        (dia_actual, mes_actual_espanol)
    )
    registros = cursor.fetchall()

    if registros:
        dia_registro = registros[0][1]
        mes_registro = registros[0][2]
        versiculo_registro = registros[0][3]
        devocional_registro = registros[0][4]

        conn.close()

        return jsonify({
            'dia': dia_registro,
            'mes': mes_registro,
            'versiculo': versiculo_registro,
            'devocional': devocional_registro
        })

    conn.close()
    return jsonify({'mensaje': 'No hay devocional disponible para hoy'})

# Health check route
@app.route('/ping', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "API is running"}), 200


@app.route('/qr.png')
def qr_code():
    return send_from_directory('.', 'qr.png')


@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>API – Chequera del Banco de la Fe</title>

        <style>
            body {
                font-family: "Georgia", "Times New Roman", serif;
                background: #fdfbf7;
                color: #2a2a2a;
                max-width: 900px;
                margin: auto;
                padding: 30px;
                line-height: 1.7;
            }

            h1 {
                text-align: center;
                font-size: 40px;
                margin-bottom: 5px;
                font-weight: bold;
            }

            h2 {
                font-size: 26px;
                margin-top: 40px;
                padding-bottom: 6px;
                border-bottom: 2px solid #d6c9a3;
            }

            .subtitle {
                text-align: center;
                font-size: 18px;
                color: #444;
                margin-bottom: 25px;
            }

            p {
                font-size: 18px;
            }

            a {
                color: #654321;
                text-decoration: none;
                font-weight: bold;
            }

            a:hover {
                text-decoration: underline;
            }

            .endpoint {
                font-size: 22px;
                margin-top: 30px;
                font-weight: bold;
            }

            pre {
                background: #f4efe6;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #d6c9a3;
                overflow-x: auto;
            }

            .qr-container {
                text-align: center;
                margin-top: 40px;
                margin-bottom: 40px;
            }

            .qr-container img {
                width: 260px;
                border: 6px solid #e5dbc3;
                border-radius: 10px;
            }

            .small-note {
                text-align: center;
                font-size: 14px;
                margin-top: 10px;
                color: #555;
            }

            .footer {
                text-align: center;
                margin-top: 50px;
                font-size: 15px;
                color: #555;
            }
        </style>
    </head>

    <body>

        <h1>📘 Chequera del Banco de la Fe</h1>
        <div class="subtitle">
            API pública creada para edificación y servicio de la comunidad cristiana.
        </div>

        <p style="text-align:center;">
            Comunidad en Telegram:<br>
            <a href="https://t.me/cristianoreformado100" target="_blank">
                https://t.me/cristianoreformado100
            </a>
        </p>

        <p>
            Esta API ha sido creada para bendecir a todo creyente que desee acceder a devocionales diarios,
            lecturas bíblicas y recursos espirituales. 
            Puede ser utilizada en aplicaciones móviles, bots de Telegram, páginas web,
            devocionales automáticos o cualquier herramienta edificante.
        </p>

        <p>
            Es completamente libre de usar, siempre con moderación y para la gloria de Dios.
        </p>

        <h2>🙏 Donaciones en Bitcoin</h2>

        <p>
            Si deseas apoyar este proyecto y ayudar a mantenerlo online, puedes hacerlo enviando una ofrenda
            en Bitcoin. ¡Muchas gracias por sembrar en la obra del Señor!
        </p>

        <div class="qr-container">
            <img src="/qr.png" alt="QR Bitcoin">
            <div class="small-note">Escanea este código para donar en BTC.</div>
        </div>

        <h2>🚀 Endpoints disponibles</h2>

        <!-- /chequera -->
        <div class="endpoint">1. GET /chequera</div>
        <p>Devocional, versículo, día y mes correspondiente a la fecha actual.</p>
        <p><a href="/chequera" target="_blank">👉 Probar endpoint</a></p>

        <pre>{
  "devocional": "En esta hora un gran monte de dificultad...",
  "dia": 25,
  "mes": "Noviembre",
  "versiculo": "¿Quién eres tú, oh gran monte?... Zacarías 4:7"
}</pre>

        <!-- /lectura_anual -->
        <div class="endpoint">2. GET /lectura_anual</div>
        <p>Lectura bíblica correspondiente al día del año (AT, NT y Sabiduría).</p>
        <p><a href="/lectura_anual" target="_blank">👉 Probar endpoint</a></p>

        <pre>{
  "antiguo_testamento": "Ezequiel 47:1-48:35",
  "dia": 329,
  "nuevo_testamento": "1 Pedro 4:1-19",
  "sabiduria": "Salmos 133:1-3"
}</pre>

        <!-- /ping -->
        <div class="endpoint">3. GET /ping</div>
        <p>Comprueba si la API está funcionando correctamente.</p>
        <p><a href="/ping" target="_blank">👉 Probar endpoint</a></p>

        <pre>{
  "message": "API is running",
  "status": "OK"
}</pre>

        <div class="footer">
            Proyecto comunitario de libre uso — Que el Señor te bendiga poderosamente.<br>
            Si necesitas soporte o tienes sugerencias, contáctame en Telegram:<br>
            <a href="https://t.me/adriel_fj" target="_blank">@adriel_fj</a>
        </div>

    </body>
    </html>
    """


# 3. Eliminar el bloque if __name__ == '__main__':
# Vercel no lo ejecuta, ya que importa la variable `app`.
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
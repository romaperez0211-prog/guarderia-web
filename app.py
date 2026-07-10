from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# FUNCIÓN PARA CREAR LA BASE DE DATOS (El archivador digital)
def inicializar_base_datos():
    # Conectamos con el archivo de la base de datos (se creará solo)
    conexion = sqlite3.connect('guarderia.db')
    cursor = conexion.cursor()
    
    # Creamos la tabla con todos los campos del formulario si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tutor TEXT,
            apellido_tutor TEXT,
            identificacion TEXT,
            telefono TEXT,
            correo TEXT,
            nombre_nino TEXT,
            ano_nacimiento TEXT,
            edad_nino TEXT,
            tiene_enfermedad TEXT,
            detalles_enfermedad TEXT,
            es_alergico TEXT,
            detalles_alergia TEXT,
            informacion_adicional TEXT
        )
    ''')
    conexion.commit()
    conexion.close()

# Inicializamos la base de datos al arrancar el programa
inicializar_base_datos()

@app.route('/')
def mostrar_registro():
    return render_template('registro.html')

@app.route('/procesar', methods=['POST'])
def procesar_formulario():
    # 1. Atrapamos los datos del formulario HTML
    nombre_padre = request.form.get('nombre_tutor')
    apellido_padre = request.form.get('apellido_tutor')
    identificacion = request.form.get('identificacion')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    nombre_infante = request.form.get('nombre_nino')
    ano_nacimiento = request.form.get('ano_nacimiento')
    edad_infante = request.form.get('edad_nino')
    tiene_enfermedad = request.form.get('tiene_enfermedad')
    detalles_enfermedad = request.form.get('detalles_enfermedad')
    es_alergico = request.form.get('es_alergico')
    detalles_alergia = request.form.get('detalles_alergia')
    informacion_adicional = request.form.get('informacion_adicional')

    # 2. GUARDAMOS EN LA BASE DE DATOS REAL
    conexion = sqlite3.connect('guarderia.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        INSERT INTO registros (
            nombre_tutor, apellido_tutor, identificacion, telefono, correo,
            nombre_nino, ano_nacimiento, edad_nino,
            tiene_enfermedad, detalles_enfermedad, es_alergico, detalles_alergia,
            informacion_adicional
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nombre_padre, apellido_padre, identificacion, telefono, correo,
        nombre_infante, ano_nacimiento, edad_infante,
        tiene_enfermedad, detalles_enfermedad, es_alergico, detalles_alergia,
        informacion_adicional
    ))
    
    conexion.commit()
    conexion.close()

    # Mostramos una respuesta bonita en el navegador
    return f"¡Gracias {nombre_padre}! El registro de {nombre_infante} se ha guardado con éxito en la base de datos."

if __name__ == '__main__':
    # Configurado listo para escuchar conexiones locales y externas
    app.run(host='0.0.0.0', port=5000, debug=True)


    



    
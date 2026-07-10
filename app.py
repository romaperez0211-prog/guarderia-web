from flask import Flask, render_template, request, redirect, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Configuramos la carpeta donde se van a guardar las actas de nacimiento (PDF o imágenes)
CARPETA_UPLOADS = 'uploads'
app.config['UPLOAD_FOLDER'] = CARPETA_UPLOADS

# Si la carpeta 'uploads' no existe en la computadora o en Render, se crea sola
if not os.path.exists(CARPETA_UPLOADS):
    os.makedirs(CARPETA_UPLOADS)

# FUNCIÓN PARA CREAR LA BASE DE DATOS (El archivador digital)
def inicializar_base_datos():
    conexion = sqlite3.connect('guarderia.db')
    cursor = conexion.cursor()
    
    # Agregamos el campo 'acta_nacimiento' al final de la tabla
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
            informacion_adicional TEXT,
            acta_nacimiento TEXT
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
    # 1. Atrapamos los datos de texto del formulario
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

    # 2. PROCESAMOS EL ARCHIVO DEL ACTA DE NACIMIENTO
    archivo_acta = request.files.get('acta_nacimiento')
    nombre_archivo_final = ""

    if archivo_acta and archivo_acta.filename != '':
        # Para que no se dupliquen nombres de archivos, le pegamos el nombre del niño al inicio
        nombre_archivo_final = f"{nombre_infante}_{archivo_acta.filename}"
        # Guardamos el archivo físico en la carpeta uploads
        archivo_acta.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo_final))
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de la carpeta para guardar las actas de nacimiento
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta 'uploads' exista en el servidor de Render
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # TRUCO DE REINICIO: Borra la tabla vieja sin la columna para solucionar el error 500
    cursor.execute("DROP TABLE IF EXISTS registros")
    
    # Crea la tabla limpia y corregida con la columna 'acta_nacimiento'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tutor TEXT NOT NULL,
            apellido_tutor TEXT NOT NULL,
            identificacion TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT NOT NULL,
            nombre_nino TEXT NOT NULL,
            ano_nacimiento INTEGER NOT NULL,
            edad_nino INTEGER NOT NULL,
            tiene_enfermedad TEXT NOT NULL,
            detalles_enfermedad TEXT,
            es_alergico TEXT NOT NULL,
            detalles_alergia TEXT,
            informacion_adicional TEXT,
            acta_nacimiento TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar la base de datos al arrancar la aplicación
init_db()

# Ruta principal: Muestra el formulario de registro
@app.route('/')
def registro():
    return render_template('registro.html')

# Ruta para procesar los datos enviados por el formulario
@app.route('/procesar', methods=['POST'])
def procesar():
    if request.method == 'POST':
        nombre_tutor = request.form['nombre_tutor']
        apellido_tutor = request.form['apellido_tutor']
        identificacion = request.form['identificacion']
        telefono = request.form['telefono']
        correo = request.form['correo']
        nombre_nino = request.form['nombre_nino']
        ano_nacimiento = int(request.form['ano_nacimiento'])
        edad_nino = int(request.form['edad_nino'])
        tiene_enfermedad = request.form['tiene_enfermedad']
        detalles_enfermedad = request.form.get('detalles_enfermedad', '')
        es_alergico = request.form['es_alergico']
        detalles_alergia = request.form.get('detalles_alergia', '')
        informacion_adicional = request.form.get('informacion_adicional', '')
        
        # Procesamiento y guardado del archivo adjunto (Acta de nacimiento)
        file = request.files.get('acta_nacimiento')
        nombre_archivo_final = "no_file.png"
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Renombrar el archivo usando el nombre del niño para evitar duplicados
            extension = filename.rsplit('.', 1)[1].lower()
            nuevo_nombre = f"acta_{secure_filename(nombre_nino)}.{extension}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nuevo_nombre))
            nombre_archivo_final = nuevo_nombre

        # Guardar la información en la base de datos corregida
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registros (
                nombre_tutor, apellido_tutor, identificacion, telefono, correo,
                nombre_nino, ano_nacimiento, edad_nino, tiene_enfermedad, detalles_enfermedad,
                es_alergico, detalles_alergia, informacion_adicional, acta_nacimiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nombre_tutor, apellido_tutor, identificacion, telefono, correo,
            nombre_nino, ano_nacimiento, edad_nino, tiene_enfermedad, detalles_enfermedad,
            es_alergico, detalles_alergia, informacion_adicional, nombre_archivo_final
        ))
        conn.commit()
        conn.close()
        
        return "<h1>¡Registro completado con éxito! Los datos y el archivo se han guardado de manera segura.</h1><p><a href='/'>Volver al formulario</a></p>"

# Ruta exclusiva del dueño: Ver la tabla de registros administradores
@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM registros')
    datos = cursor.fetchall()
    conn.close()
    return render_template('admin.html', registros=datos)

# Ruta para permitir al dueño ver/descargar los archivos guardados
@app.route('/uploads/<filename>')
def ver_archivo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)



    
    



    
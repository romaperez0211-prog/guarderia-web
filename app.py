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

    # 3. GUARDAMOS EN LA BASE DE DATOS REAL (Incluyendo el acta de nacimiento)
    conexion = sqlite3.connect('guarderia.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        INSERT INTO registros (
            nombre_tutor, apellido_tutor, identificacion, telefono, correo,
            nombre_nino, ano_nacimiento, edad_nino,
            tiene_enfermedad, detalles_enfermedad, es_alergico, detalles_alergia,
            informacion_adicional, acta_nacimiento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nombre_padre, apellido_padre, identificacion, telefono, correo,
        nombre_infante, ano_nacimiento, edad_infante,
        tiene_enfermedad, detalles_enfermedad, es_alergico, detalles_alergia,
        informacion_adicional, nombre_archivo_final
    ))
    
    conexion.commit()
    conexion.close()

    return f"¡Gracias {nombre_padre}! El registro de {nombre_infante} con su acta de nacimiento se ha guardado con éxito."

# -----------------------------------------------------------------
# PÁGINAS EXCLUSIVAS PARA EL DUEÑO DE LA GUARDERÍA
# -----------------------------------------------------------------

@app.route('/admin')
def panel_administrador():
    # Buscamos todos los niños registrados en la base de datos
    conexion = sqlite3.connect('guarderia.db')
    conexion.row_factory = sqlite3.Row  # Esto nos permite usar los nombres de las columnas en el HTML
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM registros')
    lista_ninos = cursor.fetchall()
    conexion.close()
    
    # Le mandamos la lista a una pantalla especial llamada admin.html
    return render_template('admin.html', ninos=lista_ninos)

@app.route('/ver-acta/<path:filename>')
def descargar_ver_acta(filename):
    # Esta ruta permite que cuando el dueño le dé clic al botón, se abra el PDF en el navegador
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



    

    



    
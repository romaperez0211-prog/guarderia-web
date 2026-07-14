import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from supabase import create_client, Client

# Credenciales de tu proyecto en Supabase
SUPABASE_URL = "https://rwnlofwkexxflmwxddpl.supabase.co"
SUPABASE_KEY = "sb_publishable_knGfUYRT8CLdh6XreRXiSQ_7tE7m-NS"

# Inicializamos el cliente oficial
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = 'llave_secreta_super_segura_para_la_guarderia'

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
@app.route('/enviar', methods=['POST']).
# 1. Recibir los datos del formulario (esto se queda igual que como lo tenías)
nombre_tutor = request.form.get('nombre_tutor')
apellido_tutor = request.form.get('apellido_tutor')
identificacion = request.form.get('identificacion')
telefono = request.form.get('telefono')
correo = request.form.get('correo')
nombre_nino = request.form.get('nombre_nino')
ano_nacimiento = int(request.form.get('ano_nacimiento', 0))
edad_nino = int(request.form.get('edad_nino', 0))
tiene_enfermedad = request.form.get('tiene_enfermedad')
detalles_enfermedad = request.form.get('detalles_enfermedad', '')
es_alergico = request.form.get('es_alergico')
detalles_alergia = request.form.get('detalles_alergia', '')
informacion_adicional = request.form.get('informacion_adicional', '')

# Manejo del archivo (acta de nacimiento)
file = request.files.get('acta_nacimiento')
nombre_archivo_final = ""

if file and file.filename != '':
    # Creamos un nombre único para el archivo usando la identificación del tutor
    extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    nombre_archivo_final = f"acta_{identificacion}.{extension}"
    
    # Leemos los bytes del archivo cargado
    file_bytes = file.read()
    
    try:
        # SUBIR EL ARCHIVO AL STORAGE DE SUPABASE
        # Lo subimos al bucket 'actas' que creaste
        supabase.storage.from_('actas').upload(
            path=nombre_archivo_final,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        print(f"Error al subir archivo: {e}")

try:
    # 2. GUARDAR LOS DATOS EN LA TABLA DE SUPABASE
    datos_registro = {
        "nombre_tutor": nombre_tutor,
        "apellido_tutor": apellido_tutor,
        "identificacion": identificacion,
        "telefono": telefono,
        "correo": correo,
        "nombre_nino": nombre_nino,
        "ano_nacimiento": ano_nacimiento,
        "edad_nino": edad_nino,
        "tiene_enfermedad": tiene_enfermedad,
        "detalles_enfermedad": detalles_enfermedad,
        "es_alergico": es_alergico,
        "detalles_alergia": detalles_alergia,
        "informacion_adicional": informacion_adicional,
        "nombre_archivo_final": nombre_archivo_final # Guardamos el nombre para saber cuál acta le pertenece
    }
    
    # Hacemos la inserción oficial en la nube
    supabase.table('registros').insert(datos_registro).execute()
    
    return "¡Registro guardado con éxito en Supabase!"

except Exception as e:
    return f"Hubo un error al guardar los datos: {e}"

# NUEVA RUTA: Muestra el formulario de login (Método GET) o procesa las credenciales (Método POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Definimos el usuario y contraseña del dueño aquí (Puedes cambiarlos por los que prefieras)
        if request.form['username'] == 'admin' and request.form['password'] == 'BlancaNieves2026':
            session['logueado'] = True  # Creamos el pase de entrada seguro
            return redirect(url_for('admin_panel'))
        else:
            error = 'Usuario o contraseña incorrectos. Intenta de nuevo.'
            
    return render_template('login.html', error=error)

# RUTA ACTUALIZADA: Ahora verifica si el pase existe antes de mostrar los niños
@app.route('/admin/')
@app.route('/admin')
def admin_panel():
    # SI NO ESTÁ LOGUEADO: Lo rebota inmediatamente a la pantalla de login por seguridad
    if not session.get('logueado'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM registros')
    datos = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', ninos=datos)

# NUEVA RUTA: Permite al dueño cerrar su sesión de forma segura
@app.route('/logout')
def logout():
    session.pop('logueado', None)  # Destruye el pase de entrada
    return redirect(url_for('login'))

    # NUEVA RUTA: Eliminar un registro específico por su ID
@app.route('/admin/eliminar/<int:id>')
def eliminar_registro(id):
    # SEGURIDAD: Si alguien intenta meterse a esta ruta sin loguearse, lo rebota
    if not session.get('logueado'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Ejecutamos la orden de eliminación usando el ID único del niño
    cursor.execute('DELETE FROM registros WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    # Una vez borrado, lo redirigimos de nuevo al panel para que vea la tabla actualizada
    return redirect(url_for('admin_panel'))

    # RUTA PARA SERVIR LOS ARCHIVOS DE LA CARPETA UPLOADS
@app.route('/uploads/<filename>')
def devuelve_archivo(filename):
    # Esto busca el archivo en la carpeta 'uploads' y lo manda al navegador de forma segura
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    
    

    
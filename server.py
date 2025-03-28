import io

import cv2
import easyocr
import numpy as np
from flask import Flask, jsonify, render_template, request, url_for
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError

app = Flask(
    __name__,
    static_folder='static',       # Carpeta donde están los JS/CSS del build
    template_folder='templates'   # Carpeta donde están los HTML generados
)

CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Cargar modelo OCR una vez
print("🔄 Cargando el modelo de EasyOCR...")
reader = easyocr.Reader(['es', 'la'], gpu=True)
print("✅ Modelo cargado correctamente.")

# 🔹 Página principal (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# 🔹 Otras páginas (si las tienes)
@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/testimonios')
def testimonios():
    return render_template('Testimonios.html')

@app.route('/traductor')
def traductor():
    return render_template('Traductor.html')

# 🔹 Ruta para recibir imágenes
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "⚠️ No se envió ninguna imagen."}), 400

        file = request.files['image']
        try:
            image = Image.open(io.BytesIO(file.read()))
        except UnidentifiedImageError:
            return jsonify({"error": "⚠️ Archivo de imagen inválido."}), 400

        print("📸 Aplicando OCR con EasyOCR...")
        result = reader.readtext(np.array(image))

        resultado = ' '.join([d[1] for d in result]).strip()
        print(f"✅ Texto detectado: {resultado}")
        return jsonify({"text": resultado})

    except Exception as e:
        print(f"⚠️ Error en el servidor: {e}")
        return jsonify({"error": "⚠️ Error procesando la imagen"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

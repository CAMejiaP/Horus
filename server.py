import base64
import io
import os
import re
import shutil
import tempfile
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from fpdf import FPDF
from PIL import Image, UnidentifiedImageError
from unstract.llmwhisperer import LLMWhispererClientV2
from unstract.llmwhisperer.client_v2 import LLMWhispererClientException

from backend.ejecutarDeteccion import ejecutarDeteccion

# 🔹 Cargar variables de entorno
load_dotenv()

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Página principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/testimonios')
def testimonios():
    return render_template('Testimonios.html')

@app.route('/traductor')
def traductor():
    return render_template('Traductor.html')

# 🔹 Procesamiento OCR usando LLMWhisperer
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "⚠️ No se envió ninguna imagen."}), 400

        file = request.files['image']

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
            file.save(temp_img.name)

            client = LLMWhispererClientV2(api_key=os.getenv("LLMWHISPERER_API_KEY"))
            print("📤 Enviando imagen a LLMWhisperer...")

            result = client.whisper(
                file_path=temp_img.name,
                wait_for_completion=True,
                wait_timeout=200,
                lang='spa'
            )

            print("📦 Resultado crudo:", result)

            texto_extraido = (
                result.get("result_text") or
                result.get("extraction", {}).get("result_text") or
                ""
            ).strip()

            # 🔹 Limpieza del texto extraído conservando caracteres Braille y especiales
            texto_extraido = re.sub(r'[ ]{2,}', ' ', texto_extraido)
            texto_extraido = re.sub(r'\s+\n', '\n', texto_extraido)
            texto_extraido = re.sub(r'\n\s+', '\n', texto_extraido)
            texto_extraido = texto_extraido.strip()

            print(f"🔍 Texto extraído: '{texto_extraido}'")

            return jsonify({"text": texto_extraido})

    except LLMWhispererClientException as e:
        print(f"❌ Error en API LLMWhisperer: {e}")
        return jsonify({"error": "❌ Error con la API LLMWhisperer"}), 500

    except Exception as e:
        print(f"⚠️ Error general: {e}")
        return jsonify({"error": "⚠️ Error procesando la imagen"}), 500

# 🔹 Generación de PDF usando fuente Segoe UI Symbol
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({"error": "No se recibió texto para generar el PDF"}), 400

    pdf = FPDF()
    pdf.add_page()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, 'static', 'fonts', 'SEGUISYM.TTF')

    # Verificación de existencia de la fuente
    if not os.path.exists(font_path):
        print(f"❌ Fuente no encontrada en: {font_path}")
    else:
        print(f"✅ Fuente encontrada en: {font_path}")
    
    pdf.add_font("SegoeUISymbol", "", font_path, uni=True)
    pdf.set_font("SegoeUISymbol", size=12)

    pdf.multi_cell(0, 5, text,align='J')

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        as_attachment=True,
        download_name='traduccion.pdf',
        mimetype='application/pdf'
    )

@app.route('/getbraille', methods=['POST'])
def getbrailletext():
    data = request.get_json()
    base64_original = data.get('image')
    base64_contrast = data.get('contrast_image')

    # Definir rutas temporales
    rutaImagen = "original_input.png"
    rutaImagenProcesada = "contrasted_input.png"
    nombreImagen = "input"

    # Función para guardar imagen desde base64
    def guardar_imagen_base64(data_base64, destino):
        if "," in data_base64:
            data_base64 = data_base64.split(",")[1]  # Remover encabezado data:image/...
        with open(destino, "wb") as f:
            f.write(base64.b64decode(data_base64))

    # Guardar las imágenes en disco
    guardar_imagen_base64(base64_original, rutaImagen)
    guardar_imagen_base64(base64_contrast, rutaImagenProcesada)

    # Ejecutar detección
    ejecutarDeteccion(rutaImagen, rutaImagenProcesada, nombreImagen)

    # Leer resultados
    texto_extraido = ""
    imagen_codificada = ""

    try:
        with open("runs/detect/predict/braille_text.txt", "r", encoding="utf-8") as f:
            texto_extraido = f.read()
    except FileNotFoundError:
        texto_extraido = "No se encontró el archivo de texto."

    try:
        with open("runs/detect/predict/output.png", "rb") as f:
            imagen_codificada = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        imagen_codificada = ""

    # Limpiar todo lo usado
    for path in [rutaImagen, rutaImagenProcesada]:
        if os.path.exists(path):
            os.remove(path)

    carpeta_runs = "runs"
    if os.path.exists(carpeta_runs):
        shutil.rmtree(carpeta_runs)

    # Devolver el texto y la imagen resultante
    return jsonify({
        "text": texto_extraido,
        "image": f"data:image/png;base64,{imagen_codificada}"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
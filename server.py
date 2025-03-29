import io
import os
import re
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

    font_path = Path("static/fonts/SEGUISYM.ttf")
    pdf.add_font("SegoeUISymbol", "", str(font_path))
    pdf.set_font("SegoeUISymbol", size=12)

    pdf.multi_cell(0, 5, text,align='J')

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        as_attachment=True,
        download_name='traduccion_braille.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
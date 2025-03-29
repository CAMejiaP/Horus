import io
import os

import numpy as np
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from fpdf import FPDF
from llmwhisperer_client import Client
from PIL import Image, UnidentifiedImageError

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializar cliente de LLMWhisperer con API Key
llm_client = Client(api_key=os.getenv("LLMWHISPERER_API_KEY"))

# ✩ Página principal
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

# ✩ Procesamiento OCR con LLMWhisperer
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "⚠️ No se envió ninguna imagen."}), 400

        file = request.files['image']
        file_bytes = file.read()

        print("📤 Enviando imagen a LLMWhisperer para OCR...")
        result = llm_client.ocr(file_bytes)
        texto = result.get('text', '').strip()

        print(f"✅ Texto detectado: {texto}")
        return jsonify({"text": texto})

    except Exception as e:
        print(f"⚠️ Error procesando la imagen con LLMWhisperer: {e}")
        return jsonify({"error": "⚠️ Error procesando la imagen"}), 500

# ✩ Generación de PDF con Braille
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    from pathlib import Path

    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({"error": "No se recibió texto para generar el PDF"}), 400

    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = Path("static/fonts/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", str(font_path))
    pdf.set_font("DejaVu", size=14)

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        as_attachment=True,
        download_name='traduccion_braille.pdf',
        mimetype='application/pdf'
    )

@app.route('/download_pdf_mirror', methods=['POST'])
def download_pdf_mirror():
    from pathlib import Path

    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({"error": "No se recibió texto para generar el PDF en espejo"}), 400

    mirrored_text = "\n".join([line[::-1] for line in text.splitlines()])

    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = Path("static/fonts/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", str(font_path))
    pdf.set_font("DejaVu", size=14)

    for line in mirrored_text.split('\n'):
        pdf.multi_cell(0, 10, line, align='R')

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        as_attachment=True,
        download_name='traduccion_braille_espejo.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)

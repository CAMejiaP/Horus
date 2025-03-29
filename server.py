import io

import cv2
import easyocr
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file, url_for
from flask_cors import CORS
from fpdf import FPDF
from PIL import Image, UnidentifiedImageError

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Cargar modelo OCR una vez
print("🔄 Cargando el modelo de EasyOCR...")
reader = easyocr.Reader(['es', 'la'], gpu=True)
print("✅ Modelo cargado correctamente.")

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

# 🔹 Procesamiento OCR
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "⚠️ No se envió ninguna imagen."}), 400

        file = request.files['image']
        file_bytes = file.read()
        file.stream.seek(0)

        try:
            image = Image.open(io.BytesIO(file_bytes))
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

# 🔹 Generación de PDF con Braille
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    from pathlib import Path

    from fpdf import FPDF

    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({"error": "No se recibió texto para generar el PDF"}), 400

    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ✅ Ruta corregida
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

    from fpdf import FPDF

    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({"error": "No se recibió texto para generar el PDF en espejo"}), 400

    # Invertir horizontalmente cada línea de texto
    mirrored_text = "\n".join([line[::-1] for line in text.splitlines()])

    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = Path("static/fonts/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", str(font_path))
    pdf.set_font("DejaVu", size=14)

    # 👉 Alineación a la derecha para efecto espejo completo
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

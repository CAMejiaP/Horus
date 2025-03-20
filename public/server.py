import io

import cv2
import easyocr
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Cargar el modelo OCR de EasyOCR solo una vez
print("🔄 Cargando el modelo de EasyOCR...")
reader = easyocr.Reader(['es','la'],gpu=True)  # Cargar español
print("✅ Modelo cargado correctamente.")

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

        # 🔹 Aplicar la lógica para extraer texto con bounding boxes
        resultado = ''
        for detection in result:
            text = detection[1]
            resultado += text + ' '
        
        resultado = resultado.strip()
        print(f"✅ Texto detectado:{resultado}")
        return jsonify({"text": resultado})

    except Exception as e:
        print(f"⚠️ Error en el servidor: {e}")
        return jsonify({"error": "⚠️ Error procesando la imagen"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
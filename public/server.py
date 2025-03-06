import io

import cv2
import numpy as np
import pytesseract

# 🔹 Cambia la ruta si es diferente en tu PC
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image, ImageEnhance, ImageFilter

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def preprocess_image(image):
    """ Preprocesa la imagen para mejorar la precisión del OCR """
    # Convertir a escala de grises
    image = image.convert("L")

    # Aumentar el contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # Aumentar contraste 2x

    # Convertir la imagen en array para aplicar filtros de OpenCV
    image_np = np.array(image)
    
    # Aplicar un filtro de reducción de ruido
    image_np = cv2.fastNlMeansDenoising(image_np, None, 30, 7, 21)
    
    # Aplicar binarización (umbral adaptativo)
    image_np = cv2.adaptiveThreshold(image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Convertir de nuevo a formato PIL
    processed_image = Image.fromarray(image_np)

    return processed_image

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        image = Image.open(io.BytesIO(file.read()))

        # Aplicar preprocesamiento
        processed_image = preprocess_image(image)

        # Aplicar OCR con un modo de segmentación mejorado
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(processed_image, config=custom_config, lang="eng")

        return jsonify({"text": extracted_text.strip()})

    except Exception as e:
        print(f"⚠️  Error en el servidor: {e}")
        return jsonify({"error": "Error procesando la imagen"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import io

import cv2
import easyocr
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image, ImageEnhance, UnidentifiedImageError

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔹 Cargar el modelo OCR de EasyOCR solo una vez
print("🔄 Cargando el modelo de EasyOCR...")
reader = easyocr.Reader(['en', 'es'])  # Cargar inglés y español
print("✅ Modelo cargado correctamente.")

def preprocess_image(image):
    """🔹 Mejora la calidad de la imagen para OCR."""
    image = image.convert('L')  # Escala de grises
    image = ImageEnhance.Contrast(image).enhance(2.0)  # Aumentar contraste
    image_np = np.array(image)
    image_np = cv2.fastNlMeansDenoising(image_np, None, 30, 7, 21)  # Reducción de ruido
    image_np = cv2.filter2D(image_np, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))  # Aumentar nitidez
    image_np = cv2.adaptiveThreshold(image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)  # Binarización
    return image_np  # Retornar imagen en escala de grises para EasyOCR

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "⚠️ No se envió ninguna imagen."}), 400

        file = request.files['image']
        
        try:
            image = Image.open(io.BytesIO(file.read())).convert('RGB')
        except UnidentifiedImageError:
            return jsonify({"error": "⚠️ Archivo de imagen inválido."}), 400

        print("🛠️ Aplicando preprocesamiento...")
        processed_image = preprocess_image(image)

        if processed_image is None:
            return jsonify({"error": "⚠️ Error en el procesamiento de la imagen."}), 500

        print("📸 Aplicando OCR con EasyOCR...")
        result = reader.readtext(processed_image)

        extracted_text = "\n".join([text for (bbox, text, prob) in result])

        print(f"✅ Texto detectado:\n{extracted_text}")
        return jsonify({"text": extracted_text.strip()})

    except Exception as e:
        print(f"⚠️ Error en el servidor: {e}")
        return jsonify({"error": "⚠️ Error procesando la imagen"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

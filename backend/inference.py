import os

import PIL
from ultralytics import YOLO

from .convert import convert_to_braille_unicode, parse_xywh_and_class


def load_model():
    """Carga el modelo YOLOv8 desde una ruta segura (absoluta)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "yolov8_braille.pt")
    return YOLO(model_path)


def load_image(image_path):
    """Carga imagen desde una ruta."""
    return PIL.Image.open(image_path)


def execute_inference(model, image_path):
    """Ejecuta la inferencia con el modelo y devuelve el texto Braille."""
    CONF = 0.15  # Nivel de confianza mínimo

    image = load_image(image_path)
    results = model.predict(image, save=True, save_txt=True, exist_ok=True, conf=CONF)
    boxes = results[0].boxes  # Resultado para la primera imagen

    list_boxes = parse_xywh_and_class(boxes)

    result = ""
    for box_line in list_boxes:
        str_left_to_right = ""
        box_classes = box_line[:, -1]
        for each_class in box_classes:
            str_left_to_right += convert_to_braille_unicode(model.names[int(each_class)])
        result += str_left_to_right + "\n"

    return result

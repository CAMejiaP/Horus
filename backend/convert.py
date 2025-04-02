import json
import os

import numpy as np
import torch

# Obtener ruta segura al JSON dentro del mismo paquete
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BRAILLE_MAP_PATH = os.path.join(CURRENT_DIR, "braille_map.json")

def convert_to_braille_unicode(str_input: str, path: str = BRAILLE_MAP_PATH) -> str:
    try:
        with open(path, "r", encoding="UTF-8") as fl:
            data = json.load(fl)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {path}")
        return "⠀"  # espacio en blanco Braille

    return data.get(str_input, "⠀")  # devuelve espacio si no encuentra clave


def parse_xywh_and_class(boxes: torch.Tensor) -> list:
    """
    Convierte los resultados YOLO en grupos por línea (y ordenados por x).
    """
    new_boxes = np.zeros(boxes.shape)
    new_boxes[:, :4] = boxes.xywh.numpy()  # xywh
    new_boxes[:, 4] = boxes.conf.numpy()   # confianza
    new_boxes[:, 5] = boxes.cls.numpy()    # clase

    new_boxes = new_boxes[new_boxes[:, 1].argsort()]  # ordenar por y
    y_threshold = np.mean(new_boxes[:, 3]) // 2
    boxes_diff = np.diff(new_boxes[:, 1])
    threshold_index = np.where(boxes_diff > y_threshold)[0]

    boxes_clustered = np.split(new_boxes, threshold_index + 1)
    boxes_return = []

    for cluster in boxes_clustered:
        cluster = cluster[cluster[:, 0].argsort()]  # ordenar por x
        boxes_return.append(cluster)

    return boxes_return

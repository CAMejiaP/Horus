import os
import shutil

from . import braille_detector_v2, inference


def ejecutarDeteccion(rutaImagen, rutaImagenProcesada, nombreImagen):
    # Limpiar carpeta runs si existe
    carpeta_runs = "runs"
    if os.path.exists(carpeta_runs):
        shutil.rmtree(carpeta_runs)

    # Cargar el modelo YOLO una vez
    model = inference.load_model()

    # Ejecutar inferencia (genera carpetas y labels)
    resultado_original = inference.execute_inference(model, rutaImagen)
    resultado_contraste = inference.execute_inference(model, rutaImagenProcesada)

    # Buscar archivos de etiquetas automáticamente
    labels_dir = "runs/detect/predict/labels"
    label_files = os.listdir(labels_dir)
    print("🗂 Archivos encontrados en labels/:", label_files)

    # Elegir el primero como referencia (puedes mejorar esto si sabés cuál es cuál)
    if len(label_files) >= 2:
        label_original = os.path.join(labels_dir, label_files[0])
        label_contraste = os.path.join(labels_dir, label_files[1])
    elif len(label_files) == 1:
        label_original = os.path.join(labels_dir, label_files[0])
        label_contraste = None
    else:
        raise FileNotFoundError("❌ No se encontraron archivos .txt en la carpeta de labels.")

    # Ejecutar PROCESSBRAILLE (original y contraste)
    braille_detector_v2.PROCESSBRAILLE(rutaImagenProcesada, label_original, False)

    if label_contraste:
        braille_detector_v2.PROCESSBRAILLE(rutaImagenProcesada, "runs/detect/predict/coordenadas_yolo.txt", True)

    # Guardar el resultado de texto final
    braille_text_path = "runs/detect/predict/braille_text.txt"
    with open(braille_text_path, "w", encoding="utf-8") as f:
        f.write(resultado_contraste)

from collections import Counter

import cv2
import numpy as np

# === CONFIGURATION ===
PURPLE = (255, 0, 255)         # Purple
BLUE = (255, 0, 0)             # Blue
YELLOW = (0, 255, 255)         # Yellow
GREEN = (0, 255, 0)            # Green
ORANGE = (0, 128, 255)         # Orange
RED = (0, 0, 255)              # Red
LINE_THICKNESS = 2

# === BRAILLE DICTIONARY ===
BRAILLE_DICT = {
    (0,0
    ,0,0
    ,0,0): "⠀",

    (1,0
    ,0,0
    ,0,0): "⠁",

    (1,0
    ,1,0
    ,0,0): "⠃",

    (1,1
    ,0,0
    ,0,0): "⠉",

    (1,1
    ,0,1
    ,0,0): "⠙",

    (1,0
    ,0,1
    ,0,0): "⠑",

    (1,1
    ,1,0
    ,0,0): "⠋",

    (1,1
    ,1,1
    ,0,0): "⠛",

    (1,0
    ,1,1
    ,0,0): "⠓",

    (0,1
    ,1,0
    ,0,0): "⠊",

    (0,1
    ,1,1
    ,0,0): "⠚",

    (0,1
    ,0,0
    ,0,0): "⠈",

    (0,1
    ,0,1
    ,0,0): "⠘",

    (0,0
    ,0,0
    ,1,0): "⠄",

    (1,0
    ,0,0
    ,1,0): "⠅",

    (1,0
    ,1,0
    ,1,0): "⠇",

    (1,1
    ,0,0
    ,1,0): "⠍",

    (1,1
    ,0,1
    ,1,0): "⠝",

    (1,0
    ,0,1
    ,1,0): "⠕",
    
    (1,1
    ,1,0
    ,1,0): "⠏",

    (1,1
    ,1,1
    ,1,0): "⠟",

    (1,0
    ,1,1
    ,1,0): "⠗",

    (0,1
    ,1,0
    ,1,0): "⠎",

    (0,1
    ,1,1
    ,1,0): "⠞",

    (0,1
    ,0,0
    ,1,0): "⠌",

    (0,1
    ,0,1
    ,1,0): "⠜",
    
    (0,0
    ,0,0
    ,1,1): "⠤",
    
    (1,0
    ,0,0
    ,1,1): "⠥",

    (1,0
    ,1,0
    ,1,1): "⠧",

    (1,1
    ,0,0
    ,1,1): "⠭",

    (1,1
    ,0,1
    ,1,1): "⠽",

    (1,0
    ,0,1
    ,1,1): "⠵",

    (1,1
    ,1,0
    ,1,1): "⠯",

    (1,1
    ,1,1
    ,1,1): "⠿",

    (1,0
    ,1,1
    ,1,1): "⠷",
    
    (0,1
    ,1,0
    ,1,1): "⠮",
    
    (0,1
    ,1,1
    ,1,1): "⠾",

    (0,1
    ,0,0
    ,1,1): "⠬",

    (0,1
    ,0,1
    ,1,1): "⠼",

    (0,0
    ,0,0
    ,0,1): "⠠",

    (1,0
    ,0,0
    ,0,1): "⠡",

    (1,0
    ,1,0
    ,0,1): "⠣",

    (1,1
    ,0,0
    ,0,1): "⠩",

    (1,1
    ,0,1
    ,0,1): "⠹",
    
    (1,0
    ,0,1
    ,0,1): "⠱",
    
    (1,1
    ,1,0
    ,0,1): "⠫",

    (1,1
    ,1,1
    ,0,1): "⠻",

    (1,0
    ,1,1
    ,0,1): "⠳",

    (0,1
    ,1,0
    ,0,1): "⠪",

    (0,1
    ,1,1
    ,0,1): "⠺",

    (0,1
    ,0,0
    ,0,1): "⠨",

    (0,1
    ,0,1
    ,0,1): "⠸",

    (0,0
    ,1,0
    ,0,0): "⠂",
    
    (0,0
    ,1,0
    ,1,0): "⠆",
    
    (0,0
    ,1,1
    ,0,0): "⠒",

    (0,0
    ,1,1
    ,0,1): "⠲",

    (0,0
    ,1,0
    ,0,1): "⠢",

    (0,0
    ,1,1
    ,1,0): "⠖",

    (0,0
    ,1,1
    ,1,1): "⠶",

    (0,0
    ,1,0
    ,1,1): "⠦",

    (0,0
    ,0,1
    ,1,0): "⠔",

    (0,0
    ,0,1
    ,1,1): "⠴",
    
    (0,0
    ,0,1
    ,0,0): "⠐",
    
    (0,0
    ,0,1
    ,0,1): "⠰",   
}

def load_coordinates(file_path):
    """Load YOLO format coordinates from a text file."""
    coords = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 5:
                _, x, y, w, h = map(float, parts)
                coords.append((x, y, w, h))
    return coords

def denormalize_coordinates(coords, width, height):
    """Convert normalized YOLO coordinates to pixel coordinates."""
    boxes = []
    for x, y, w, h in coords:
        x_pix = int((x - w / 2) * width)
        y_pix = int((y - h / 2) * height)
        w_pix = int(w * width)
        h_pix = int(h * height)
        boxes.append((x_pix, y_pix, w_pix, h_pix))
    return boxes

def group_by_lines(boxes, tolerance=12):
    """Group boxes into lines based on vertical position."""
    lines = []
    for box in sorted(boxes, key=lambda b: b[1]):
        added = False
        for line in lines:
            if abs(line[0][1] - box[1]) < tolerance:
                line.append(box)
                added = True
                break
        if not added:
            lines.append([box])
    return lines

def draw_blue_rectangles(img, lines, width):
    """Draw blue rectangles between purple boxes and to the right edge."""
    blue_rectangles = []
    
    for line in lines:
        line = sorted(line, key=lambda b: b[0])  # sort horizontally
        for i in range(len(line) - 1):
            x1, y1, w1, h1 = line[i]
            x2, y2, w2, h2 = line[i + 1]

            space = x2 - (x1 + w1)
            if space > 2:
                x_start = x1 + w1
                space_width = x2 - x_start
                y_top = min(y1, y2)
                height = max(y1 + h1, y2 + h2) - y_top
                cv2.rectangle(img, (x_start, y_top), (x_start + space_width, y_top + height), BLUE, 1)
                blue_rectangles.append((x_start, y_top, space_width, height))

        # space from last box to right edge
        x_last, y_last, w_last, h_last = line[-1]
        x_final = x_last + w_last
        final_space = width - x_final

        if final_space > 2:
            x_start = x_final
            space_width = final_space
            y_top = y_last
            height = h_last
            cv2.rectangle(img, (x_start, y_top), (x_start + space_width, y_top + height), BLUE, 1)
            blue_rectangles.append((x_start, y_top, space_width, height))
    
    return blue_rectangles

def detect_red_points(img, contours, purple_boxes, blue_rectangles):
    """Detect and mark red points that are in blue rectangles but not purple boxes."""
    red_points = []
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2

        in_purple = any(point_in_rectangle(cx, cy, r) for r in purple_boxes)
        in_blue = any(point_in_rectangle(cx, cy, r) for r in blue_rectangles)

        if in_blue and not in_purple:
            cv2.circle(img, (cx, cy), 2, RED, -1)
            red_points.append((cx, cy))
    
    return red_points

def point_in_rectangle(px, py, rectangle):
    """Check if a point is inside a rectangle."""
    x, y, w, h = rectangle
    return x <= px <= x + w and y <= py <= y + h

def group_points_by_lines(points, tolerance=20):
    """Group points into lines based on vertical position."""
    lines = []
    for px, py in sorted(points, key=lambda p: p[1]):
        added = False
        for line in lines:
            if abs(line[0][1] - py) < tolerance:
                line.append((px, py))
                added = True
                break
        if not added:
            lines.append([(px, py)])
    return lines

def group_horizontally(points, tolerance=30):
    """Group points horizontally based on x position."""
    groups = []
    for px, py in sorted(points, key=lambda p: p[0]):
        added = False
        for group in groups:
            if abs(group[-1][0] - px) < tolerance:
                group.append((px, py))
                added = True
                break
        if not added:
            groups.append([(px, py)])
    return groups

def calculate_average_spacing(purple_boxes):
    """Calculate average horizontal spacing between purple boxes."""
    spacings = []
    for line in group_by_lines(purple_boxes):
        line = sorted(line, key=lambda b: b[0])
        for i in range(len(line) - 1):
            x1, _, w1, _ = line[i]
            x2, _, _, _ = line[i + 1]
            space = x2 - (x1 + w1)
            if space > 0:
                spacings.append(space)
    
    # Filter reasonable spacings
    filtered = [d for d in spacings if 1 < d < 10]
    return Counter(filtered).most_common(1)[0][0] if filtered else 1

def rectangles_overlap(rect1, rect2):
    """Devuelve True si rect1 y rect2 se solapan (en 2D)."""
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or
                y1 + h1 <= y2 or y2 + h2 <= y1)

def point_in_rectangle(px, py, rect):
    """Devuelve True si el punto (px, py) está dentro del rectángulo (x, y, w, h)."""
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h

def draw_yellow_rectangles(img, red_points, purple_boxes, blue_rectangles, avg_width, avg_height, avg_spacing, width, height):
    """Dibuja recuadros amarillos alrededor de grupos de puntos rojos, evitando que su centro esté dentro de un recuadro púrpura."""
    yolo_coordinates = []
    
    for line in group_points_by_lines(red_points):
        groups = group_horizontally(line)
        for group in groups:
            xs = [p[0] for p in group]
            ys = [p[1] for p in group]
            cx = int(np.mean(xs))
            cy = int(np.mean(ys))

            for blue in blue_rectangles:
                ax, ay, aw, ah = blue
                if ax <= cx <= ax + aw and ay <= cy <= ay + ah:
                    new_x = max(ax, min(cx - avg_width // 2, ax + aw - avg_width))
                    new_y = max(ay, min(cy - avg_height // 2, ay + ah - avg_height))
                    x1, y1 = new_x, new_y
                    x2 = x1 + avg_width
                    y2 = y1 + avg_height

                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    # Verificar que el centro no esté dentro de un recuadro púrpura de la misma línea
                    same_line_purple = [r for r in purple_boxes if abs((r[1] + r[3] // 2) - center_y) < 15]
                    center_inside_morado = any(point_in_rectangle(center_x, center_y, r) for r in same_line_purple)
                    if center_inside_morado:
                        continue  # No dibujar si el centro cae dentro de un púrpura

                    # Posicionamiento basado en púrpura más cercano
                    left = [r for r in same_line_purple if r[0] + r[2] <= x1]
                    right = [r for r in same_line_purple if r[0] >= x2]
                    dist_left = min([abs(x1 - (r[0] + r[2])) for r in left], default=9999)
                    dist_right = min([abs(r[0] - x2) for r in right], default=9999)

                    if dist_left < dist_right and left:
                        nearest_left = max(left, key=lambda r: r[0] + r[2])
                        x1 = nearest_left[0] + nearest_left[2] + avg_spacing
                        color = (0, 255, 0)  # GREEN
                    elif dist_right < dist_left and right:
                        nearest_right = min(right, key=lambda r: r[0])
                        x1 = nearest_right[0] - avg_spacing - avg_width
                        color = (0, 128, 255)  # ORANGE
                    else:
                        color = (0, 255, 255)  # YELLOW

                    # Asegurar que se mantenga dentro del azul
                    x1 = max(ax, min(x1, ax + aw - avg_width))
                    x2 = x1 + avg_width

                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

                    x_center = (x1 + x2) / 2 / width
                    y_center = (y1 + y2) / 2 / height
                    w_norm = avg_width / width
                    h_norm = avg_height / height

                    yolo_coordinates.append((1, x_center, y_center, w_norm, h_norm, x1, y1))
                    break  # Solo usar un azul por grupo

    return yolo_coordinates

def detect_braille_binary(x1, y1, x2, y2, contours):
    """Detect braille pattern in a rectangle and return binary string."""
    w = x2 - x1
    h = y2 - y1
    dx = w / 2
    dy = h / 3

    cells = [
        (x1, y1, x1 + dx, y1 + dy),             # point 1
        (x1 + dx, y1, x2, y1 + dy),             # point 4
        (x1, y1 + dy, x1 + dx, y1 + 2 * dy),    # point 2
        (x1 + dx, y1 + dy, x2, y1 + 2 * dy),    # point 5
        (x1, y1 + 2 * dy, x1 + dx, y2),         # point 3
        (x1 + dx, y1 + 2 * dy, x2, y2)          # point 6
    ]

    bits = ['0'] * 6
    for cnt in contours:
        x, y, w_c, h_c = cv2.boundingRect(cnt)
        cx, cy = x + w_c // 2, y + h_c // 2
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            for idx, (cx1, cy1, cx2, cy2) in enumerate(cells):
                if cx1 <= cx <= cx2 and cy1 <= cy <= cy2:
                    bits[idx] = '1'
                    break
    return ''.join(bits)

def process_braille_to_text(binary_result):
    """Convert binary braille patterns to text using the dictionary."""
    lines = binary_result.strip().split('\n')
    final_result = []
    finalest_result = []
    
    for line in lines:
        binaries_str = line.strip().split()
        binaries_tuples = [tuple(int(b) for b in group) for group in binaries_str]
        braille_line = ' '.join(BRAILLE_DICT.get(tuple, '?') for tuple in binaries_tuples)
        final_result.append(braille_line)
        
    for line in final_result:
        new_line = line.replace("⠨ ", "⠨")
        finalest_result.append(new_line)
    
    return '\n'.join(finalest_result)

def remove_overlapping_duplicates(yolo_coords, width, height, iou_threshold=0.3):
    """Elimina coordenadas solapadas significativamente."""
    unique = []
    for i, (cls_i, x_i, y_i, w_i, h_i, x_pix_i, y_pix_i) in enumerate(yolo_coords):
        box_i = (
            int((x_i - w_i / 2) * width),
            int((y_i - h_i / 2) * height),
            int(w_i * width),
            int(h_i * height)
        )

        is_duplicate = False
        for cls_j, x_j, y_j, w_j, h_j, x_pix_j, y_pix_j in unique:
            box_j = (
                int((x_j - w_j / 2) * width),
                int((y_j - h_j / 2) * height),
                int(w_j * width),
                int(h_j * height)
            )
            if is_overlapping(box_i, box_j, iou_threshold):
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append((cls_i, x_i, y_i, w_i, h_i, x_pix_i, y_pix_i))
    
    return unique

def is_overlapping(box1, box2, threshold=0.3):
    """Check if box1 overlaps with box2 above a certain threshold (IoU)."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Calcular coordenadas del área de intersección
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)

    inter_width = max(0, xi2 - xi1)
    inter_height = max(0, yi2 - yi1)
    inter_area = inter_width * inter_height

    # Área de la unión
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area

    # IoU (Intersection over Union)
    iou = inter_area / union_area if union_area > 0 else 0
    return iou > threshold

def PROCESSBRAILLE(image_path, coords_path, saveImage):

    IMAGE_PATH = image_path
    COORDS_PATH = coords_path

    # Load and process image
    img = cv2.imread(IMAGE_PATH)
    height, width = img.shape[:2]
    
    # Load and denormalize coordinates
    norm_coords = load_coordinates(COORDS_PATH)
    pixel_coords = denormalize_coordinates(norm_coords, width, height)
    
    # Initialize YOLO coordinates list with purple boxes
    yolo_coordinates = []
    for (x, y, w, h) in pixel_coords:
        x_center = (x + w / 2) / width
        y_center = (y + h / 2) / height
        w_norm = w / width
        h_norm = h / height
        yolo_coordinates.append((0, x_center, y_center, w_norm, h_norm, x, y))
    
    # Draw purple rectangles
    for (x, y, w, h) in pixel_coords:
        cv2.rectangle(img, (x, y), (x + w, y + h), PURPLE, LINE_THICKNESS)
    
    # Group by lines and draw blue rectangles
    lines = group_by_lines(pixel_coords)
    blue_rectangles = draw_blue_rectangles(img, lines, width)
    
    # Detect red points (in blue but not purple)
    img_original = cv2.imread(IMAGE_PATH)
    gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    red_points = detect_red_points(img, contours, pixel_coords, blue_rectangles)
    
    # Calculate average dimensions and spacing
    avg_width = int(np.median([w for _, _, w, _ in pixel_coords]))
    avg_height = int(np.median([h for _, _, _, h in pixel_coords]))
    avg_spacing = calculate_average_spacing(pixel_coords)
    
    # Draw yellow rectangles around red points
    yellow_yolo = draw_yellow_rectangles(img, red_points, pixel_coords, blue_rectangles, 
                                       avg_width, avg_height, avg_spacing, width, height)
    yolo_coordinates.extend(yellow_yolo)
    
   # Eliminar duplicados por solapamiento
    yolo_coordinates = remove_overlapping_duplicates(yolo_coordinates, width, height)

    # Ordenar por fila y columna
    yolo_coordinates.sort(key=lambda c: (round(c[2] * height), round(c[1] * width)))

    # Guardar en archivo
    with open("runs\detect\predict\coordenadas_yolo.txt", "w") as file:
        for cls, x_center, y_center, w_norm, h_norm, _, _ in yolo_coordinates:
            file.write(f"{cls} {x_center:.7f} {y_center:.7f} {w_norm:.7f} {h_norm:.7f}\n")
    
    # Process braille detection
    purple_boxes = [(x, y, x + w, y + h) for (x, y, w, h) in pixel_coords]
    yellow_boxes = [(x, y, x + avg_width, y + avg_height) 
                   for cls, _, _, _, _, x, y in yolo_coordinates if cls == 1]
    all_boxes = purple_boxes + yellow_boxes
    
    # Group boxes by lines
    box_lines = []
    for line in group_by_lines([(x1, y1, x2-x1, y2-y1) for (x1, y1, x2, y2) in all_boxes]):
        line = sorted(line, key=lambda b: b[0])
        box_lines.append([(x, y, x + w, y + h) for (x, y, w, h) in line])
    
    # Generate binary braille result
    binary_result = ""
    for line in box_lines:
        for x1, y1, x2, y2 in line:
            binary = detect_braille_binary(x1, y1, x2, y2, contours)
            binary_result += binary + " "
        binary_result = binary_result.rstrip() + "\n"
    
    


    if (saveImage):
            # Convert to text and save to file
        braille_text = process_braille_to_text(binary_result)
        with open("runs\detect\predict\\braille_text.txt", "w",encoding="utf-8") as f:
            f.write(braille_text)
        
        save_path = "runs\detect\predict\\output.png"
        cv2.imwrite(save_path, img)
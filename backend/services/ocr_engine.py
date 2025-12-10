import cv2
import pytesseract
import numpy as np

def extract_text_from_image(image_path: str):
    # 1. Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "No se pudo leer el archivo."}

    # Factor de escalado
    SCALE_FACTOR = 2.0 

    # --- ESCALADO (V2) ---
    # Guardamos las dimensiones originales para referencia si hiciera falta
    # original_h, original_w = img.shape[:2]
    
    # Ampliamos la imagen x2
    img_scaled = cv2.resize(img, None, fx=SCALE_FACTOR, fy=SCALE_FACTOR, interpolation=cv2.INTER_CUBIC)

    # 2. Pre-procesamiento sobre la imagen ESCALADA
    gray = cv2.cvtColor(img_scaled, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 31, 2)

    # 3. Configuración Tesseract
    custom_config = r'--oem 3 --psm 11'

    # 4. Extraer datos (Las coordenadas vendrán multiplicadas por 2)
    data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)

    detected_blocks = []
    n_boxes = len(data['text'])

    for i in range(n_boxes):
# ... dentro del for i in range(n_boxes): ...
        text = data['text'][i].strip()
        conf = int(data['conf'][i])
        
        # Calculamos el área (ancho x alto) para ignorar "moscas" o ruido pequeño
        w_temp = int(data['width'][i] / SCALE_FACTOR)
        h_temp = int(data['height'][i] / SCALE_FACTOR)
        area = w_temp * h_temp

        # --- FILTRO DE PROTECCIÓN DE ARTE ---
        # 1. Confianza: Subimos de 20 a 40 (para no borrar arrugas de caras).
        # 2. Área: Ignoramos cosas menores a 200px (manchitas pequeñas).
        # 3. Longitud: Ignoramos textos de 1 o 2 letras (suelen ser fallos).
        if conf > 40 and area > 200 and len(text) > 2:
            
            # ... (cálculo de coordenadas x,y,w,h igual que antes) ...
            x = int(data['left'][i] / SCALE_FACTOR)
            y = int(data['top'][i] / SCALE_FACTOR)
            w = w_temp
            h = h_temp

            detected_blocks.append({
                "text": text,
                "confidence": conf,
                "box": {
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h
                }
            })

    return {
        "total_blocks": len(detected_blocks),
        "text_content": [b['text'] for b in detected_blocks],
        "detailed_blocks": detected_blocks
    }
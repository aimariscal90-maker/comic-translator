import cv2
import pytesseract
import numpy as np

def extract_text_from_image(image_path: str):
    # 1. Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "No se pudo leer el archivo."}

    # --- MEJORA V2: ESCALADO ---
    # Aumentamos la imagen x2 para que Tesseract vea las letras más grandes.
    # Esto es CRÍTICO para cómics y textos pequeños.
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 2. Pre-procesamiento
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicamos un desenfoque muy suave para quitar el ruido del papel/dibujo
    gray = cv2.medianBlur(gray, 3)

    # Thresholding Adaptativo (Mejor para cómics que el Otsu simple)
    # Se adapta si hay sombras o fondos no uniformes en los bocadillos
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 31, 2)

    # 3. Configuración Tesseract
    # --psm 6: Asume un bloque de texto uniforme (a veces funciona mejor tras escalar)
    # Si falla, volvemos a --psm 11 (texto disperso)
    custom_config = r'--oem 3 --psm 11'

    # 4. Extraer
    data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)

    detected_blocks = []
    n_boxes = len(data['text'])

    for i in range(n_boxes):
        text = data['text'][i].strip()
        conf = int(data['conf'][i])
        
        # Subimos un poco la exigencia de confianza y longitud
        if conf > 40 and len(text) > 2:
            detected_blocks.append({
                "text": text,
                "confidence": conf,
                "box": data['left'][i] # Simplificamos el output por ahora
            })

    return {
        "total_blocks": len(detected_blocks),
        "text_content": [b['text'] for b in detected_blocks]
    }
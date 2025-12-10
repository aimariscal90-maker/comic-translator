from paddleocr import PaddleOCR
import numpy as np
import cv2

# Inicializamos el motor
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')

def detect_text(image_bytes):
    """
    Detecta texto en una imagen. Versión Robusta con Debug.
    """
    # 1. Preparar imagen
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Ejecutar IA
    raw_result = ocr_engine.ocr(img)
    
    # --- ZONA DE DEBUG ---
    # Esto imprimirá en tu terminal la estructura real para que no adivinemos
    print(f"\n🔍 DEBUG RAW OCR: {raw_result}\n")
    
    detections = []
    
    # Si no detecta nada, devolvemos lista vacía
    if not raw_result:
        return []

    # 3. Normalizar la estructura (El truco "Todoterreno")
    # Paddle a veces devuelve [ [Línea1, Línea2] ] y a veces [Línea1, Línea2]
    # Vamos a buscar la lista de líneas correcta.
    
    lines_list = []
    
    # Caso A: Estructura anidada estándar (List -> Page -> Lines)
    if isinstance(raw_result[0], list) and len(raw_result[0]) > 0 and isinstance(raw_result[0][0], list):
        lines_list = raw_result[0]
    # Caso B: Estructura plana (List -> Lines)
    elif isinstance(raw_result, list):
        lines_list = raw_result
        
    # 4. Procesar las líneas
    for line in lines_list:
        # Una línea válida debe ser una lista/tupla con 2 elementos: [Coords, (Texto, Confianza)]
        if not isinstance(line, (list, tuple)) or len(line) != 2:
            continue
            
        coords = line[0]
        content = line[1]
        
        # Validar contenido
        text = ""
        confidence = 0.0
        
        if isinstance(content, (list, tuple)) and len(content) == 2:
            text = content[0]
            confidence = content[1]
        elif isinstance(content, str):
            text = content
            confidence = 0.99

        detections.append({
            "text": text,
            "bbox": coords,
            "confidence": confidence
        })
            
    return detections
import cv2
import numpy as np
from backend.services.ocr_engine import extract_text_from_image

def clean_image_text(image_path: str, output_path: str):
    """
    Detecta el texto, crea una máscara unificada y lo borra.
    """
    # 1. Obtener coordenadas (ya corregidas con el factor de escala del Día 2)
    ocr_result = extract_text_from_image(image_path)
    
    if "error" in ocr_result:
        return {"error": ocr_result["error"]}
    
    blocks = ocr_result.get("detailed_blocks", [])
    if not blocks:
        return {"warning": "No se detectó texto para borrar."}

    # 2. Cargar imagen original
    img = cv2.imread(image_path)
    
    # 3. Crear máscara inicial (negra)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    # 4. Dibujar rectángulos blancos FUERTES sobre las letras
    for block in blocks:
        box = block['box']
        x, y, w, h = box['x'], box['y'], box['w'], box['h']
        
        # Dibujamos el rectángulo
        cv2.rectangle(mask, (x, y), (x + w, y + h), (255), thickness=-1)

    # --- LA MEJORA DEL DÍA 3 (Fusión de Bloques) ---
    # Usamos "Dilatación" para expandir los rectángulos blancos.
    # Esto hace que las letras cercanas se fusionen en una sola mancha grande.
    # Así el borrador no deja "ruido" entre letras.
    kernel = np.ones((15, 15), np.uint8)  # Un pincel cuadrado de 15x15 píxeles
    mask = cv2.dilate(mask, kernel, iterations=4)
    # 5. Aplicar Inpainting (Borrador Mágico)
    # Radius 5: Toma más contexto de alrededor para rellenar
    cleaned_img = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

    # 6. Guardar
    cv2.imwrite(output_path, cleaned_img)

    return {
        "status": "success",
        "cleaned_file": output_path,
        "blocks_removed": len(blocks)
    }
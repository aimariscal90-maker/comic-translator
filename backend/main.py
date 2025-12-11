
# --- IMPORTS ---
import shutil
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# Importamos tus 3 motores:
from backend.services.ocr_engine import extract_text_from_image
from backend.services.cleaner_engine import clean_image_text
from backend.services.translator_engine import translate_text_blocks

app = FastAPI(
    title="Comic Translator API",
    description="Backend para traducir cómics con IA",
    version="0.4.0" # ¡Subimos versión por el Día 2!
)

app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

# Carpeta temporal para guardar imágenes subidas
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Día 2: Sistema de visión activado."
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- NUEVO ENDPOINT DEL DÍA 2 ---
@app.post("/api/v1/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Sube una imagen (página de cómic), procésala y extrae el texto.
    """
    # 1. Guardar el archivo temporalmente en el disco
    temp_filename = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Llamar a nuestro motor de OCR (el cerebro)
        result = extract_text_from_image(temp_filename)
        
        return {
            "filename": file.filename,
            "ocr_result": result
        }
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        # 3. Limpieza: Borrar el archivo temporal (Opcional, pero recomendado)
        # os.remove(temp_filename) 
        pass

# --- NUEVO ENDPOINT DÍA 3: LIMPIEZA ---
@app.post("/api/v1/clean-image")
async def clean_image(file: UploadFile = File(...)):
    # 1. Guardar imagen original
    temp_filename = f"{UPLOAD_DIR}/{file.filename}"
    clean_filename = f"{UPLOAD_DIR}/clean_{file.filename}"
    
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Ejecutar el borrador
        result = clean_image_text(temp_filename, clean_filename)
        
        if "error" in result:
            return {"error": result["error"]}

        # 3. Devolver la imagen limpia directamente para verla en el navegador
        return FileResponse(clean_filename)
    
    except Exception as e:
        return {"error": str(e)}
    
# --- NUEVO ENDPOINT DÍA 4: EL FLUJO COMPLETO ---
@app.post("/api/v1/translate-page")
async def translate_page(file: UploadFile = File(...)):
    """
    1. Sube imagen.
    2. Detecta texto (OCR).
    3. Traduce texto (AI).
    4. Devuelve JSON con Coordenadas + Original + Traducción.
    """
    temp_filename = f"{UPLOAD_DIR}/{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # PASO 1: OCR (Ojos)
        ocr_result = extract_text_from_image(temp_filename)
        
        if "error" in ocr_result:
            return {"error": ocr_result["error"]}

        # Preparamos la lista para la IA
        original_texts = ocr_result.get("text_content", [])
        detailed_blocks = ocr_result.get("detailed_blocks", [])

        # PASO 2: Traducción (Cerebro)
        if original_texts:
            print(f"Traduciendo {len(original_texts)} bloques...")
            translated_texts = translate_text_blocks(original_texts)
        else:
            translated_texts = []

        # PASO 3: Fusión de datos
        # Unimos: Dónde está (box) + Qué decía (original) + Qué dirá (translated)
        final_data = []
        for i, block in enumerate(detailed_blocks):
            # Seguridad de índices
            tr_text = translated_texts[i] if i < len(translated_texts) else block["text"]
            
            final_data.append({
                "id": i,
                "box": block["box"], # x, y, w, h
                "original": block["text"],
                "translated": tr_text
            })

        return {
            "status": "success",
            "filename": file.filename,
            "blocks": final_data
        }

    except Exception as e:
        return {"error": str(e)}
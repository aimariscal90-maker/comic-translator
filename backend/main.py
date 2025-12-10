import shutil
import os
from fastapi import FastAPI, File, UploadFile
from backend.services.ocr_engine import extract_text_from_image # Importamos nuestro motor
# Añade este import arriba del todo
from fastapi.responses import FileResponse
from backend.services.cleaner_engine import clean_image_text

app = FastAPI(
    title="Comic Translator API",
    description="Backend para traducir cómics con IA",
    version="0.2.0" # ¡Subimos versión por el Día 2!
)

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
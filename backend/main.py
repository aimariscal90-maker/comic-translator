from fastapi import FastAPI

# Inicializamos la aplicación
app = FastAPI(
    title="Comic Translator API",
    description="Backend para traducir cómics con IA",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Endpoint de prueba para ver si el servidor respira."""
    return {
        "status": "online",
        "platform": "GitHub Codespaces 🚀",
        "message": "Bienvenido al Día 1. El motor está en marcha."
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
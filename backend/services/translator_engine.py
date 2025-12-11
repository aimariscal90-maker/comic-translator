import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Inicializamos el cliente. Si no hay KEY, fallará amablemente.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def translate_text_blocks(text_list: list, target_lang="Spanish"):
    """
    Recibe una lista de textos en inglés y devuelve sus traducciones.
    Usa GPT-4o-mini para ser rápido y barato.
    """
    # 1. Si no hay API Key, devolvemos un "Mock" (Simulacro) para no romper la app
    if not client:
        return [f"[MOCK] {t}" for t in text_list]
    
    if not text_list:
        return []

    # 2. El Prompt del Sistema (La personalidad de la IA)
    system_prompt = (
        f"You are a professional comic book translator translating from English to {target_lang}. "
        "Tone: Gritty, noir, natural dialogue. "
        "IMPORTANT: Return ONLY a raw JSON array of strings. No markdown formatting. "
        "Maintain the exact same number of elements as the input list."
    )

    # 3. Empaquetamos el texto para enviarlo
    user_content = json.dumps(text_list)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3, # Baja creatividad para fidelidad
        )

        # 4. Procesar respuesta
        raw_content = response.choices[0].message.content
        # Limpieza de seguridad por si GPT mete ```json al principio
        clean_content = raw_content.replace("```json", "").replace("```", "").strip()
        
        translated_list = json.loads(clean_content)
        return translated_list

    except Exception as e:
        print(f"Error OpenAI: {e}")
        # En caso de error, devolvemos el texto original con marca de error
        return [f"[ERR] {t}" for t in text_list]
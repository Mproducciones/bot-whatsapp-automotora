"""
Test simple para verificar la conexión con Groq API
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
print(f"API Key encontrada: {'SÍ' if GROQ_API_KEY else 'NO'}")
print(f"Longitud: {len(GROQ_API_KEY)}")

if GROQ_API_KEY:
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": "Hola, cómo estás?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7,
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            )
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Groq funciona: {data['choices'][0]['message']['content']}")
            else:
                print(f"❌ Error: {resp.status_code} - {resp.text}")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
else:
    print("❌ No se encontró API Key")

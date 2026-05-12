"""
Chat interactivo simplificado para debugging
"""
import os
import httpx
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Inventario simplificado
INVENTARIO = [
    {"Marca":"Dodge","Modelo":"Journey","Año":2017,"Combustible":"Bencina","Kilometraje":150000,"Precio":5990000,"Stock":1,"Tipo":"SUV","Origen":"Propio"},
    {"Marca":"Geely","Modelo":"LC","Año":2012,"Combustible":"Bencina","Kilometraje":128997,"Precio":3390000,"Stock":1,"Tipo":"Hatchback","Origen":"Propio"},
    {"Marca":"Toyota","Modelo":"Yaris","Año":2007,"Combustible":"Bencina","Kilometraje":45000,"Precio":3850000,"Stock":1,"Tipo":"Hatchback","Origen":"Propio"},
    {"Marca":"Suzuki","Modelo":"Swift","Año":2019,"Combustible":"Bencina","Kilometraje":85000,"Precio":4290000,"Stock":1,"Tipo":"Hatchback","Origen":"Consignación","Dueño":"Cliente-001"},
    {"Marca":"Hyundai","Modelo":"Tucson","Año":2018,"Combustible":"Bencina","Kilometraje":95000,"Precio":8500000,"Stock":1,"Tipo":"SUV","Origen":"Consignación","Dueño":"Cliente-002"},
]

class ChatRequest(BaseModel):
    mensaje: str
    conversation_id: str = ""
    historial: list = []

def buscar_autos(consulta: str) -> str:
    """Búsqueda simplificada."""
    q = consulta.lower()
    resultados = []
    
    for auto in INVENTARIO:
        if auto["Stock"] <= 0:
            continue
            
        score = 0
        if auto["Marca"].lower() in q:
            score += 3
        if auto["Modelo"].lower() in q:
            score += 2
        if auto["Tipo"].lower() in q:
            score += 2
        
        if score > 0:
            resultados.append({"auto": auto, "score": score})
    
    resultados.sort(key=lambda x: x["score"], reverse=True)
    
    if not resultados:
        return "No encontré vehículos que coincidan con tu búsqueda."
    
    lineas = []
    for auto in [r["auto"] for r in resultados[:3]]:
        precio = f"${int(auto['Precio']):,}".replace(",",".") 
        km = f"{int(auto['Kilometraje']):,} kms".replace(",",".") 
        origen = auto.get('Origen', 'Propio')
        if origen == 'Consignación':
            lineas.append(f"• {auto['Marca']} {auto['Modelo']} {auto.get('Año','')} | {auto.get('Combustible','')} | {km} | {precio} 🏷️")
        else:
            lineas.append(f"• {auto['Marca']} {auto['Modelo']} {auto.get('Año','')} | {auto.get('Combustible','')} | {km} | {precio}")
    
    return "Vehículos que coinciden:\n" + "\n".join(lineas)

async def consultar_groq(mensaje: str, historial: list) -> str:
    """Llama a Groq API con historial simplificado."""
    if not GROQ_API_KEY:
        return "Por favor contáctanos directamente al +56 9 8808 3279 🙏"

    # Preparar mensajes para la API
    mensajes = [
        {"role": "system", "content": """Eres Valentina, asesora de ventas de la Automotora Marco Yáñez Langer. Responde de forma natural y amigable. Los vehículos con 🏷️ están en consignación."""}
    ]
    
    # Agregar historial limitado
    mensajes.extend(historial[-3:])  # Solo últimos 3 mensajes
    mensajes.append({"role": "user", "content": mensaje})
    
    payload = {
        "model": GROQ_MODEL,
        "messages": mensajes,
        "max_tokens": 300,
        "temperature": 0.7,
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return "Estoy con mucho trabajo en este momento 😅"
        return "Tuve un problema técnico. Por favor intenta más tarde."
    except Exception as e:
        return "Tuve un problema técnico. Por favor intenta más tarde."

app = FastAPI(title="Chat Simple - Marco Yáñez Langer")

@app.get("/")
async def chat_interface():
    """Interfaz web simplificada para chatear"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat con Valentina - Marco Yáñez Langer</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
        .chat-box { height: 400px; border: 1px solid #ddd; padding: 20px; overflow-y: auto; margin: 20px 0; background: #fafafa; }
        .message { margin: 10px 0; padding: 10px; border-radius: 10px; max-width: 80%; }
        .user { background: #007bff; color: white; margin-left: auto; text-align: right; }
        .bot { background: #28a745; color: white; }
        .input-area { display: flex; padding: 20px; background: #f8f9fa; border-radius: 0 0 10px 10px; }
        #messageInput { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-right: 10px; }
        #sendButton { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        #sendButton:hover { background: #0056b3; }
        .info { text-align: center; color: #666; margin: 10px 0; }
        .typing { color: #666; font-style: italic; margin: 5px 0; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Chat con Valentina</h1>
            <p>Asesora de Ventas - Marco Yáñez Langer</p>
            <div class="info">📍 Av. Libertador O'Higgins 0214, Rancagua | 📱 +56 9 8808 3279</div>
        </div>
        
        <div id="chatBox" class="chat-box">
            <div class="message bot">
                ¡Hola! Soy Valentina, tu asesora virtual de Marco Yáñez Langer 😊<br><br>
                Estoy aquí para ayudarte a encontrar el vehículo perfecto para ti.<br><br>
                ¿Qué tipo de auto estás buscando?<br><br>
                ¡Estoy para servirte! 🚗
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Escribe tu mensaje aquí..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendButton">Enviar</button>
        </div>
        
        <div class="info">
            💬 Mantén una conversación natural
        </div>
    </div>

    <script>
        let conversationId = 'test-' + Math.random().toString(36).substr(2, 9);
        let messageHistory = [];
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function addMessage(content, isUser = false) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function addError(content) {
            const chatBox = document.getElementById('chatBox');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.innerHTML = content;
            chatBox.appendChild(errorDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function showTyping() {
            const chatBox = document.getElementById('chatBox');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing';
            typingDiv.id = 'typing';
            typingDiv.textContent = 'Valentina está escribiendo...';
            chatBox.appendChild(typingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function hideTyping() {
            const typingDiv = document.getElementById('typing');
            if (typingDiv) {
                typingDiv.remove();
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Agregar mensaje del usuario
            addMessage(message, true);
            messageHistory.push({role: 'user', content: message});
            input.value = '';
            
            // Mostrar indicador de escritura
            showTyping();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        mensaje: message,
                        conversation_id: conversationId,
                        historial: messageHistory
                    })
                });
                
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                // Ocultar indicador de escritura
                hideTyping();
                
                // Agregar respuesta del bot
                if (data.error) {
                    addError('Error: ' + data.respuesta);
                } else {
                    addMessage(data.respuesta, false);
                    messageHistory.push({role: 'assistant', content: data.respuesta});
                }
                
            } catch (error) {
                hideTyping();
                console.error('Error en sendMessage:', error);
                addError('Lo siento, tuve un problema técnico. Por favor recarga la página y vuelve a intentar. 😊');
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Endpoint simplificado para procesar mensajes del chat"""
    try:
        print(f"Mensaje recibido: {request.mensaje}")
        print(f"Conversation ID: {request.conversation_id}")
        print(f"Historial: {request.historial}")
        
        # Buscar información relevante para el contexto
        stock_context = ""
        if any(palabra in request.mensaje.lower() for palabra in ["auto", "vehiculo", "suv", "camioneta", "sedan", "hatchback"]):
            stock_context = buscar_autos(request.mensaje)
        
        respuesta = await consultar_groq(request.mensaje, request.historial[-3:] if len(request.historial) > 0 else [])
        
        return {
            "respuesta": respuesta,
            "conversation_id": request.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "stock_info": stock_context if stock_context else None
        }
    except Exception as e:
        print(f"Error en chat_endpoint: {e}")
        return {
            "respuesta": f"Error técnico: {str(e)}",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

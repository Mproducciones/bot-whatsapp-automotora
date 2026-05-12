"""
Chat interactivo para mantener conversación continua con el bot
"""
import os
import httpx
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Inventario (mismo que el sistema principal)
INVENTARIO = [
    {"Marca":"Dodge","Modelo":"Journey","Año":2017,"Combustible":"Bencina","Kilometraje":150000,"Precio":5990000,"Stock":1,"Tipo":"SUV","Origen":"Propio"},
    {"Marca":"Geely","Modelo":"LC","Año":2012,"Combustible":"Bencina","Kilometraje":128997,"Precio":3390000,"Stock":1,"Tipo":"Hatchback","Origen":"Propio"},
    {"Marca":"Toyota","Modelo":"Yaris","Año":2007,"Combustible":"Bencina","Kilometraje":45000,"Precio":3850000,"Stock":1,"Tipo":"Hatchback","Origen":"Propio"},
    {"Marca":"Ford","Modelo":"Ecosport","Año":2007,"Combustible":"Bencina","Kilometraje":75000,"Precio":3990000,"Stock":1,"Tipo":"SUV","Origen":"Propio"},
    {"Marca":"Chevrolet","Modelo":"Spark","Año":2011,"Combustible":"Bencina","Kilometraje":62000,"Precio":4690000,"Stock":1,"Tipo":"Hatchback","Origen":"Propio"},
    {"Marca":"Peugeot","Modelo":"407","Año":2008,"Combustible":"Bencina","Kilometraje":196686,"Precio":4790000,"Stock":1,"Tipo":"Sedán","Origen":"Propio"},
    {"Marca":"ZNA","Modelo":"Oting","Año":2014,"Combustible":"Bencina","Kilometraje":125000,"Precio":4990000,"Stock":1,"Tipo":"SUV","Origen":"Propio"},
    {"Marca":"JAC","Modelo":"Trip-J6","Año":2015,"Combustible":"Bencina","Kilometraje":179269,"Precio":5390000,"Stock":1,"Tipo":"Furgón","Origen":"Propio"},
    {"Marca":"Jeep","Modelo":"Cherokee","Año":2007,"Combustible":"Bencina","Kilometraje":150000,"Precio":5890000,"Stock":1,"Tipo":"SUV","Origen":"Propio"},
    {"Marca":"Suzuki","Modelo":"Swift","Año":2019,"Combustible":"Bencina","Kilometraje":85000,"Precio":4290000,"Stock":1,"Tipo":"Hatchback","Origen":"Consignación","Dueño":"Cliente-001"},
    {"Marca":"Hyundai","Modelo":"Tucson","Año":2018,"Combustible":"Bencina","Kilometraje":95000,"Precio":8500000,"Stock":1,"Tipo":"SUV","Origen":"Consignación","Dueño":"Cliente-002"},
    {"Marca":"Nissan","Modelo":"Sentra","Año":2020,"Combustible":"Bencina","Kilometraje":45000,"Precio":7200000,"Stock":1,"Tipo":"Sedán","Origen":"Consignación","Dueño":"Cliente-003"},
]

def buscar_autos(consulta: str, max_resultados: int = 3) -> str:
    """Búsqueda simplificada sin pandas."""
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
        if auto["Combustible"].lower() in q:
            score += 1
        
        if score > 0:
            resultados.append({"auto": auto, "score": score})
    
    resultados.sort(key=lambda x: x["score"], reverse=True)
    
    if not resultados:
        disponibles = [a for a in INVENTARIO if a["Stock"] > 0][:max_resultados]
        prefijo = "No encontré exactamente lo que buscas, pero tenemos estos disponibles:\n"
    else:
        disponibles = [r["auto"] for r in resultados[:max_resultados]]
        prefijo = "Vehículos en stock que coinciden:\n"
    
    if not disponibles:
        return "Sin stock disponible en este momento."
    
    lineas = []
    for auto in disponibles:
        precio = f"${int(auto['Precio']):,}".replace(",",".") 
        km = f"{int(auto['Kilometraje']):,} kms".replace(",",".") 
        origen = auto.get('Origen', 'Propio')
        if origen == 'Consignación':
            lineas.append(f"• {auto['Marca']} {auto['Modelo']} {auto.get('Año','')} | {auto.get('Combustible','')} | {km} | {precio} 🏷️")
        else:
            lineas.append(f"• {auto['Marca']} {auto['Modelo']} {auto.get('Año','')} | {auto.get('Combustible','')} | {km} | {precio}")
    
    return prefijo + "\n".join(lineas)

async def consultar_groq_conversacion(mensaje: str, historial: list) -> str:
    """Llama a Groq API manteniendo el historial de conversación."""
    if not GROQ_API_KEY:
        return "Por favor contáctanos directamente al +56 9 8808 3279 🙏"

    # Preparar el historial para la API
    mensajes = [
        {"role": "system", "content": f"""Eres Valentina, asesora de ventas de la Automotora Marco Yáñez Langer, ubicada en Av. Libertador Bernardo O'Higgins 0214, Rancagua, Chile. Llevamos más de 53 años en el rubro. Lema: "Mi única meta es tu sonrisa."

Reglas:
1. Español chileno natural, cálido, para WhatsApp. Máximo 3-4 párrafos cortos.
2. Ayuda a encontrar el vehículo según el stock disponible.
3. Los vehículos marcados con 🏷️ están en consignación (dueños particulares vendiendo a través nuestra).
4. Si alguien quiere vender su auto, ofrecer servicio de consignación online.
5. Invita a visitar: Lunes-Viernes 09:30-19:30 hrs.
6. Crédito automotriz: 1 año antigüedad laboral, renta mínima $350.000, buen informe comercial.
7. NO inventes precios ni datos que no están en el stock.
8. Si no hay stock del auto buscado, ofrece alternativas similares.
9. Emojis con moderación (máximo 2 por mensaje).
10. Contacto: 📱 +56 9 8808 3279 | 🌐 automotorarancagua.com

SERVICIO DE CONSIGNACIÓN:
- Vendemos tu auto por ti sin estrés
- Máximo valor de venta vs venta directa
- Nos encargamos de toda la documentación
- Publicación en todas nuestras plataformas
- Solo pagas comisión cuando vendemos

Mantén una conversación natural y fluida. Recuerda lo que hemos hablado antes."""}
    ]
    
    # Agregar el historial de conversación
    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": mensaje})
    
    payload = {
        "model": GROQ_MODEL,
        "messages": mensajes,
        "max_tokens": 400,
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
            return "Estoy con mucho trabajo en este momento 😅 Llámanos al +56 9 8808 3279 y te atendemos de inmediato."
        return "Tuve un problema técnico. Contáctanos al +56 9 8808 3279 😊"
    except Exception as e:
        return "Tuve un problema técnico. Contáctanos al +56 9 8808 3279 😊"

app = FastAPI(title="Chat Interactivo - Marco Yáñez Langer")

# Almacenamiento de conversaciones activas
conversaciones_activas = {}

@app.get("/")
async def chat_interface():
    """Interfaz web para chatear con el bot"""
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
                ¿Qué tipo de auto estás buscando? ¿O quizás quieres vender tu auto a través de nuestro servicio de consignación?<br><br>
                ¡Estoy para servirte! 🚗
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Escribe tu mensaje aquí..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendButton">Enviar</button>
        </div>
        
        <div class="info">
            💬 Mantén una conversación natural - Recuerdo lo que hablamos
        </div>
    </div>

    <script>
        let conversationId = Math.random().toString(36).substr(2, 9);
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
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Ocultar indicador de escritura
                hideTyping();
                
                // Agregar respuesta del bot
                if (data.error) {
                    addMessage('Error: ' + data.respuesta, false);
                } else {
                    addMessage(data.respuesta, false);
                    messageHistory.push({role: 'assistant', content: data.respuesta});
                }
                
            } catch (error) {
                hideTyping();
                console.error('Error en sendMessage:', error);
                addMessage('Lo siento, tuve un problema técnico. Por favor recarga la página y vuelve a intentar. 😊', false);
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat_endpoint(request):
    """Endpoint para procesar mensajes del chat interactivo"""
    try:
        body = await request.json()
        
        # Validación explícita de los campos requeridos
        if not body:
            return {
                "respuesta": "Por favor envía un mensaje válido.",
                "error": "No se recibieron datos"
            }
        
        mensaje = body.get("mensaje", "")
        if not mensaje or not mensaje.strip():
            return {
                "respuesta": "Por favor escribe un mensaje.",
                "error": "Mensaje vacío"
            }
        
        conversation_id = body.get("conversation_id", "")
        historial = body.get("historial", [])
        
        # Asegurar que historial sea una lista
        if not isinstance(historial, list):
            historial = []
        
        # Buscar información relevante para el contexto
        stock_context = ""
        if any(palabra in mensaje.lower() for palabra in ["auto", "vehiculo", "suv", "camioneta", "sedan", "hatchback"]):
            stock_context = buscar_autos(mensaje)
        
        respuesta = await consultar_groq_conversacion(mensaje, historial[-5:] if len(historial) > 0 else [])
        
        return {
            "respuesta": respuesta,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "stock_info": stock_context if stock_context else None
        }
    except Exception as e:
        return {
            "respuesta": "Lo siento, tuve un problema técnico. Por favor intenta de nuevo.",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

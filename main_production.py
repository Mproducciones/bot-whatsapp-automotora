"""
Versión de producción optimizada para Vercel con IA real
"""
import os
import logging
import httpx
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# ─── Configuración ────────────────────────────────────────────────────────────
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EVOLUTION_URL   = os.getenv("EVOLUTION_URL", "")
EVOLUTION_TOKEN = os.getenv("EVOLUTION_TOKEN", "")
EVOLUTION_INST  = os.getenv("EVOLUTION_INSTANCE", "yanez-langer")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="Agente Ventas - Marco Yáñez Langer")

# ─── INVENTARIO ────────────────────────────────────────────────────────────────

INVENTARIO_DEMO = [
    {"Marca":"Toyota","Modelo":"Yaris","Año":2020,"Combustible":"Gasolina","Kilometraje":45000,"Precio":8990000,"Stock":1,"Tipo":"Sedán"},
    {"Marca":"Suzuki","Modelo":"Swift","Año":2019,"Combustible":"Gasolina","Kilometraje":62000,"Precio":6490000,"Stock":1,"Tipo":"Hatchback"},
    {"Marca":"Chevrolet","Modelo":"Captiva","Año":2018,"Combustible":"Diesel","Kilometraje":88000,"Precio":9800000,"Stock":1,"Tipo":"SUV"},
    {"Marca":"Hyundai","Modelo":"Tucson","Año":2021,"Combustible":"Gasolina","Kilometraje":31000,"Precio":13500000,"Stock":1,"Tipo":"SUV"},
    {"Marca":"Ford","Modelo":"Ranger","Año":2019,"Combustible":"Diesel","Kilometraje":75000,"Precio":14990000,"Stock":2,"Tipo":"Camioneta"},
]

def buscar_autos_simplificado(consulta: str, max_resultados: int = 3) -> str:
    """Búsqueda simplificada sin pandas."""
    q = consulta.lower()
    resultados = []
    
    for auto in INVENTARIO_DEMO:
        if auto["Stock"] <= 0:
            continue
            
        score = 0
        # Buscar por marca
        if auto["Marca"].lower() in q:
            score += 3
        # Buscar por modelo
        if auto["Modelo"].lower() in q:
            score += 2
        # Buscar por tipo
        if auto["Tipo"].lower() in q:
            score += 2
        # Buscar por combustible
        if auto["Combustible"].lower() in q:
            score += 1
        
        if score > 0:
            resultados.append({"auto": auto, "score": score})
    
    # Ordenar por score
    resultados.sort(key=lambda x: x["score"], reverse=True)
    
    if not resultados:
        # Si no hay resultados, mostrar disponibles
        disponibles = [a for a in INVENTARIO_DEMO if a["Stock"] > 0][:max_resultados]
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
        lineas.append(f"• {auto['Marca']} {auto['Modelo']} {auto.get('Año','')} | {auto.get('Combustible','')} | {km} | {precio}")
    
    return prefijo + "\n".join(lineas)

# ─── MÓDULO DE IA (Groq) ──────────────────────────────────────────────────────

async def consultar_groq(mensaje: str, stock_context: str) -> str:
    """Llama a Groq API con Llama 3.3 70B (gratis, sin tarjeta)."""
    if not GROQ_API_KEY:
        log.error("GROQ_API_KEY no configurada.")
        return "Por favor contáctanos directamente al +56 9 8808 3279 🙏"

    system_prompt = f"""Eres Valentina, asesora de ventas de la Automotora Marco Yáñez Langer, ubicada en Av. Libertador Bernardo O'Higgins 0214, Rancagua, Chile. Llevamos más de 53 años en el rubro. Lema: "Mi única meta es tu sonrisa."

Reglas:
1. Español chileno natural, cálido, para WhatsApp. Máximo 3-4 párrafos cortos.
2. Ayuda a encontrar el vehículo según el stock disponible.
3. Invita a visitar: Lunes-Viernes 09:30-19:30 hrs.
4. Crédito automotriz: 1 año antigüedad laboral, renta mínima $350.000, buen informe comercial.
5. NO inventes precios ni datos que no están en el stock.
6. Si no hay stock del auto buscado, ofrece alternativas similares.
7. Emojis con moderación (máximo 2 por mensaje).
8. Contacto: 📱 +56 9 8808 3279 | 🌐 automotorarancagua.com

STOCK DISPONIBLE:
{stock_context}"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
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
        log.error(f"Groq {e.response.status_code}: {e.response.text[:200]}")
        if e.response.status_code == 429:
            return "Estoy con mucho trabajo en este momento 😅 Llámanos al +56 9 8808 3279 y te atendemos de inmediato."
        return "Tuve un problema técnico. Contáctanos al +56 9 8808 3279 😊"
    except Exception as e:
        log.error(f"Error Groq: {e}")
        return "Tuve un problema técnico. Contáctanos al +56 9 8808 3279 😊"

# ─── SISTEMA DE PROTECCIÓN Y TRACKING ────────────────────────────────────────

class SistemaProteccion:
    def __init__(self):
        # Almacenamiento en memoria para serverless
        self.conversaciones = {}
        self.ventas_atribuidas = {}
        self.alertas_fraude = []
    
    def generar_codigo_seguimiento(self, numero_cliente):
        codigo = f"BOT-{abs(hash(numero_cliente)) % 10000:04d}"
        return codigo
    
    def registrar_conversacion(self, numero_cliente, mensaje_cliente, respuesta_bot):
        conv_id = str(uuid.uuid4())
        codigo = self.generar_codigo_seguimiento(numero_cliente)
        
        self.conversaciones[conv_id] = {
            "id": conv_id,
            "numero_cliente": numero_cliente,
            "mensaje_cliente": mensaje_cliente,
            "respuesta_bot": respuesta_bot,
            "timestamp": datetime.now(),
            "codigo_seguimiento": codigo,
            "estado": "activa",
            "atribucion_venta": None
        }
        
        return conv_id, codigo
    
    def atribuir_venta(self, numero_cliente, monto_venta, fecha_venta, evidencias=None):
        # Buscar conversaciones del cliente
        conversaciones_cliente = [
            conv for conv in self.conversaciones.values() 
            if conv["numero_cliente"] == numero_cliente
        ]
        
        if not conversaciones_cliente:
            return {"atribuible": False, "motivo": "sin_conversacion_previa"}
        
        # Calcular confianza de atribución
        confianza = self.calcular_confianza_atribucion(conversaciones_cliente, evidencias)
        
        if confianza >= 0.7:
            venta_id = str(uuid.uuid4())
            comision = monto_venta * 0.07  # 7% comisión estándar
            
            venta_data = {
                "id": venta_id,
                "numero_cliente": numero_cliente,
                "monto_venta": monto_venta,
                "fecha_venta": fecha_venta,
                "comision": comision,
                "confianza": confianza,
                "evidencias": evidencias or {},
                "timestamp_atribucion": datetime.now(),
                "hash_seguridad": self.generar_hash_seguridad(venta_id, monto_venta)
            }
            
            self.ventas_atribuidas[venta_id] = venta_data
            
            # Marcar conversación como convertida
            for conv in conversaciones_cliente:
                conv["atribucion_venta"] = venta_id
            
            return {
                "atribuible": True,
                "venta_id": venta_id,
                "comision": comision,
                "confianza": confianza
            }
        
        return {"atribuible": False, "confianza": confianza}
    
    def calcular_confianza_atribucion(self, conversaciones, evidencias):
        confianza = 0.0
        
        # Tiempo desde última conversación
        ultima_conv = max(conv["timestamp"] for conv in conversaciones)
        tiempo_venta = datetime.now() - ultima_conv
        
        if tiempo_venta.days <= 7:  # Dentro de 7 días
            confianza += 0.4
        elif tiempo_venta.days <= 30:
            confianza += 0.2
        
        # Evidencias adicionales
        if evidencias:
            if evidencias.get("codigo_mencionado"):
                confianza += 0.3
            if evidencias.get("testimonio_cliente"):
                confianza += 0.2
            if evidencias.get("crm_integration"):
                confianza += 0.25
            if evidencias.get("intencion_compra"):
                confianza += 0.15
        
        return min(confianza, 1.0)
    
    def generar_hash_seguridad(self, venta_id, monto_venta):
        datos = f"{venta_id}_{monto_venta}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.sha256(datos.encode()).hexdigest()[:16]
    
    def generar_dashboard_cliente(self, cliente_id):
        ventas_cliente = [
            v for v in self.ventas_atribuidas.values()
        ]
        
        conversaciones_cliente = [
            c for c in self.conversaciones.values()
        ]
        
        total_ventas = sum(v["monto_venta"] for v in ventas_cliente)
        total_comisiones = sum(v["comision"] for v in ventas_cliente)
        
        return {
            "cliente_id": cliente_id,
            "periodo": datetime.now().strftime("%Y-%m"),
            "conversaciones_totales": len(conversaciones_cliente),
            "ventas_atribuidas": len(ventas_cliente),
            "monto_total_ventas": total_ventas,
            "comisiones_generadas": total_comisiones,
            "tasa_conversion": len(ventas_cliente) / max(len(conversaciones_cliente), 1) * 100,
            "promedio_confianza": sum(v["confianza"] for v in ventas_cliente) / max(len(ventas_cliente), 1),
            "alertas_activas": 0,
            "roi_calculado": (total_ventas * 0.07) / max(total_comisiones, 1) * 100
        }

# Instancia global del sistema de protección
sistema_proteccion = SistemaProteccion()

# ─── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"estado": "activo", "agente": "Valentina - Marco Yáñez Langer", "ia": GROQ_MODEL, "groq_configured": bool(GROQ_API_KEY)}

@app.post("/test")
async def test_agente(request: Request):
    """Prueba el agente sin WhatsApp. Enviar JSON: {"mensaje": "busco una SUV"}"""
    try:
        body = await request.json()
        texto = body.get("mensaje", "Hola, qué autos tienen?")
        stock = buscar_autos_simplificado(texto)
        respuesta = await consultar_groq(texto, stock)
        
        # Registrar conversación de prueba
        conv_id, codigo = sistema_proteccion.registrar_conversacion("+56912345678", texto, respuesta)
        
        return {
            "mensaje": texto, 
            "stock": stock, 
            "respuesta": respuesta,
            "conversacion_id": conv_id,
            "codigo_seguimiento": codigo
        }
    except Exception as e:
        log.error(f"Error en /test: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/atribuir_venta")
async def atribuir_venta(request: Request):
    """Atribuir una venta al bot."""
    try:
        body = await request.json()
        
        numero_cliente = body.get("numero_cliente")
        monto_venta = body.get("monto_venta")
        fecha_venta = body.get("fecha_venta", datetime.now().strftime("%Y-%m-%d"))
        evidencias = body.get("evidencias", {})
        
        if not numero_cliente or not monto_venta:
            raise HTTPException(status_code=400, detail="numero_cliente y monto_venta son requeridos")
        
        resultado = sistema_proteccion.atribuir_venta(numero_cliente, monto_venta, fecha_venta, evidencias)
        
        return JSONResponse(resultado)
    except Exception as e:
        log.error(f"Error en /atribuir_venta: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/dashboard_admin")
async def dashboard_admin():
    """Dashboard de administración para todos los clientes."""
    try:
        total_conversaciones = len(sistema_proteccion.conversaciones)
        total_ventas = len(sistema_proteccion.ventas_atribuidas)
        total_comisiones = sum(v["comision"] for v in sistema_proteccion.ventas_atribuidas.values())
        total_ventas_monto = sum(v["monto_venta"] for v in sistema_proteccion.ventas_atribuidas.values())
        
        return JSONResponse({
            "resumen_global": {
                "conversaciones_totales": total_conversaciones,
                "ventas_atribuidas": total_ventas,
                "monto_total_ventas": total_ventas_monto,
                "comisiones_generadas": total_comisiones,
                "tasa_conversion_global": (total_ventas / max(total_conversaciones, 1)) * 100,
                "alertas_fraude_activas": len(sistema_proteccion.alertas_fraude),
                "backup_registros": 0
            },
            "ventas_recientes": [
                {
                    "id": v["id"],
                    "numero_cliente": v["numero_cliente"],
                    "monto_venta": v["monto_venta"],
                    "comision": v["comision"],
                    "confianza": v["confianza"],
                    "fecha_venta": v["fecha_venta"]
                }
                for v in list(sistema_proteccion.ventas_atribuidas.values())[-10:]
            ],
            "alertas_fraude": sistema_proteccion.alertas_fraude[-5:]  # Últimas 5 alertas
        })
    except Exception as e:
        log.error(f"Error en /dashboard_admin: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

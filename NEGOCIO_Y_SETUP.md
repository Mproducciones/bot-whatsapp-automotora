# 🚗 Agente de Ventas WhatsApp — Marco Yáñez Langer
## Guía completa: tecnología + modelo de negocio

---

## 💡 LA IDEA DE NEGOCIO (Inversión $0)

### El problema que resuelves
Las automotoras pierden clientes fuera del horario de atención. Alguien escribe a las 11 PM preguntando por una camioneta y al día siguiente ya compró en otra parte. Un agente de WhatsApp atiende 24/7, filtra el stock real, y agenda visitas automáticamente.

### El modelo
**Fase 1 — Prueba de concepto (hoy, costo $0)**
Tú mismo instalas esto en Marco Yáñez Langer. Si funciona, tienes un caso de estudio real.

**Fase 2 — Servicio a otras automotoras (~$5/mes por cliente)**
Cada automotora de la Región de O'Higgins, Metropolitana y del resto del país necesita esto. Les cobras una mensualidad y tú pagas el hosting con su plata.

**Fase 3 — Escalar (~$30-100/mes por cliente)**
Con 10 clientes cubres todos los costos y empiezas a ganar. Con 50 clientes tienes un negocio de $1.500.000-5.000.000/mes.

---

## 🆓 STACK COMPLETAMENTE GRATUITO

| Componente | Servicio | Costo | Límite gratis |
|---|---|---|---|
| Backend (FastAPI) | Railway | $5/mes* | ~suficiente para 1 cliente |
| IA (Llama 3.3 70B) | Groq API | **$0** | 500.000 tokens/día, 14.400 req/día |
| Inventario | Google Sheets | **$0** | ilimitado |
| WhatsApp | Evolution API en Railway | $5/mes* | ilimitado |
| Dominio HTTPS | Railway (incluido) | **$0** | incluido |

*Railway cobra $5/mes pero incluye $5 de crédito de uso → en la práctica $0 si el tráfico es bajo.

**Total mes 1: $0 — $5 máximo**

---

## 🚀 IMPLEMENTACIÓN PASO A PASO

### Paso 1: Groq API (5 minutos, gratis)
1. Ve a https://console.groq.com
2. Regístrate con Google
3. API Keys → Create Key
4. Copia la key (empieza con `gsk_...`)

### Paso 2: Railway — Backend FastAPI (10 minutos)
1. Ve a https://railway.app
2. Regístrate con GitHub
3. New Project → Deploy from GitHub repo
4. Sube tu código (o usa GitHub para subir esta carpeta)
5. En Variables de entorno agrega:
   - `GROQ_API_KEY` = tu key de Groq
   - `GROQ_MODEL` = llama-3.3-70b-versatile
6. Railway te da una URL tipo `https://tu-app.up.railway.app`

### Paso 3: Evolution API en Railway (15 minutos)
1. En Railway → New Service → Deploy template
2. Busca "Evolution API" → Deploy
3. En variables agrega: `AUTHENTICATION_API_KEY=un_token_secreto`
4. Anota la URL del servicio
5. Ve a `https://tu-evolution.railway.app/manager` 
6. Crea una instancia → escanea el QR con el WhatsApp de la automotora

### Paso 4: Google Sheets como inventario (5 minutos)
1. Crea una Google Sheet con estas columnas:
   `Marca | Modelo | Año | Combustible | Kilometraje | Precio | Stock | Tipo`
2. Ingresa el stock real de la automotora
3. Archivo → Compartir → Publicar en la web → Hoja → CSV → Publicar
4. Copia la URL y ponla en `GSHEETS_CSV_URL`

### Paso 5: Conectar webhook (5 minutos)
En Evolution API, en tu instancia:
- Webhook URL: `https://tu-fastapi.railway.app/webhook`
- Eventos: `messages.upsert` ✓

### Paso 6: Probar sin WhatsApp
```bash
curl -X POST https://tu-app.railway.app/test \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "tienen camionetas diesel?"}'
```

---

## 📈 MODELO DE ESCALAMIENTO

### Con 1 cliente (Marco Yáñez Langer):
- Costo mensual: ~$5 USD = ~$4.800 CLP
- Cobro sugerido: $50.000-80.000 CLP/mes
- **Ganancia neta: $45.000-75.000 CLP/mes**

### Con 10 clientes (automotoras de la región):
- Costo mensual: ~$50-80 USD (~$48.000-77.000 CLP)
- Ingreso: $500.000-800.000 CLP/mes
- **Ganancia neta: ~$420.000-750.000 CLP/mes**

### Con 50 clientes (nacional):
- Costo: ~$200-400 USD/mes → un VPS propio ya conviene
- Ingreso: $2.500.000-4.000.000 CLP/mes
- **Ganancia neta: $2.000.000-3.700.000 CLP/mes**

### Cómo conseguir los primeros clientes:
1. **Marco Yáñez Langer** primero → caso de éxito gratis
2. Fotografía conversaciones reales del bot → muéstralas en LinkedIn/Instagram
3. Busca en Google Maps "automotora Rancagua", "automotora Talca", etc.
4. Envíales un demo por WhatsApp: "Hola, soy X, monté un agente de IA para automotoras..."
5. Precio de entrada: $0 el primer mes, $50.000 desde el segundo

---

## ⚙️ ROADMAP TÉCNICO (de $0 a pago)

**Hoy (gratis):**
- ✅ Responde consultas de stock
- ✅ Detecta tipo de vehículo, precio, combustible
- ✅ Agenda visitas (el bot pregunta horario)
- ✅ Inventario en Google Sheets (la automotora lo actualiza sola)

**Con $20.000 CLP/mes (VPS básico):**
- Conversaciones con memoria (el bot recuerda el hilo)
- Múltiples automotoras en el mismo servidor
- Panel web para ver conversaciones

**Con $50.000 CLP/mes:**
- CRM básico: guarda leads con nombre, teléfono, auto de interés
- Notificación al vendedor cuando hay un cliente caliente
- Estadísticas de consultas

---

## 📞 Datos reales de la automotora
- Dirección: Av. Libertador B. O'Higgins 0214, Rancagua
- San Martín 665 y 709, Rancagua
- Teléfono: +56 9 8808 3279
- Email: rancaguaautomotora@gmail.com / marco@yanezlanger.cl
- Web: automotorarancagua.com
- Horario: Lunes-Viernes 09:30-19:30 hrs

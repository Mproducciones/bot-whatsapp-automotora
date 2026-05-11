# 🚀 Guía de Despliegue Rápido - Sistema Multi-Escenario

## 📋 Opción 1: Vercel (Recomendado para inicio)

### Paso 1: Preparar Variables de Entorno
```bash
# Copiar .env.example a .env.local
cp .env.example .env.local

# Configurar variables mínimas
GROQ_API_KEY=tu_key_groq
GROQ_MODEL=llama-3.3-70b-versatile
```

### Paso 2: Instalar Vercel CLI
```bash
npm i -g vercel
```

### Paso 3: Despliegue
```bash
# En la carpeta del proyecto
vercel --prod

# Seguir instrucciones:
# - Conectar cuenta GitHub
# - Confirmar configuración
# - Obtener URL del deployment
```

### Paso 4: Probar Sistema
```bash
# Test básico
curl -X POST https://tu-app.vercel.app/test \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "busco una SUV diesel"}'

# Ver dashboard
curl https://tu-app.vercel.app/dashboard_admin
```

## 📋 Opción 2: Railway (Para producción completa)

### Paso 1: Crear cuenta en Railway
- Visitar https://railway.app
- Registrarse con GitHub
- Nuevo proyecto → GitHub repo

### Paso 2: Configurar Variables
En Railway → Variables de entorno:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
EVOLUTION_URL=https://tu-evolution.railway.app
EVOLUTION_TOKEN=tu_token_secreto
EVOLUTION_INSTANCE=yanez-langer
GSHEETS_CSV_URL=https://docs.google.com/spreadsheets/d/TU_ID/pub?output=csv
```

### Paso 3: Configurar Evolution API
1. Nuevo servicio → Deploy template → Evolution API
2. Variable: AUTHENTICATION_API_KEY=un_token_secreto
3. Escanear QR con WhatsApp business

### Paso 4: Configurar Webhook
En Evolution API → Webhook URL:
```
https://tu-fastapi.railway.app/webhook
```

## 🎯 Primeras Pruebas

### Test 1: Conversación Simulada
```bash
curl -X POST https://tu-app/test \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "tienes camionetas diesel?"}'
```

### Test 2: Atribución de Venta
```bash
curl -X POST https://tu-app/atribuir_venta \
  -H "Content-Type: application/json" \
  -d '{
    "numero_cliente": "+56912345678",
    "monto_venta": 9800000,
    "fecha_venta": "2024-01-15",
    "evidencias": {"codigo_mencionado": true}
  }'
```

### Test 3: Dashboard
```bash
# Ver estadísticas globales
curl https://tu-app/estadisticas_globales

# Ver dashboard admin
curl https://tu-app/dashboard_admin
```

## 📊 Flujo Completo de Prueba

1. **Enviar mensaje de prueba** → Recibir código BOT-1234
2. **Atribuir venta manualmente** → Ver comisión calculada
3. **Ver dashboard** → Confirmar tracking
4. **Probar detección de fraude** → Simular alertas

## 🔧 Configuración de WhatsApp (Opcional)

### Para producción real:
1. Evolution API en Railway
2. Escanear QR con WhatsApp Business
3. Configurar webhook a tu app
4. Probar con mensajes reales

### Para desarrollo:
- Usar endpoint `/test` sin WhatsApp
- Simular conversaciones manualmente
- Probar atribución de ventas

## 📈 Monitoreo y Métricas

### Endpoints clave:
- `/dashboard_admin` → Vista global
- `/estadisticas_globales` → KPIs del sistema
- `/ventas_atribuidas` → Ventas registradas
- `/detectar_fraude` → Análisis de comportamiento

### Alertas automáticas:
- Caída de ventas atribuidas
- Bot inactivo con ventas humanas
- Múltiples ventas sin código

## 🎯 Escenarios de Uso

### Escenario 1: Venta Directa
- Cliente paga $X millones por sistema completo
- Recibe acceso a todos los endpoints
- Administra sus propias comisiones

### Escenario 2: Administración
- Instalación gratuita
- Tú controlas dashboards
- Recibes 7% de comisiones

### Escenario 3: Híbrido
- Pago inicial + mensualidad
- Compartes administración
- Control total del sistema

## 🛡️ Seguridad y Protección

- **Cada conversación** tiene ID único y timestamp
- **Cada venta** requiere múltiples evidencias
- **Cada comisión** tiene hash de seguridad
- **Backup automático** de todos los datos

## 📞 Soporte

Para problemas técnicos:
1. Verificar logs en Vercel/Railway
2. Confirmar variables de entorno
3. Probar con endpoint `/test`
4. Revisar dashboard de alertas

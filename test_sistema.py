#!/usr/bin/env python3
"""
Script de prueba completo para el sistema de bot WhatsApp
Ejecuta: python test_sistema.py
"""

import requests
import json
import time
from datetime import datetime

# Configuración (cambiar por tu URL de despliegue)
BASE_URL = "http://localhost:8000"  # Cambiar a tu URL de Vercel/Railway

def test_conversacion():
    """Test 1: Probar conversación del bot"""
    print("🤖 Test 1: Probando conversación del bot...")
    
    payload = {"mensaje": "busco una SUV diesel para trabajo"}
    
    try:
        response = requests.post(f"{BASE_URL}/test", json=payload)
        data = response.json()
        
        print(f"✅ Conversación exitosa:")
        print(f"   Mensaje: {data['mensaje']}")
        print(f"   Respuesta: {data['respuesta'][:100]}...")
        print(f"   Código seguimiento: {data['codigo_seguimiento']}")
        print(f"   Conversación ID: {data['conversacion_id']}")
        
        return data['conversacion_id'], data['codigo_seguimiento']
        
    except Exception as e:
        print(f"❌ Error en conversación: {e}")
        return None, None

def test_atribucion_venta(conversacion_id, codigo):
    """Test 2: Atribuir venta al bot"""
    print("\n💰 Test 2: Probando atribución de venta...")
    
    payload = {
        "numero_cliente": "+56912345678",
        "monto_venta": 9800000,
        "fecha_venta": "2024-01-15",
        "evidencias": {
            "codigo_mencionado": True,
            "testimonio_cliente": True,
            "intencion_compra": True
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/atribuir_venta", json=payload)
        data = response.json()
        
        if data.get('atribuible'):
            print(f"✅ Venta atribuida exitosamente:")
            print(f"   Venta ID: {data['venta_id']}")
            print(f"   Comisión: ${data['comision']:,.0f}")
            print(f"   Confianza: {data['confianza']:.1%}")
            return data['venta_id']
        else:
            print(f"❌ Venta no atribuible: {data.get('motivo', 'Confianza baja')}")
            return None
            
    except Exception as e:
        print(f"❌ Error en atribución: {e}")
        return None

def test_dashboard_admin():
    """Test 3: Ver dashboard administrativo"""
    print("\n📊 Test 3: Probando dashboard admin...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard_admin")
        data = response.json()
        
        print("✅ Dashboard admin:")
        resumen = data['resumen_global']
        print(f"   Conversaciones totales: {resumen['conversaciones_totales']}")
        print(f"   Ventas atribuidas: {resumen['ventas_atribuidas']}")
        print(f"   Comisiones generadas: ${resumen['comisiones_generadas']:,.0f}")
        print(f"   Tasa conversión: {resumen['tasa_conversion_global']:.1f}%")
        print(f"   Alertas activas: {resumen['alertas_fraude_activas']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        return False

def test_deteccion_fraude():
    """Test 4: Probar detección de fraude"""
    print("\n🚨 Test 4: Probando detección de fraude...")
    
    payload = {
        "cliente_id": "test_cliente",
        "metrics": {
            "ventas_atribuidas": 2,
            "promedio_ventas": 15,
            "mensajes_bot": 0,
            "ventas_humanas": 10,
            "ventas_sin_codigo": 8
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/detectar_fraude", json=payload)
        data = response.json()
        
        if data['alertas_detectadas']:
            print("✅ Alertas de fraude detectadas:")
            for alerta in data['alertas_detectadas']:
                print(f"   ⚠️  {alerta}")
        else:
            print("✅ Sin alertas de fraude (comportamiento normal)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en detección de fraude: {e}")
        return False

def test_estadisticas_globales():
    """Test 5: Ver estadísticas globales"""
    print("\n📈 Test 5: Probando estadísticas globales...")
    
    try:
        response = requests.get(f"{BASE_URL}/estadisticas_globales")
        data = response.json()
        
        print("✅ Estadísticas globales:")
        print(f"   Período: {data['periodo']}")
        print(f"   Conversaciones hoy: {data['conversaciones_hoy']}")
        print(f"   Ventas mes: {data['ventas_mes']}")
        print(f"   Comisiones mes: ${data['comisiones_mes']:,.0f}")
        print(f"   Promedio confianza: {data['promedio_confianza']:.1%}")
        print(f"   Sistema activo: {data['sistema_activo']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en estadísticas: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests completos del sistema...")
    print(f"📍 URL base: {BASE_URL}")
    print("=" * 50)
    
    # Test 1: Conversación
    conv_id, codigo = test_conversacion()
    
    # Test 2: Atribución de venta
    if conv_id and codigo:
        venta_id = test_atribucion_venta(conv_id, codigo)
    
    # Test 3: Dashboard admin
    test_dashboard_admin()
    
    # Test 4: Detección de fraude
    test_deteccion_fraude()
    
    # Test 5: Estadísticas globales
    test_estadisticas_globales()
    
    print("\n" + "=" * 50)
    print("✅ Tests completados. Revisa los resultados arriba.")
    print("📊 Para ver el dashboard completo visita:")
    print(f"   {BASE_URL}/dashboard_admin")

if __name__ == "__main__":
    main()

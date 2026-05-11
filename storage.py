"""
Almacenamiento persistente para Vercel serverless
Usa variables globales para persistencia entre llamadas
"""

import json
import os
from datetime import datetime

class StorageManager:
    def __init__(self):
        self.conversaciones_file = "conversaciones.json"
        self.ventas_file = "ventas.json"
        self.alertas_file = "alertas.json"
        
    def cargar_datos(self, archivo, default=None):
        """Cargar datos desde archivo JSON"""
        try:
            if os.path.exists(archivo):
                with open(archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default or {}
        except Exception as e:
            print(f"Error cargando {archivo}: {e}")
            return default or {}
    
    def guardar_datos(self, archivo, datos):
        """Guardar datos en archivo JSON"""
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error guardando {archivo}: {e}")
            return False
    
    def get_conversaciones(self):
        return self.cargar_datos(self.conversaciones_file, {})
    
    def save_conversaciones(self, conversaciones):
        return self.guardar_datos(self.conversaciones_file, conversaciones)
    
    def get_ventas(self):
        return self.cargar_datos(self.ventas_file, {})
    
    def save_ventas(self, ventas):
        return self.guardar_datos(self.ventas_file, ventas)
    
    def get_alertas(self):
        return self.cargar_datos(self.alertas_file, [])
    
    def save_alertas(self, alertas):
        return self.guardar_datos(self.alertas_file, alertas)

# Instancia global
storage = StorageManager()

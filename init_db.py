#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos MongoDB con las colecciones necesarias
y crear un usuario administrador por defecto.
"""

import sys
import os
import logging
import hashlib
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Parámetros de conexión a MongoDB
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "gestion_camiones"

def hash_password(password):
    """Genera un hash para la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Inicializa la base de datos"""
    try:
        # Conectar a MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[DB_NAME]
        logging.info(f"Conexión establecida a MongoDB en {MONGODB_URL}")
        
        # Crear colecciones si no existen
        if "camiones" not in db.list_collection_names():
            db.create_collection("camiones")
        
        if "reparaciones" not in db.list_collection_names():
            db.create_collection("reparaciones")
        
        if "usuarios" not in db.list_collection_names():
            db.create_collection("usuarios")
            
            # Crear usuario administrador por defecto
            admin_user = {
                "_id": ObjectId(),
                "nombre": "Administrador",
                "apellido": "Sistema",
                "usuario": "admin",
                "password": hash_password("admin"),
                "rol": "Admin",
                "activo": True
            }
            
            db.usuarios.insert_one(admin_user)
            logging.info("Usuario administrador creado (usuario: admin, contraseña: admin)")
        
        # Crear algunos datos de ejemplo
        if db.camiones.count_documents({}) == 0:
            # Añadir algunos camiones de ejemplo
            camiones_ejemplo = [
                {
                    "_id": ObjectId(),
                    "matricula": "ABC-123",
                    "modelo": "Volvo FH16",
                    "año": 2022,
                    "estado": "Operativo",
                    "fecha_registro": datetime.now(),
                    "ultima_actualizacion": datetime.now()
                },
                {
                    "_id": ObjectId(),
                    "matricula": "XYZ-789",
                    "modelo": "Mercedes-Benz Actros",
                    "año": 2021,
                    "estado": "Operativo",
                    "fecha_registro": datetime.now(),
                    "ultima_actualizacion": datetime.now()
                }
            ]
            db.camiones.insert_many(camiones_ejemplo)
            logging.info("Datos de ejemplo de camiones creados")
        
        logging.info("Inicialización de la base de datos completada con éxito")
        
        # Cerrar conexión
        client.close()
        return True
    
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    if init_database():
        print("Base de datos inicializada correctamente.")
        sys.exit(0)
    else:
        print("Error al inicializar la base de datos.")
        sys.exit(1)

        #
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para gestionar la conexión a la base de datos MongoDB.
"""

import logging
import os
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class DatabaseConnection:
    """Clase para gestionar la conexión a MongoDB"""
    
    _instance = None
    
    # Valores por defecto para la conexión
    DEFAULT_CONFIG = {
        'mongodb_uri': 'mongodb+srv://royepm005:ZSVRrDPXCHwSJDiP@cluster0.un0zp.mongodb.net',
        'mongodb_db': 'gestion_camiones',
        'log_level': 'INFO',
        'log_file': 'app.log',
        'debug_mode': 'False',
        'app_port': '5000'
    }
    
    def __new__(cls):
        """Implementa el patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        if self._initialized:
            return
            
        self._initialized = True
        self.config = self._cargar_configuracion()
        self.client = None
        self.db = None
        self.connect()
    
    def _cargar_configuracion(self):
        """Carga la configuración de la aplicación"""
        try:
            # Intentar cargar desde variables de entorno primero
            config = {}
            config['mongodb_uri'] = os.environ.get('MONGODB_URI', self.DEFAULT_CONFIG['mongodb_uri'])
            config['mongodb_db'] = os.environ.get('DATABASE_NAME', self.DEFAULT_CONFIG['mongodb_db'])
            config['log_level'] = os.environ.get('LOG_LEVEL', self.DEFAULT_CONFIG['log_level'])
            config['log_file'] = os.environ.get('LOG_FILE', self.DEFAULT_CONFIG['log_file'])
            config['debug_mode'] = os.environ.get('DEBUG_MODE', self.DEFAULT_CONFIG['debug_mode'])
            config['app_port'] = os.environ.get('APP_PORT', self.DEFAULT_CONFIG['app_port'])
            
            # Si no hay variables de entorno, intentar cargar desde archivo
            if not config['mongodb_uri'] or config['mongodb_uri'] == self.DEFAULT_CONFIG['mongodb_uri']:
                # Ruta al archivo de configuración
                config_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'GestionCamiones')
                config_file = os.path.join(config_dir, 'config.json')
                
                # Verificar si existe el archivo y cargarlo
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        # Actualizar solo los valores que no estén en variables de entorno
                        for key, value in file_config.items():
                            if key not in config or not config[key]:
                                config[key] = value
            
            return config
                
        except Exception as e:
            logging.error(f"DatabaseConnection: Error al cargar configuración: {str(e)}")
            # Configuración por defecto en caso de error
            return self.DEFAULT_CONFIG.copy()
    
    def connect(self):
        """Establece la conexión a MongoDB"""
        if self.client is not None:
            return True
        
        try:
            # Obtener URI de la configuración
            uri = self.config.get('mongodb_uri', self.DEFAULT_CONFIG['mongodb_uri'])
            db_name = self.config.get('mongodb_db', self.DEFAULT_CONFIG['mongodb_db'])
            
            # Establecer conexión con timeout
            self.client = MongoClient(uri, serverSelectionTimeoutMS=10000)
            # Verificar conexión
            self.client.admin.command('ping')
            
            # Obtener referencia a la base de datos
            self.db = self.client[db_name]
            
            logging.info(f"Conexión establecida a MongoDB Atlas en {uri.split('@')[1]}")
            
            # Asegurarse de que las colecciones existan
            self._ensure_collections_exist()
            
            return True
        except ConnectionFailure as e:
            logging.error(f"No se pudo conectar a MongoDB: {str(e)}")
            raise
        except ServerSelectionTimeoutError as e:
            logging.error(f"Timeout al conectar a MongoDB: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error al conectar a MongoDB: {str(e)}")
            raise
    
    def _ensure_collections_exist(self):
        """Verifica y crea las colecciones necesarias si no existen"""
        try:
            # Lista de colecciones que se van a verificar/crear
            collections = ['mecanicos', 'camiones', 'reparaciones', 'usuarios', 'preventivas']
            
            # Obtener lista de colecciones existentes
            existing_collections = self.db.list_collection_names()
            
            # Crear colecciones que no existen
            for collection_name in collections:
                if collection_name not in existing_collections:
                    self.db.create_collection(collection_name)
                    logging.info(f"Colección '{collection_name}' creada")
                    
                    # Crear índices básicos según la colección
                    if collection_name == 'mecanicos':
                        self.db[collection_name].create_index([('apellidos', 1)])
                        self.db[collection_name].create_index([('actividad', 1)])
                    elif collection_name == 'camiones':
                        self.db[collection_name].create_index([('matricula', 1)], unique=True)
                        self.db[collection_name].create_index([('estado', 1)])
                    elif collection_name == 'reparaciones':
                        self.db[collection_name].create_index([('id_camion', 1)])
                        self.db[collection_name].create_index([('id_mecanico', 1)])
                    elif collection_name == 'usuarios':
                        self.db[collection_name].create_index([('username', 1)], unique=True)
                    elif collection_name == 'preventivas':
                        self.db[collection_name].create_index([('matricula', 1)])
                        self.db[collection_name].create_index([('estado', 1)])
                        self.db[collection_name].create_index([('nivel_urgencia', 1)])
            
        except Exception as e:
            logging.error(f"Error al verificar/crear colecciones: {str(e)}")
    
    def close(self):
        """Cierra la conexión a MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logging.info("Conexión a MongoDB cerrada")
    
    def get_collection(self, collection_name):
        """Obtiene una colección de la base de datos"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def get_mecanicos_collection(self):
        """Obtiene la colección de mecánicos"""
        return self.get_collection("mecanicos")
    
    def get_camiones_collection(self):
        """Obtiene la colección de camiones"""
        return self.get_collection("camiones")
    
    def get_reparaciones_collection(self):
        """Obtiene la colección de reparaciones"""
        return self.get_collection("reparaciones")
    
    def get_usuarios_collection(self):
        """Obtiene la colección de usuarios"""
        return self.get_collection("usuarios")
    
    def get_preventivas_collection(self):
        """Obtiene la colección de preventivas"""
        return self.get_collection("preventivas")
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuración global de la aplicación.
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Clase de configuración para la aplicación"""
    
    # Configuración por defecto
    DEFAULT_CONFIG = {
        "database": {
            "type": "local",  # "local" o "atlas"
            "host": "localhost",
            "port": 27017,
            "name": "gestion_camiones",
            "auth_enabled": False,
            "username": "",
            "password": "",
            "atlas_uri": ""
        },
        "app": {
            "theme": "light",  # "light" o "dark"
            "language": "es",
            "log_level": "INFO"
        }
    }
    
    _instance = None
    
    def __new__(cls):
        """Implementa el patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa la configuración"""
        if self._initialized:
            return
            
        self._initialized = True
        self._config = None
        self._config_file = self._get_config_file_path()
        
        # Cargar variables de entorno
        self._load_env_variables()
        
        # Cargar configuración
        self.load_config()
        
        # Crear atributos directos para compatibilidad
        self.mongodb_uri = self._get_mongodb_uri()
        self.database_name = self.get("database", "name")
    
    def _load_env_variables(self):
        """Carga variables de entorno desde archivo .env si existe"""
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logging.info(f"Variables de entorno cargadas desde {env_file}")
    
    def _get_config_file_path(self):
        """Obtiene la ruta del archivo de configuración"""
        # En Windows: %APPDATA%\GestionCamiones\config.json
        # En Linux/Mac: ~/.config/GestionCamiones/config.json
        if os.name == "nt":  # Windows
            app_data = os.getenv("APPDATA")
            config_dir = os.path.join(app_data, "GestionCamiones")
        else:  # Linux/Mac
            home = os.path.expanduser("~")
            config_dir = os.path.join(home, ".config", "GestionCamiones")
        
        # Crear directorio si no existe
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        return os.path.join(config_dir, "config.json")
    
    def load_config(self):
        """Carga la configuración desde el archivo"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logging.info(f"Configuración cargada desde {self._config_file}")
            else:
                self._config = self.DEFAULT_CONFIG
                self.save_config()
                logging.info("Configuración por defecto creada")
        except Exception as e:
            logging.error(f"Error al cargar la configuración: {str(e)}")
            self._config = self.DEFAULT_CONFIG
        
        # Aplicar variables de entorno si existen
        self._apply_env_config()
        
        # Actualizar atributos directos después de cargar configuración
        self.mongodb_uri = self._get_mongodb_uri()
        self.database_name = self.get("database", "name")
    
    def _apply_env_config(self):
        """Aplica configuración desde variables de entorno"""
        # Configuración de MongoDB Atlas desde variables de entorno
        mongodb_uri = os.getenv("MONGODB_URI")
        if mongodb_uri:
            self._config["database"]["type"] = "atlas"
            self._config["database"]["atlas_uri"] = mongodb_uri
            
        # Credenciales separadas para MongoDB Atlas
        mongodb_user = os.getenv("MONGODB_USER")
        mongodb_password = os.getenv("MONGODB_PASSWORD")
        mongodb_host = os.getenv("MONGODB_HOST")
        
        if mongodb_user and mongodb_password and mongodb_host:
            self._config["database"]["type"] = "atlas"
            self._config["database"]["username"] = mongodb_user
            self._config["database"]["password"] = mongodb_password
            self._config["database"]["host"] = mongodb_host
            self._config["database"]["auth_enabled"] = True
        
        # Nombre de la base de datos
        db_name = os.getenv("DATABASE_NAME")
        if db_name:
            self._config["database"]["name"] = db_name
    
    def save_config(self):
        """Guarda la configuración en el archivo"""
        try:
            # Crear una copia de la configuración sin información sensible
            safe_config = json.loads(json.dumps(self._config))
            
            # Eliminamos contraseñas y URIs completas del archivo guardado
            if "database" in safe_config:
                if "atlas_uri" in safe_config["database"]:
                    if safe_config["database"]["atlas_uri"]:
                        safe_config["database"]["atlas_uri"] = "***REDACTED***"
                
                if "password" in safe_config["database"]:
                    if safe_config["database"]["password"]:
                        safe_config["database"]["password"] = "***REDACTED***"
            
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(safe_config, f, indent=4)
            logging.info(f"Configuración guardada en {self._config_file}")
        except Exception as e:
            logging.error(f"Error al guardar la configuración: {str(e)}")
    
    def get(self, section, key=None):
        """Obtiene un valor de configuración"""
        if key is None:
            return self._config.get(section, {})
        return self._config.get(section, {}).get(key)
    
    def set(self, section, key, value):
        """Establece un valor de configuración"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self.save_config()
        
        # Actualizar atributos si es necesario
        if section == "database":
            self.mongodb_uri = self._get_mongodb_uri()
            if key == "name":
                self.database_name = value
    
    def _get_mongodb_uri(self):
        """Obtiene la URI de conexión a MongoDB"""
        db_config = self.get("database")
        
        # Si tenemos una URI de Atlas ya configurada, utilizarla
        if db_config.get("type") == "atlas":
            atlas_uri = db_config.get("atlas_uri")
            if atlas_uri:
                # Limpiar la URI para asegurar formato correcto
                # Eliminar cualquier barra final
                atlas_uri = atlas_uri.rstrip("/")
                
                # Asegurarnos que la URI incluye el nombre de la base de datos
                # pero sin barra final
                if not atlas_uri.endswith(f"/{db_config['name']}"):
                    atlas_uri += f"/{db_config['name']}"
                
                return atlas_uri
            
            # Construir URI de Atlas con credenciales separadas
            if db_config.get("username") and db_config.get("password") and db_config.get("host"):
                return f"mongodb+srv://{db_config['username']}:{db_config['password']}@{db_config['host']}/{db_config['name']}"
        
        # URI para MongoDB local
        if db_config.get("auth_enabled", False):
            return f"mongodb://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
        else:
            return f"mongodb://{db_config['host']}:{db_config['port']}/{db_config['name']}"
    
    @property
    def theme(self):
        """Obtiene el tema de la aplicación"""
        return self.get("app", "theme")
    
    @theme.setter
    def theme(self, value):
        """Establece el tema de la aplicación"""
        self.set("app", "theme", value)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constantes y configuraciones globales de la aplicación.
"""

# Nombre de la aplicación
APP_NAME = "Sistema de Gestión de Reparaciones de Camiones"
APP_VERSION = "1.0.0"

# Configuración de la base de datos
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 27017
DEFAULT_DB_NAME = "gestion_camiones"

# Temas de la aplicación
THEME_LIGHT = "light"
THEME_DARK = "dark"

# Configuración de la interfaz de usuario
UI_DEFAULT_FONT = "Segoe UI" if hasattr(__import__('os'), 'name') and __import__('os').name == 'nt' else "Arial"
UI_DEFAULT_FONT_SIZE = 10
UI_DEFAULT_SPACING = 10

# Colores para estados
COLOR_OPERATIVO = "#C8FFC8"  # Verde claro
COLOR_EN_REPARACION = "#FFC8C8"  # Rojo claro
COLOR_FUERA_SERVICIO = "#C8C8C8"  # Gris claro
COLOR_EN_ESPERA = "#FFFFC8"  # Amarillo claro
COLOR_REPARADO = "#C8FFC8"  # Verde claro

# Formato de fecha
DATE_FORMAT = "%d/%m/%Y %H:%M"
DATE_FORMAT_SHORT = "%d/%m/%Y"

# Mensajes comunes
MSG_ERROR_DB_CONNECTION = "No se pudo conectar a la base de datos. Verifique la configuración."
MSG_ERROR_AUTHENTICATION = "Usuario o contraseña incorrectos."
MSG_ERROR_PERMISSION = "No tiene permisos para realizar esta acción."
MSG_CONFIRM_DELETE = "¿Está seguro que desea eliminar este registro? Esta acción no se puede deshacer."
MSG_CONFIRM_EXIT = "¿Está seguro que desea salir de la aplicación?"
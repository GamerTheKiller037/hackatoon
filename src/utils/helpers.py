#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funciones auxiliares para la aplicación.
"""

import logging
import os
import sys
import platform
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QColor

def configure_logging(log_file="app.log", level=logging.INFO):
    """
    Configura el sistema de logging.
    
    Args:
        log_file (str): Ruta del archivo de log
        level (int): Nivel de logging
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_app_dir():
    """
    Obtiene el directorio de datos de la aplicación según el sistema operativo.
    
    Returns:
        str: Ruta del directorio de datos
    """
    app_name = "GestionCamiones"
    
    if platform.system() == "Windows":
        app_data = os.environ.get("APPDATA")
        return os.path.join(app_data, app_name)
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", app_name)
    else:  # Linux/Unix
        return os.path.join(os.path.expanduser("~"), ".config", app_name)

def ensure_dir_exists(directory):
    """
    Asegura que un directorio existe, lo crea si no existe.
    
    Args:
        directory (str): Ruta del directorio
    
    Returns:
        bool: True si el directorio existe o fue creado, False en caso contrario
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        logging.error(f"Error al crear directorio {directory}: {str(e)}")
        return False

def format_date(date):
    """
    Formatea una fecha para mostrar.
    
    Args:
        date (datetime): Fecha a formatear
    
    Returns:
        str: Fecha formateada
    """
    if date is None:
        return ""
    
    # Convertir a formato legible
    return date.strftime("%d/%m/%Y %H:%M")

def timestamp_to_datetime(timestamp):
    """
    Convierte un timestamp a datetime.
    
    Args:
        timestamp (int): Timestamp en segundos
    
    Returns:
        datetime: Objeto datetime
    """
    return datetime.fromtimestamp(timestamp)

def datetime_to_timestamp(dt):
    """
    Convierte un datetime a timestamp.
    
    Args:
        dt (datetime): Objeto datetime
    
    Returns:
        int: Timestamp en segundos
    """
    return int(dt.timestamp())

def datetime_to_qdatetime(dt):
    """
    Convierte un datetime de Python a QDateTime.
    
    Args:
        dt (datetime): Objeto datetime de Python
    
    Returns:
        QDateTime: Objeto QDateTime
    """
    if dt is None:
        return QDateTime.currentDateTime()
    
    qdt = QDateTime()
    qdt.setSecsSinceEpoch(int(dt.timestamp()))
    return qdt

def qdatetime_to_datetime(qdt):
    """
    Convierte un QDateTime a datetime de Python.
    
    Args:
        qdt (QDateTime): Objeto QDateTime
    
    Returns:
        datetime: Objeto datetime de Python
    """
    return datetime.fromtimestamp(qdt.toSecsSinceEpoch())

def show_error_message(parent, title, message):
    """
    Muestra un mensaje de error.
    
    Args:
        parent (QWidget): Widget padre
        title (str): Título del mensaje
        message (str): Contenido del mensaje
    """
    QMessageBox.critical(parent, title, message)

def show_warning_message(parent, title, message):
    """
    Muestra un mensaje de advertencia.
    
    Args:
        parent (QWidget): Widget padre
        title (str): Título del mensaje
        message (str): Contenido del mensaje
    """
    QMessageBox.warning(parent, title, message)

def show_info_message(parent, title, message):
    """
    Muestra un mensaje informativo.
    
    Args:
        parent (QWidget): Widget padre
        title (str): Título del mensaje
        message (str): Contenido del mensaje
    """
    QMessageBox.information(parent, title, message)

def show_confirmation_message(parent, title, message):
    """
    Muestra un mensaje de confirmación.
    
    Args:
        parent (QWidget): Widget padre
        title (str): Título del mensaje
        message (str): Contenido del mensaje
    
    Returns:
        bool: True si se confirmó, False en caso contrario
    """
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes

def get_color_for_estado_camion(estado):
    """
    Obtiene el color para un estado de camión.
    
    Args:
        estado (str): Estado del camión
    
    Returns:
        QColor: Color para el estado
    """
    from models.camion import Camion
    from utils.constants import COLOR_OPERATIVO, COLOR_EN_REPARACION, COLOR_FUERA_SERVICIO
    
    if estado == Camion.ESTADO_OPERATIVO:
        return QColor(COLOR_OPERATIVO)
    elif estado == Camion.ESTADO_EN_REPARACION:
        return QColor(COLOR_EN_REPARACION)
    elif estado == Camion.ESTADO_FUERA_SERVICIO:
        return QColor(COLOR_FUERA_SERVICIO)
    else:
        return QColor(Qt.white)

def get_color_for_estado_reparacion(estado):
    """
    Obtiene el color para un estado de reparación.
    
    Args:
        estado (str): Estado de la reparación
    
    Returns:
        QColor: Color para el estado
    """
    from models.reparacion import Reparacion
    from utils.constants import COLOR_EN_ESPERA, COLOR_EN_REPARACION, COLOR_REPARADO
    
    if estado == Reparacion.ESTADO_EN_ESPERA:
        return QColor(COLOR_EN_ESPERA)
    elif estado == Reparacion.ESTADO_EN_REPARACION:
        return QColor(COLOR_EN_REPARACION)
    elif estado == Reparacion.ESTADO_REPARADO:
        return QColor(COLOR_REPARADO)
    else:
        return QColor(Qt.white)
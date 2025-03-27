#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Gestión de Reparaciones de Camiones
Punto de entrada principal para la aplicación.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import qdarkstyle

# Agregar directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Importar después de configurar el path
from views.login_dialog import LoginDialog
from views.main_window import MainWindow
from database.connection import DatabaseConnection
from config import Config

def excepthook(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones no capturadas"""
    logging.error("Excepción no capturada:", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def main():
    """Función principal de la aplicación"""
    # Configurar manejador de excepciones
    sys.excepthook = excepthook
    
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Gestión de Reparaciones de Camiones")
    app.setOrganizationName("MiEmpresa")
    
    # Establecer estilo oscuro (opcional, se puede cambiar por preferencia del usuario)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    # Configurar ícono de la aplicación
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Inicializar conexión a la base de datos
    try:
        db_connection = DatabaseConnection()
        db_connection.connect()
        logging.info("Conexión a la base de datos establecida correctamente")
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {str(e)}")
        # Aquí podrías mostrar un diálogo de error y salir de la aplicación
        sys.exit(1)
    
    # Mostrar diálogo de inicio de sesión
    login_dialog = LoginDialog()
    if login_dialog.exec_() == LoginDialog.Accepted:
        # Inicio de sesión exitoso, obtener usuario actual
        current_user = login_dialog.get_current_user()
        
        # Crear y mostrar la ventana principal
        main_window = MainWindow(current_user)
        main_window.show()
        
        # Ejecutar el bucle de eventos
        return_code = app.exec_()
        
        # Cerrar conexión a la base de datos al salir
        db_connection.close()
        
        return return_code
    else:
        # El usuario canceló el inicio de sesión
        db_connection.close()
        return 0
with open('src/main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

for i, line in enumerate(lines):
    if 'main_window = MainWindow(current_user)' in line:
            lines[i] = line.replace('current_user=current_user', 'current_user')

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Archivo main.py corregido para usar parámetro posicional en lugar de con nombre.")

if __name__ == "__main__":
    sys.exit(main())
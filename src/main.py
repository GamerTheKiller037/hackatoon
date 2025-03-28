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
from PyQt5.QtGui import QIcon, QFont
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
    
    # Configurar la fuente global para hacerla más grande y legible
    font = QFont("Segoe UI", 10)  # Fuente más grande (antes era 9)
    app.setFont(font)
    
    # Establecer hoja de estilo global
    app.setStyleSheet("""
        QMainWindow::title {
            background-color: #6a1b9a;
            color: white;
        }
        
        QMenuBar {
            background-color: #6a1b9a;
            color: white;
            font-size: 11pt;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 10px;
        }
        
        QMenuBar::item:selected {
            background-color: #8e24aa;
        }
        
        QMenu {
            background-color: #f5f5f5;
            font-size: 11pt;
        }
        
        QMenu::item:selected {
            background-color: #e1bee7;
        }
        
        QTabWidget::pane {
            border: 1px solid #d0d0d0;
        }
        
        QTabBar::tab {
            background-color: #f0f0f0;
            padding: 8px 12px;
            margin-right: 2px;
            font-size: 11pt;
        }
        
        QTabBar::tab:selected {
            background-color: #6a1b9a;
            color: white;
        }
        
        QTableWidget {
            font-size: 11pt;
        }
        
        QHeaderView::section {
            background-color: #6a1b9a;
            color: white;
            padding: 6px;
            font-size: 11pt;
            font-weight: bold;
        }
        
        QPushButton {
            padding: 6px 12px;
            font-size: 11pt;
        }
        
        QLineEdit, QComboBox, QSpinBox, QDateEdit {
            padding: 6px;
            font-size: 11pt;
        }
        
        QLabel {
            font-size: 11pt;
        }
    """)
    
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

if __name__ == "__main__":
    sys.exit(main())
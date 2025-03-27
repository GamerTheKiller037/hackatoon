#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget personalizado para mostrar el estado (camión o reparación).
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QFont

class StatusWidget(QLabel):
    """Widget personalizado para mostrar el estado con colores"""
    
    def __init__(self, text="", color=None, parent=None):
        """
        Inicializa el widget de estado.
        
        Args:
            text (str): Texto a mostrar
            color (QColor, optional): Color de fondo
            parent (QWidget, optional): Widget padre
        """
        super().__init__(text, parent)
        
        self.text = text
        self.bg_color = color or QColor(255, 255, 255)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setMinimumWidth(100)
        self.setMinimumHeight(30)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"background-color: {self.bg_color.name()}; "
            f"border-radius: 4px; "
            f"padding: 4px; "
            f"font-weight: bold;"
        )
    
    def set_text(self, text):
        """
        Establece el texto del widget.
        
        Args:
            text (str): Nuevo texto
        """
        self.text = text
        self.setText(text)
    
    def set_color(self, color):
        """
        Establece el color de fondo.
        
        Args:
            color (QColor): Nuevo color
        """
        self.bg_color = color
        self.setStyleSheet(
            f"background-color: {self.bg_color.name()}; "
            f"border-radius: 4px; "
            f"padding: 4px; "
            f"font-weight: bold;"
        )

class CamionStatusWidget(StatusWidget):
    """Widget para mostrar el estado de un camión"""
    
    def __init__(self, estado, parent=None):
        """
        Inicializa el widget de estado de camión.
        
        Args:
            estado (str): Estado del camión
            parent (QWidget, optional): Widget padre
        """
        from models.camion import Camion
        from utils.helpers import get_color_for_estado_camion
        
        color = get_color_for_estado_camion(estado)
        super().__init__(estado, color, parent)

class ReparacionStatusWidget(StatusWidget):
    """Widget para mostrar el estado de una reparación"""
    
    def __init__(self, estado, parent=None):
        """
        Inicializa el widget de estado de reparación.
        
        Args:
            estado (str): Estado de la reparación
            parent (QWidget, optional): Widget padre
        """
        from models.reparacion import Reparacion
        from utils.helpers import get_color_for_estado_reparacion
        
        color = get_color_for_estado_reparacion(estado)
        super().__init__(estado, color, parent)
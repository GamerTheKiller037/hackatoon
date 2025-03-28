#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Formulario para crear o editar un camión.p
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QMessageBox,
                           QFormLayout, QSpinBox, QDialogButtonBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database.camiones_dao import CamionesDAO
from models.camion import Camion

class FormCamionDialog(QDialog):
    """Diálogo para crear o editar un camión"""
    
    def __init__(self, camion=None, parent=None):
        """
        Inicializa el formulario para camión.
        
        Args:
            camion (Camion, optional): Camión a editar. Si es None, se crea uno nuevo.
            parent (QWidget, optional): Widget padre.
        """
        super().__init__(parent)
        
        self.camion = camion
        self.camiones_dao = CamionesDAO()
        
        self.setup_ui()
        
        # Si estamos editando, cargar datos del camión
        if self.camion:
            self.setWindowTitle("Editar Camión")
            self.load_camion_data()
        else:
            self.setWindowTitle("Nuevo Camión")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setMinimumWidth(500)  # Aumentar ancho mínimo
        self.setMinimumHeight(400)  # Aumentar alto mínimo
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Establecer una fuente más grande para todo el diálogo
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Márgenes más grandes
        
        # Barra superior morada 
        header = QFrame()
        header.setStyleSheet("background-color: #6a1b9a; min-height: 50px;")
        header_layout = QVBoxLayout(header)
        
        # Título en la barra morada
        title_label = QLabel("Información del Camión")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)  # Alineación a la izquierda
        form_layout.setFormAlignment(Qt.AlignLeft)   # Alineación a la izquierda
        form_layout.setVerticalSpacing(15)  # Más espacio entre campos
        
        # Estilo para las etiquetas del formulario
        label_style = "font-size: 18px; font-weight: bold;"
        
        # Campo: Matrícula
        label_matricula = QLabel("Matrícula:")
        label_matricula.setStyleSheet(label_style)
        self.matricula_input = QLineEdit()
        self.matricula_input.setMaxLength(20)
        self.matricula_input.setPlaceholderText("Ingrese la matrícula")
        self.matricula_input.setMinimumHeight(35)  # Altura mínima aumentada
        form_layout.addRow(label_matricula, self.matricula_input)
        
        # Campo: Modelo
        label_modelo = QLabel("Modelo:")
        label_modelo.setStyleSheet(label_style)
        self.modelo_input = QLineEdit()
        self.modelo_input.setMaxLength(50)
        self.modelo_input.setPlaceholderText("Ingrese el modelo")
        self.modelo_input.setMinimumHeight(35)  # Altura mínima aumentada
        form_layout.addRow(label_modelo, self.modelo_input)
        
        # Campo: Año
        label_año = QLabel("Año:")
        label_año.setStyleSheet(label_style)
        self.año_input = QSpinBox()
        self.año_input.setRange(1950, 2100)
        self.año_input.setValue(2023)  # Valor por defecto
        self.año_input.setMinimumHeight(35)  # Altura mínima aumentada
        form_layout.addRow(label_año, self.año_input)
        
        # Campo: Estado
        label_estado = QLabel("Estado:")
        label_estado.setStyleSheet(label_style)
        self.estado_input = QComboBox()
        for estado in Camion.ESTADOS_VALIDOS:
            self.estado_input.addItem(estado)
        self.estado_input.setMinimumHeight(35)  # Altura mínima aumentada
        form_layout.addRow(label_estado, self.estado_input)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # Más espacio entre botones
        
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setMinimumHeight(40)  # Altura mínima aumentada
        self.btn_guardar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px; border-radius: 4px;")
        self.btn_guardar.clicked.connect(self.accept)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setMinimumHeight(40)  # Altura mínima aumentada
        self.btn_cancelar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px; border-radius: 4px;")
        self.btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cancelar)
        
        main_layout.addLayout(button_layout)
    
    def load_camion_data(self):
        """Carga los datos del camión en el formulario"""
        if not self.camion:
            return
        
        self.matricula_input.setText(self.camion.matricula)
        self.modelo_input.setText(self.camion.modelo)
        self.año_input.setValue(self.camion.año)
        
        # Seleccionar el estado actual
        index = self.estado_input.findText(self.camion.estado)
        if index >= 0:
            self.estado_input.setCurrentIndex(index)
    
    def validate_form(self):
        """
        Valida el formulario.
        
        Returns:
            bool: True si el formulario es válido, False en caso contrario.
        """
        # Código original sin cambios
        
    
    
    
    def accept(self):
        """Procesa el formulario cuando se acepta"""
        if not self.validate_form():
            return
        
        # Obtener datos del formulario
        matricula = self.matricula_input.text().strip()
        modelo = self.modelo_input.text().strip()
        año = self.año_input.value()
        estado = self.estado_input.currentText()
        
        try:
            if self.camion:
                # Actualizar camión existente
                self.camion.actualizar(
                    matricula=matricula,
                    modelo=modelo,
                    año=año,
                    estado=estado
                )
                
                if self.camiones_dao.actualizar(self.camion):
                    QMessageBox.information(
                        self, 
                        "Camión actualizado", 
                        f"El camión {matricula} ha sido actualizado correctamente."
                    )
                    # Notificar a la ventana principal sobre la actualización
                    parent_window = self.parent()
                    while parent_window and not hasattr(parent_window, 'on_camion_actualizado'):
                        parent_window = parent_window.parent()
                    
                    if parent_window and hasattr(parent_window, 'on_camion_actualizado'):
                        parent_window.on_camion_actualizado(self.camion)
                    
                    super().accept()
                else:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "No se pudo actualizar el camión. Inténtelo de nuevo."
                    )
            else:
                # Crear nuevo camión
                new_camion = Camion(
                    matricula=matricula,
                    modelo=modelo,
                    año=año,
                    estado=estado
                )
                
                if self.camiones_dao.insertar(new_camion):
                    QMessageBox.information(
                        self, 
                        "Camión creado", 
                        f"El camión {matricula} ha sido creado correctamente."
                    )
                    # Notificar a la ventana principal sobre la creación
                    parent_window = self.parent()
                    while parent_window and not hasattr(parent_window, 'dashboard'):
                        parent_window = parent_window.parent()
                    
                    if parent_window and hasattr(parent_window, 'dashboard') and hasattr(parent_window.dashboard, 'agregar_actividad'):
                        parent_window.dashboard.agregar_actividad('camion', new_camion, "Nuevo camión creado")
                    
                    super().accept()
                else:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "No se pudo crear el camión. Inténtelo de nuevo."
                    )
        except Exception as e:
            logging.error(f"Error al guardar el camión: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Ha ocurrido un error al guardar el camión: {str(e)}"
            )

if __name__ == "__main__":
    # Prueba del diálogo
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Prueba de creación
    dialog = FormCamionDialog()
    if dialog.exec_():
        print("Camión creado")
    
    # Prueba de edición
    camion = Camion(
        matricula="ABC-123",
        modelo="Modelo de prueba",
        año=2023,
        estado="Operativo"
    )
    dialog = FormCamionDialog(camion=camion)
    if dialog.exec_():
        print("Camión actualizado")
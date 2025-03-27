#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Formulario para crear o editar un camión.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QMessageBox,
                           QFormLayout, QSpinBox, QDialogButtonBox)
from PyQt5.QtCore import Qt

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
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        
        # Campo: Matrícula
        self.matricula_input = QLineEdit()
        self.matricula_input.setMaxLength(20)
        self.matricula_input.setPlaceholderText("Ingrese la matrícula")
        form_layout.addRow("Matrícula:", self.matricula_input)
        
        # Campo: Modelo
        self.modelo_input = QLineEdit()
        self.modelo_input.setMaxLength(50)
        self.modelo_input.setPlaceholderText("Ingrese el modelo")
        form_layout.addRow("Modelo:", self.modelo_input)
        
        # Campo: Año
        self.año_input = QSpinBox()
        self.año_input.setRange(1950, 2100)
        self.año_input.setValue(2023)  # Valor por defecto
        form_layout.addRow("Año:", self.año_input)
        
        # Campo: Estado
        self.estado_input = QComboBox()
        for estado in Camion.ESTADOS_VALIDOS:
            self.estado_input.addItem(estado)
        form_layout.addRow("Estado:", self.estado_input)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(button_box)
    
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
        # Validar matrícula
        matricula = self.matricula_input.text().strip()
        if not matricula:
            QMessageBox.warning(self, "Validación", "La matrícula es obligatoria.")
            self.matricula_input.setFocus()
            return False
        
        # Validar modelo
        modelo = self.modelo_input.text().strip()
        if not modelo:
            QMessageBox.warning(self, "Validación", "El modelo es obligatorio.")
            self.modelo_input.setFocus()
            return False
        
        # Si estamos creando un nuevo camión, verificar que la matrícula no exista
        if not self.camion:
            existing_camion = self.camiones_dao.obtener_por_matricula(matricula)
            if existing_camion:
                QMessageBox.warning(
                    self, 
                    "Matrícula duplicada", 
                    f"Ya existe un camión con la matrícula {matricula}."
                )
                self.matricula_input.setFocus()
                return False
        
        # Si estamos editando y la matrícula cambió, verificar que no exista
        elif self.camion.matricula != matricula:
            existing_camion = self.camiones_dao.obtener_por_matricula(matricula)
            if existing_camion:
                QMessageBox.warning(
                    self, 
                    "Matrícula duplicada", 
                    f"Ya existe un camión con la matrícula {matricula}."
                )
                self.matricula_input.setFocus()
                return False
        
        return True
    
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
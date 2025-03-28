"""
Formulario para crear o editar un mecánico.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QMessageBox,
                           QFormLayout, QDialogButtonBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database.mecanicos_dao import MecanicosDAO
from models.mecanico import Mecanico

class FormMecanicoDialog(QDialog):
    """Diálogo para crear o editar un mecánico"""
    
    def __init__(self, mecanico=None, parent=None):
        """
        Inicializa el formulario para mecánico.
        
        Args:
            mecanico (Mecanico, optional): Mecánico a editar. Si es None, se crea uno nuevo.
            parent (QWidget, optional): Widget padre.
        """
        super().__init__(parent)
        
        self.mecanico = mecanico
        self.mecanicos_dao = MecanicosDAO()
        
        self.setup_ui()
        
        # Si estamos editando, cargar datos del mecánico
        if self.mecanico:
            self.setWindowTitle("Editar Mecánico")
            self.load_mecanico_data()
        else:
            self.setWindowTitle("Nuevo Mecánico")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setMinimumWidth(500)  # Aumentar ancho mínimo
        self.setMinimumHeight(400)  # Aumentar alto mínimo
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Establecer una fuente más grande para todo el diálogo
        font = QFont()
        font.setPointSize(12)
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
        title_label = QLabel("Información del Mecánico")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(15)  # Más espacio entre campos
        
        # Estilo para las etiquetas del formulario
        label_style = "font-size: 18px; font-weight: bold;"
        
        # Campo: Nombre
        label_nombre = QLabel("Nombre:")
        label_nombre.setStyleSheet(label_style)
        self.nombre_input = QLineEdit()
        self.nombre_input.setMaxLength(50)
        self.nombre_input.setPlaceholderText("Ingrese el nombre")
        self.nombre_input.setMinimumHeight(35)  # Altura mínima aumentada
        form_layout.addRow(label_nombre, self.nombre_input)
        
        # Campo: Apellidos
        label_apellidos = QLabel("Apellidos:")
        label_apellidos.setStyleSheet(label_style)
        self.apellidos_input = QLineEdit()
        self.apellidos_input.setMaxLength(100)
        self.apellidos_input.setPlaceholderText("Ingrese los apellidos")
        self.apellidos_input.setMinimumHeight(35)  # Altura mínima aumentada
        form_layout.addRow(label_apellidos, self.apellidos_input)
        
        # Campo: Actividad
        label_actividad = QLabel("Actividad:")
        label_actividad.setStyleSheet(label_style)
        self.actividad_input = QComboBox()
        self.actividad_input.setMinimumHeight(35)  # Altura mínima aumentada
        for actividad in Mecanico.ACTIVIDADES_VALIDAS:
            self.actividad_input.addItem(actividad)
        form_layout.addRow(label_actividad, self.actividad_input)
        
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
    
    def load_mecanico_data(self):
        """Carga los datos del mecánico en el formulario"""
        if not self.mecanico:
            return
        
        self.nombre_input.setText(self.mecanico.nombre)
        self.apellidos_input.setText(self.mecanico.apellidos)
        
        # Seleccionar la actividad actual
        index = self.actividad_input.findText(self.mecanico.actividad)
        if index >= 0:
            self.actividad_input.setCurrentIndex(index)
    
    def validate_form(self):
        """
        Valida el formulario.
        
        Returns:
            bool: True si el formulario es válido, False en caso contrario.
        """
        # Validar nombre
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            self.nombre_input.setFocus()
            return False
        
        # Validar apellidos
        apellidos = self.apellidos_input.text().strip()
        if not apellidos:
            QMessageBox.warning(self, "Validación", "Los apellidos son obligatorios.")
            self.apellidos_input.setFocus()
            return False
        
        return True
    
    def accept(self):
        """Procesa el formulario cuando se acepta"""
        if not self.validate_form():
            return
        
        # Obtener datos del formulario
        nombre = self.nombre_input.text().strip()
        apellidos = self.apellidos_input.text().strip()
        actividad = self.actividad_input.currentText()
        
        try:
            if self.mecanico:
                # Actualizar mecánico existente
                self.mecanico.actualizar(
                    nombre=nombre,
                    apellidos=apellidos,
                    actividad=actividad
                )
                
                if self.mecanicos_dao.actualizar(self.mecanico):
                    QMessageBox.information(
                        self, 
                        "Mecánico actualizado", 
                        f"El mecánico {nombre} {apellidos} ha sido actualizado correctamente."
                    )
                    super().accept()
                else:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "No se pudo actualizar el mecánico. Inténtelo de nuevo."
                    )
            else:
                # Crear nuevo mecánico
                new_mecanico = Mecanico(
                    nombre=nombre,
                    apellidos=apellidos,
                    actividad=actividad
                )
                
                if self.mecanicos_dao.insertar(new_mecanico):
                    QMessageBox.information(
                        self, 
                        "Mecánico creado", 
                        f"El mecánico {nombre} {apellidos} ha sido creado correctamente."
                    )
                    super().accept()
                else:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "No se pudo crear el mecánico. Inténtelo de nuevo."
                    )
        except Exception as e:
            logging.error(f"Error al guardar el mecánico: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Ha ocurrido un error al guardar el mecánico: {str(e)}"
            )
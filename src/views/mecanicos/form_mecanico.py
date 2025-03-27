"""
Formulario para crear o editar un mecánico.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QMessageBox,
                           QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt

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
        
        # Campo: Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setMaxLength(50)
        self.nombre_input.setPlaceholderText("Ingrese el nombre")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Campo: Apellidos
        self.apellidos_input = QLineEdit()
        self.apellidos_input.setMaxLength(100)
        self.apellidos_input.setPlaceholderText("Ingrese los apellidos")
        form_layout.addRow("Apellidos:", self.apellidos_input)
        
        # Campo: Actividad
        self.actividad_input = QComboBox()
        for actividad in Mecanico.ACTIVIDADES_VALIDAS:
            self.actividad_input.addItem(actividad)
        form_layout.addRow("Actividad:", self.actividad_input)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(button_box)
    
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

if __name__ == "__main__":
    # Prueba del diálogo
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Prueba de creación
    dialog = FormMecanicoDialog()
    if dialog.exec_():
        print("Mecánico creado")
    
    # Prueba de edición
    mecanico = Mecanico(
        nombre="Juan",
        apellidos="Pérez González",
        actividad="Sin actividad"
    )
    dialog = FormMecanicoDialog(mecanico=mecanico)
    if dialog.exec_():
        print("Mecánico actualizado")
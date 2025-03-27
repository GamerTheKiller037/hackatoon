from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtCore import QDate
from models.mecanico import Mecanico
from database.mecanicos_dao import MecanicosDAO
from bson import ObjectId

class DetalleMecanicoDialog(QDialog):
    def __init__(self, mecanico, parent=None):
        """
        Diálogo para mostrar y editar los detalles de un mecánico
        
        Args:
            mecanico: Objeto Mecanico a mostrar
            parent: Widget padre
        """
        super().__init__(parent)
        self.mecanico = mecanico
        self.mecanicos_dao = MecanicosDAO()
        self.actividad_anterior = mecanico.actividad
        self.setWindowTitle(f"Detalles del Mecánico: {mecanico.nombre} {mecanico.apellidos}")
        self.resize(400, 300)
        
        self.initUI()
        
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout()
        
        # Formulario de detalles
        form_layout = QFormLayout()
        
        # Información básica
        form_layout.addRow("ID:", QLabel(str(self.mecanico.id)))
        form_layout.addRow("Nombre:", QLabel(self.mecanico.nombre))
        form_layout.addRow("Apellidos:", QLabel(self.mecanico.apellidos))
        
        # Actividad (editable)
        self.combo_actividad = QComboBox()
        self.combo_actividad.addItems(Mecanico.ACTIVIDADES_VALIDAS)
        index = self.combo_actividad.findText(self.mecanico.actividad)
        if index >= 0:
            self.combo_actividad.setCurrentIndex(index)
        form_layout.addRow("Actividad:", self.combo_actividad)
        
        # Más información
        form_layout.addRow("Última actualización:", QLabel(self.mecanico.ultima_actualizacion.strftime("%d/%m/%Y %H:%M")))
        if hasattr(self.mecanico, 'fecha_contratacion') and self.mecanico.fecha_contratacion:
            form_layout.addRow("Fecha de contratación:", QLabel(self.mecanico.fecha_contratacion.strftime("%d/%m/%Y")))
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_guardar = QPushButton("Guardar cambios")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cerrar)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def guardar_cambios(self):
        """Guarda los cambios realizados al mecánico"""
        nueva_actividad = self.combo_actividad.currentText()
        
        # Actualizar la actividad del mecánico
        self.mecanico.actividad = nueva_actividad
        
        # Guardar en la base de datos
        try:
            self.mecanicos_dao.actualizar(self.mecanico)
            QMessageBox.information(self, "Éxito", "Cambios guardados correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron guardar los cambios: {str(e)}")

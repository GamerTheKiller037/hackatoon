from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtCore import QDate
from models.camion import Camion
from database.camiones_dao import CamionesDAO
from src.controllers.reparacion_controller import ReparacionController
from bson import ObjectId
import importlib

class DetalleCamionDialog(QDialog):
    def __init__(self, camion, parent=None):
        """
        Diálogo para mostrar y editar los detalles de un camión
        
        Args:
            camion: Objeto Camion a mostrar
            parent: Widget padre
        """
        super().__init__(parent)
        self.camion = camion
        self.camiones_dao = CamionesDAO()
        self.estado_anterior = camion.estado
        self.setWindowTitle(f"Detalles del Camión: {camion.matricula}")
        self.resize(400, 300)
        
        self.initUI()
        
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout()
        
        # Formulario de detalles
        form_layout = QFormLayout()
        
        # Información básica
        form_layout.addRow("Matrícula:", QLabel(self.camion.matricula))
        form_layout.addRow("Modelo:", QLabel(self.camion.modelo))
        form_layout.addRow("Año:", QLabel(str(self.camion.año)))
        
        # Estado (editable)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(Camion.ESTADOS_VALIDOS)
        index = self.combo_estado.findText(self.camion.estado)
        if index >= 0:
            self.combo_estado.setCurrentIndex(index)
        # Conectar el evento de cambio en el combobox
        self.combo_estado.currentTextChanged.connect(self.on_estado_changed)
        form_layout.addRow("Estado:", self.combo_estado)
        
        # Más información
        form_layout.addRow("Última actualización:", QLabel(self.camion.ultima_actualizacion.strftime("%d/%m/%Y %H:%M")))
        if hasattr(self.camion, 'fecha_adquisicion') and self.camion.fecha_adquisicion:
            form_layout.addRow("Fecha de adquisición:", QLabel(self.camion.fecha_adquisicion.strftime("%d/%m/%Y")))
        
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

    def on_estado_changed(self, nuevo_estado):
        """Manejador para cuando cambia el estado seleccionado"""
        # Si el estado seleccionado es "En Reparación" y antes no lo era, abrir el formulario inmediatamente
        if nuevo_estado == Camion.ESTADO_EN_REPARACION and self.estado_anterior != Camion.ESTADO_EN_REPARACION:
            # Mostrar mensaje informativo
            QMessageBox.information(
                self,
                "Nueva Reparación",
                "Para cambiar el estado a 'En Reparación', debe registrar los detalles de la reparación."
            )
            if not self.abrir_formulario_reparacion():
                # Si el formulario fue cancelado, volver al estado anterior
                self.combo_estado.setCurrentText(self.estado_anterior)
        
        # Si el camión pasa a otro estado, notificar el cambio a la ventana principal
        if nuevo_estado != self.estado_anterior:
            # Buscar la ventana principal para notificar el cambio
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'dashboard'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'dashboard'):
                # Actualizar el dashboard con el cambio de estado
                parent_window.refresh_data()
    
    def guardar_cambios(self):
        """Guarda los cambios realizados al camión"""
        nuevo_estado = self.combo_estado.currentText()
        
        # Actualizar el estado del camión (ya validado en on_estado_changed)
        self.camion.estado = nuevo_estado
        
        # Guardar en la base de datos
        try:
            self.camiones_dao.actualizar(self.camion)
            
            # Notificar a la ventana principal sobre la actualización
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'dashboard'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'dashboard'):
                parent_window.dashboard.agregar_actividad('camion', self.camion, "Cambio de estado")
                parent_window.refresh_data()
            
            QMessageBox.information(self, "Éxito", "Cambios guardados correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron guardar los cambios: {str(e)}")

    def abrir_formulario_reparacion(self):
        """
        Abre el formulario de reparación para el camión actual
        
        Returns:
            bool: True si se completó la reparación, False si se canceló
        """
        try:
            # Importación dinámica para evitar la circular
            FormReparacionModule = importlib.import_module('views.reparaciones.form_reparacion')
            FormReparaciones = getattr(FormReparacionModule, 'FormReparaciones')
            
            # Crear datos iniciales para la reparación
            # Convertir ObjectId a string para compatibilidad con el formulario
            camion_id = str(self.camion.id) if isinstance(self.camion.id, ObjectId) else self.camion.id
            
            datos_reparacion = {
                # No incluir ID, el controlador lo generará
                'camion_id': camion_id,
                'matricula': self.camion.matricula,
                'modelo': self.camion.modelo,
                'anio': self.camion.año,
                'estado': Camion.ESTADO_EN_REPARACION,
                'fecha_ingreso': QDate.currentDate().toString('yyyy-MM-dd')
            }
            
            # Instanciar el controlador de reparaciones
            controller = ReparacionController()
            
            # Mostrar el formulario (pasando los datos iniciales)
            dialog = FormReparaciones(controller, datos_reparacion, self)
            
            if dialog.exec_():
                # La reparación fue registrada correctamente
                
                # Notificar a la ventana principal que debe actualizar la lista de reparaciones
                # Esto depende de cómo esté estructurada tu aplicación, pero podrías:
                # 1. Emitir una señal (si usas señales de PyQt)
                # 2. Acceder directamente a la ventana principal y llamar a un método
                
                # Por ejemplo, si tienes acceso a la ventana principal:
                main_window = self.parent()
                if hasattr(main_window, 'reparaciones_widget') and main_window.reparaciones_widget:
                    main_window.reparaciones_widget.cargarReparaciones()
                
                return True
            else:
                # El usuario canceló el formulario
                QMessageBox.warning(
                    self,
                    "Cambio de Estado Cancelado",
                    "No se puede cambiar el estado a 'En Reparación' sin registrar los detalles de la reparación."
                )
                return False
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error detallado: {error_detallado}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de reparación: {str(e)}")
            return False
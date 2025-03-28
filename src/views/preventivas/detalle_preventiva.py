from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QPushButton, QComboBox, QMessageBox, 
                           QTabWidget, QWidget, QGroupBox, QFrame)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor
from models.preventiva import Preventiva
from database.preventivas_dao import PreventivasDAO
from controllers.reparacion_controller import ReparacionController
from bson import ObjectId
import importlib
import logging

class DetallePreventiva(QDialog):
    def __init__(self, preventiva, parent=None):
        """
        Diálogo para mostrar y editar los detalles de una tarea preventiva
        
        Args:
            preventiva: Objeto Preventiva a mostrar
            parent: Widget padre
        """
        super().__init__(parent)
        self.preventiva = preventiva
        self.preventivas_dao = PreventivasDAO()
        self.estado_anterior = preventiva.estado
        self.nivel_urgencia_anterior = preventiva.nivel_urgencia
        self.setWindowTitle(f"Detalles de Mantenimiento Preventivo - {preventiva.matricula}")
        self.resize(600, 500)  # Tamaño aumentado
        
        # Establecer fuente más grande para todo el diálogo
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        
        self.initUI()
        
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Barra superior morada
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #6a1b9a;")
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Título en la barra morada
        title_label = QLabel(f"Información del Mantenimiento Preventivo")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Pestañas
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 15px;
                margin-right: 2px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #6a1b9a;
                color: white;
            }
        """)
        
        # Pestaña de Información General
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        # Grupo: Datos Básicos
        datos_group = QGroupBox("Datos Básicos")
        datos_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        form_layout = QFormLayout(datos_group)
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignLeft)  # Alineación a la izquierda
        form_layout.setFormAlignment(Qt.AlignLeft)   # Alineación a la izquierda
        
        # Aplicar estilo a las etiquetas
        label_style = "font-weight: bold; color: #444444;"
        value_style = "font-size: 12px;"
        
        # Matrícula
        matricula_label = QLabel(self.preventiva.matricula)
        matricula_label.setStyleSheet(value_style)
        matricula_label_title = QLabel("Matrícula:")
        matricula_label_title.setStyleSheet(label_style)
        form_layout.addRow(matricula_label_title, matricula_label)
        
        # Modelo
        modelo_label = QLabel(self.preventiva.modelo)
        modelo_label.setStyleSheet(value_style)
        modelo_label_title = QLabel("Modelo:")
        modelo_label_title.setStyleSheet(label_style)
        form_layout.addRow(modelo_label_title, modelo_label)
        
        # Tipo
        tipo_label = QLabel(self.preventiva.tipo)
        tipo_label.setStyleSheet(value_style)
        tipo_label_title = QLabel("Tipo:")
        tipo_label_title.setStyleSheet(label_style)
        form_layout.addRow(tipo_label_title, tipo_label)
        
        # Estado (editable)
        self.combo_estado = QComboBox()
        self.combo_estado.setStyleSheet("padding: 5px; font-size: 12px;")
        self.combo_estado.addItems(Preventiva.ESTADOS_VALIDOS)
        index = self.combo_estado.findText(self.preventiva.estado)
        if index >= 0:
            self.combo_estado.setCurrentIndex(index)
        # Conectar el evento de cambio en el combobox
        self.combo_estado.currentTextChanged.connect(self.on_estado_changed)
        
        estado_label_title = QLabel("Estado:")
        estado_label_title.setStyleSheet(label_style)
        form_layout.addRow(estado_label_title, self.combo_estado)
        
        # Nivel de urgencia (editable)
        self.combo_urgencia = QComboBox()
        self.combo_urgencia.setStyleSheet("padding: 5px; font-size: 12px;")
        self.combo_urgencia.addItems(Preventiva.NIVELES_URGENCIA)
        index = self.combo_urgencia.findText(self.preventiva.nivel_urgencia)
        if index >= 0:
            self.combo_urgencia.setCurrentIndex(index)
        
        urgencia_label_title = QLabel("Nivel de urgencia:")
        urgencia_label_title.setStyleSheet(label_style)
        form_layout.addRow(urgencia_label_title, self.combo_urgencia)
        
        # Fecha de registro
        fecha_registro_label = QLabel(self.preventiva.fecha_registro.strftime("%d/%m/%Y %H:%M"))
        fecha_registro_label.setStyleSheet(value_style)
        fecha_registro_label_title = QLabel("Fecha de registro:")
        fecha_registro_label_title.setStyleSheet(label_style)
        form_layout.addRow(fecha_registro_label_title, fecha_registro_label)
        
        # Última actualización de reparación
        ultima_act_str = "Sin actualizaciones"
        if self.preventiva.ultima_actualizacion_reparacion:
            ultima_act_str = self.preventiva.ultima_actualizacion_reparacion.strftime("%d/%m/%Y %H:%M")
        
        ultima_actualizacion_label = QLabel(ultima_act_str)
        ultima_actualizacion_label.setStyleSheet(value_style)
        ultima_act_label_title = QLabel("Última actualización de reparación:")
        ultima_act_label_title.setStyleSheet(label_style)
        form_layout.addRow(ultima_act_label_title, ultima_actualizacion_label)
        
        info_layout.addWidget(datos_group)
        
        # Grupo: Estadísticas
        stats_group = QGroupBox("Estadísticas")
        stats_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        stats_layout = QFormLayout(stats_group)
        stats_layout.setVerticalSpacing(12)
        stats_layout.setLabelAlignment(Qt.AlignLeft)  # Alineación a la izquierda
        stats_layout.setFormAlignment(Qt.AlignLeft)   # Alineación a la izquierda
        
        # Calcular estadísticas (usamos valores de ejemplo, reemplazar por datos reales)
        # En un entorno real, estos datos vendrían de la base de datos
        total_reparaciones = 0  # Obtener desde la base de datos
        reparaciones_activas = 0  # Obtener desde la base de datos
        ultima_reparacion = "Sin actualizaciones"  # Obtener desde la base de datos
        
        # Total de reparaciones
        total_rep_label = QLabel(str(total_reparaciones))
        total_rep_label.setStyleSheet(value_style)
        total_rep_label_title = QLabel("Total de actualizaciones:")
        total_rep_label_title.setStyleSheet(label_style)
        stats_layout.addRow(total_rep_label_title, total_rep_label)
        
        # Reparaciones activas
        rep_activas_label = QLabel(str(reparaciones_activas))
        rep_activas_label.setStyleSheet(value_style)
        rep_activas_label_title = QLabel("Actualizaciones pendientes:")
        rep_activas_label_title.setStyleSheet(label_style)
        stats_layout.addRow(rep_activas_label_title, rep_activas_label)
        
        # Última reparación
        ultima_rep_label = QLabel(ultima_reparacion)
        ultima_rep_label.setStyleSheet(value_style)
        ultima_rep_label_title = QLabel("Última actualización:")
        ultima_rep_label_title.setStyleSheet(label_style)
        stats_layout.addRow(ultima_rep_label_title, ultima_rep_label)
        
        info_layout.addWidget(stats_group)
        
        # Pestaña de Historial de Actualizaciones de Reparaciones
        historial_tab = QWidget()
        historial_layout = QVBoxLayout(historial_tab)
        
        # Implementar historial de actualizaciones de reparaciones aquí
        historial_placeholder = QLabel("No hay actualizaciones de reparaciones para mostrar")
        historial_placeholder.setAlignment(Qt.AlignCenter)
        historial_placeholder.setStyleSheet("font-size: 13px; color: gray;")
        historial_layout.addWidget(historial_placeholder)
        
        # Añadir pestañas al widget
        tab_widget.addTab(info_tab, "Información General")
        tab_widget.addTab(historial_tab, "Historial de Actualizaciones de Reparaciones")
        
        main_layout.addWidget(tab_widget)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.btn_guardar = QPushButton("Guardar cambios")
        self.btn_guardar.setMinimumHeight(35)
        self.btn_guardar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 16px; font-size: 13px; border-radius: 4px;")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setMinimumHeight(35)
        self.btn_cerrar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; font-size: 13px; border-radius: 4px;")
        self.btn_cerrar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cerrar)
        
        main_layout.addLayout(button_layout)

    def on_estado_changed(self, nuevo_estado):
        """Manejador para cuando cambia el estado seleccionado"""
        # Si el estado seleccionado es "En Reparación" y antes no lo era, abrir el formulario inmediatamente
        if nuevo_estado == Preventiva.ESTADO_EN_REPARACION and self.estado_anterior != Preventiva.ESTADO_EN_REPARACION:
            # Mostrar mensaje informativo
            QMessageBox.information(
                self,
                "Nueva Actualización de Reparación",
                "Para cambiar el estado a 'En Reparación', debe registrar los detalles de la actualización."
            )
            if not self.abrir_formulario_reparacion():
                # Si el formulario fue cancelado, volver al estado anterior
                self.combo_estado.setCurrentText(self.estado_anterior)
        
        # Si la preventiva pasa a otro estado, notificar el cambio a la ventana principal
        if nuevo_estado != self.estado_anterior:
            # Buscar la ventana principal para notificar el cambio
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'dashboard'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'dashboard'):
                # Actualizar el dashboard con el cambio de estado
                parent_window.refresh_data()
    
    def guardar_cambios(self):
        """Guarda los cambios realizados a la preventiva"""
        nuevo_estado = self.combo_estado.currentText()
        nuevo_nivel_urgencia = self.combo_urgencia.currentText()
        
        # Actualizar el estado y nivel de urgencia de la preventiva
        self.preventiva.estado = nuevo_estado
        self.preventiva.nivel_urgencia = nuevo_nivel_urgencia
        
        # Guardar en la base de datos
        try:
            self.preventivas_dao.actualizar(self.preventiva)
            
            # Notificar a la ventana principal sobre la actualización
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'dashboard'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'dashboard'):
                parent_window.dashboard.agregar_actividad('preventiva', self.preventiva, "Cambio de estado/urgencia")
                parent_window.refresh_data()
            
            QMessageBox.information(self, "Éxito", "Cambios guardados correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron guardar los cambios: {str(e)}")

    def abrir_formulario_reparacion(self):
        """
        Abre el formulario de reparación para la preventiva actual
        
        Returns:
            bool: True si se completó la reparación, False si se canceló
        """
        try:
            # Importación dinámica para evitar la circular
            FormReparacionModule = importlib.import_module('views.reparaciones.form_reparacion')
            FormReparaciones = getattr(FormReparacionModule, 'FormReparaciones')
            
            # Crear datos iniciales para la reparación
            # Convertir ObjectId a string para compatibilidad con el formulario
            preventiva_id = str(self.preventiva.id) if isinstance(self.preventiva.id, ObjectId) else self.preventiva.id
            
            datos_reparacion = {
                # No incluir ID, el controlador lo generará
                'preventiva_id': preventiva_id,
                'matricula': self.preventiva.matricula,
                'modelo': self.preventiva.modelo,
                'tipo': self.preventiva.tipo,
                'estado': Preventiva.ESTADO_EN_REPARACION,
                'fecha_ingreso': QDate.currentDate().toString('yyyy-MM-dd')
            }
            
            # Instanciar el controlador de reparaciones
            controller = ReparacionController()
            
            # Mostrar el formulario (pasando los datos iniciales)
            dialog = FormReparaciones(controller, datos_reparacion, self)
            
            if dialog.exec_():
                # La reparación fue registrada correctamente
                
                # Notificar a la ventana principal que debe actualizar la lista de reparaciones
                main_window = self.parent()
                if hasattr(main_window, 'reparaciones_widget') and main_window.reparaciones_widget:
                    main_window.reparaciones_widget.cargarReparaciones()
                
                return True
            else:
                # El usuario canceló el formulario
                QMessageBox.warning(
                    self,
                    "Cambio de Estado Cancelado",
                    "No se puede cambiar el estado a 'En Reparación' sin registrar los detalles de la actualización."
                )
                return False
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error detallado: {error_detallado}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario de reparación: {str(e)}")
            return False
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QPushButton, QComboBox, QMessageBox, 
                           QTabWidget, QWidget, QGroupBox, QFrame)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor
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
        self.setWindowTitle(f"Detalles del Camión - {camion.matricula}")
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
        title_label = QLabel(f"Información del Camión")
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
        matricula_label = QLabel(self.camion.matricula)
        matricula_label.setStyleSheet(value_style)
        matricula_label_title = QLabel("Matrícula:")
        matricula_label_title.setStyleSheet(label_style)
        form_layout.addRow(matricula_label_title, matricula_label)
        
        # Modelo
        modelo_label = QLabel(self.camion.modelo)
        modelo_label.setStyleSheet(value_style)
        modelo_label_title = QLabel("Modelo:")
        modelo_label_title.setStyleSheet(label_style)
        form_layout.addRow(modelo_label_title, modelo_label)
        
        # Año
        año_label = QLabel(str(self.camion.año))
        año_label.setStyleSheet(value_style)
        año_label_title = QLabel("Año:")
        año_label_title.setStyleSheet(label_style)
        form_layout.addRow(año_label_title, año_label)
        
        # Estado (editable)
        self.combo_estado = QComboBox()
        self.combo_estado.setStyleSheet("padding: 5px; font-size: 12px;")
        self.combo_estado.addItems(Camion.ESTADOS_VALIDOS)
        index = self.combo_estado.findText(self.camion.estado)
        if index >= 0:
            self.combo_estado.setCurrentIndex(index)
        # Conectar el evento de cambio en el combobox
        self.combo_estado.currentTextChanged.connect(self.on_estado_changed)
        
        estado_label_title = QLabel("Estado:")
        estado_label_title.setStyleSheet(label_style)
        form_layout.addRow(estado_label_title, self.combo_estado)
        
        # Fecha de registro
        fecha_registro_label = QLabel(self.camion.fecha_registro.strftime("%d/%m/%Y %H:%M"))
        fecha_registro_label.setStyleSheet(value_style)
        fecha_registro_label_title = QLabel("Fecha de registro:")
        fecha_registro_label_title.setStyleSheet(label_style)
        form_layout.addRow(fecha_registro_label_title, fecha_registro_label)
        
        # Última actualización
        ultima_actualizacion_label = QLabel(self.camion.ultima_actualizacion.strftime("%d/%m/%Y %H:%M"))
        ultima_actualizacion_label.setStyleSheet(value_style)
        ultima_act_label_title = QLabel("Última actualización:")
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
        ultima_reparacion = "Sin reparaciones"  # Obtener desde la base de datos
        
        # Total de reparaciones
        total_rep_label = QLabel(str(total_reparaciones))
        total_rep_label.setStyleSheet(value_style)
        total_rep_label_title = QLabel("Total de reparaciones:")
        total_rep_label_title.setStyleSheet(label_style)
        stats_layout.addRow(total_rep_label_title, total_rep_label)
        
        # Reparaciones activas
        rep_activas_label = QLabel(str(reparaciones_activas))
        rep_activas_label.setStyleSheet(value_style)
        rep_activas_label_title = QLabel("Reparaciones activas:")
        rep_activas_label_title.setStyleSheet(label_style)
        stats_layout.addRow(rep_activas_label_title, rep_activas_label)
        
        # Última reparación
        ultima_rep_label = QLabel(ultima_reparacion)
        ultima_rep_label.setStyleSheet(value_style)
        ultima_rep_label_title = QLabel("Última reparación:")
        ultima_rep_label_title.setStyleSheet(label_style)
        stats_layout.addRow(ultima_rep_label_title, ultima_rep_label)
        
        info_layout.addWidget(stats_group)
        
        # Pestaña de Historial de Reparaciones
        historial_tab = QWidget()
        historial_layout = QVBoxLayout(historial_tab)
        
        # Implementar historial de reparaciones aquí
        historial_placeholder = QLabel("No hay reparaciones para mostrar")
        historial_placeholder.setAlignment(Qt.AlignCenter)
        historial_placeholder.setStyleSheet("font-size: 13px; color: gray;")
        historial_layout.addWidget(historial_placeholder)
        
        # Añadir pestañas al widget
        tab_widget.addTab(info_tab, "Información General")
        tab_widget.addTab(historial_tab, "Historial de Reparaciones")
        
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
            # Actualizar la UI
            self.actualizar_estado_ui()
    
    def actualizar_estado_ui(self):
        """
        Actualiza la UI después de un cambio de estado
        """
        # Notificar a la ventana principal sobre cambios
        try:
            # Buscar la ventana principal
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'dashboard'):
                main_window = main_window.parent()
            
            if main_window:
                if hasattr(main_window, 'dashboard'):
                    main_window.dashboard.agregar_actividad('camion', self.camion, "Cambio de estado")
                    
                if hasattr(main_window, 'refresh_data'):
                    print("Actualizando datos en la ventana principal...")
                    main_window.refresh_data()
                    
                if hasattr(main_window, 'reparaciones_widget') and main_window.reparaciones_widget:
                    print("Actualizando lista de reparaciones en la ventana principal...")
                    main_window.reparaciones_widget.cargarReparaciones()
        except Exception as e:
            print(f"Error al actualizar UI después de cambio de estado: {str(e)}")
            # No mostrar este error al usuario, solo registrarlo
    
    def guardar_cambios(self):
        """Guarda los cambios realizados al camión"""
        nuevo_estado = self.combo_estado.currentText()
        
        # Actualizar el estado del camión (ya validado en on_estado_changed)
        self.camion.estado = nuevo_estado
        
        # Guardar en la base de datos
        try:
            self.camiones_dao.actualizar(self.camion)
            
            # Notificar a la ventana principal sobre la actualización
            self.actualizar_estado_ui()
            
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
            dialog.setWindowTitle(f"Nueva Reparación - Camión {self.camion.matricula}")
            
            if dialog.exec_():
                # La reparación fue registrada correctamente
                
                # Actualizar la UI después de crear la reparación
                self.actualizar_estado_ui()
                
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
    
    def actualizar_estado_ui(self):
        """
        Actualiza la UI después de un cambio de estado
        """
        # Notificar a la ventana principal sobre cambios
        try:
            # Buscar la ventana principal
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'dashboard'):
                main_window = main_window.parent()
            
            if main_window:
                if hasattr(main_window, 'dashboard'):
                    main_window.dashboard.agregar_actividad('camion', self.camion, "Cambio de estado")
                    
                if hasattr(main_window, 'refresh_data'):
                    print("Actualizando datos en la ventana principal...")
                    main_window.refresh_data()
                    
                if hasattr(main_window, 'reparaciones_widget') and main_window.reparaciones_widget:
                    print("Actualizando lista de reparaciones en la ventana principal...")
                    main_window.reparaciones_widget.cargarReparaciones()
        except Exception as e:
            print(f"Error al actualizar UI después de cambio de estado: {str(e)}")
            # No mostrar este error al usuario, solo registrarlo
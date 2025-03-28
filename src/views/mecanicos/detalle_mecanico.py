from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QPushButton, QComboBox, QMessageBox, QFrame,
                           QTabWidget, QWidget, QGroupBox)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
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
        self.resize(600, 500)
        
        # Establecer fuente más grande para todo el diálogo
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        
        self.initUI()
        
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes para que la barra ocupe todo el ancho
        main_layout.setSpacing(0)  # Sin espacio entre la barra y el contenido
        
        # Barra superior morada
        header = QFrame()
        header.setStyleSheet("background-color: #6a1b9a;")
        header.setFixedHeight(80)  # Altura fija para la barra superior
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Título en la barra morada
        title_label = QLabel("Información del Mecánico")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Contenido principal con pestañas
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
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
        label_style = "font-weight: bold; color: #444444; font-size: 18px;"
        value_style = "font-size: 16px;"
        
        # ID
        id_label = QLabel(str(self.mecanico.id))
        id_label.setStyleSheet(value_style)
        id_title = QLabel("ID:")
        id_title.setStyleSheet(label_style)
        form_layout.addRow(id_title, id_label)
        
        # Nombre
        nombre_label = QLabel(self.mecanico.nombre)
        nombre_label.setStyleSheet(value_style)
        nombre_title = QLabel("Nombre:")
        nombre_title.setStyleSheet(label_style)
        form_layout.addRow(nombre_title, nombre_label)
        
        # Apellidos
        apellidos_label = QLabel(self.mecanico.apellidos)
        apellidos_label.setStyleSheet(value_style)
        apellidos_title = QLabel("Apellidos:")
        apellidos_title.setStyleSheet(label_style)
        form_layout.addRow(apellidos_title, apellidos_label)
        
        # Actividad (editable)
        actividad_title = QLabel("Actividad:")
        actividad_title.setStyleSheet(label_style)
        self.combo_actividad = QComboBox()
        self.combo_actividad.setStyleSheet("padding: 5px; font-size: 16px;")
        self.combo_actividad.setMinimumHeight(35)
        self.combo_actividad.addItems(Mecanico.ACTIVIDADES_VALIDAS)
        index = self.combo_actividad.findText(self.mecanico.actividad)
        if index >= 0:
            self.combo_actividad.setCurrentIndex(index)
        form_layout.addRow(actividad_title, self.combo_actividad)
        
        # Última actualización
        ultima_actualizacion_title = QLabel("Última actualización:")
        ultima_actualizacion_title.setStyleSheet(label_style)
        ultima_actualizacion_label = QLabel(self.mecanico.ultima_actualizacion.strftime("%d/%m/%Y %H:%M"))
        ultima_actualizacion_label.setStyleSheet(value_style)
        form_layout.addRow(ultima_actualizacion_title, ultima_actualizacion_label)
        
        # Fecha de contratación (si existe)
        if hasattr(self.mecanico, 'fecha_contratacion') and self.mecanico.fecha_contratacion:
            fecha_contratacion_title = QLabel("Fecha de contratación:")
            fecha_contratacion_title.setStyleSheet(label_style)
            fecha_contratacion_label = QLabel(self.mecanico.fecha_contratacion.strftime("%d/%m/%Y"))
            fecha_contratacion_label.setStyleSheet(value_style)
            form_layout.addRow(fecha_contratacion_title, fecha_contratacion_label)
        
        info_layout.addWidget(datos_group)
        
        # Pestaña de Historial de Actividades
        historial_tab = QWidget()
        historial_layout = QVBoxLayout(historial_tab)
        
        # Implementar historial de actividades aquí
        historial_placeholder = QLabel("No hay actividades para mostrar")
        historial_placeholder.setAlignment(Qt.AlignCenter)
        historial_placeholder.setStyleSheet("font-size: 16px; color: gray;")
        historial_layout.addWidget(historial_placeholder)
        
        # Añadir pestañas al widget
        tab_widget.addTab(info_tab, "Información General")
        tab_widget.addTab(historial_tab, "Historial de Actividades")
        
        content_layout.addWidget(tab_widget)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.btn_guardar = QPushButton("Guardar cambios")
        self.btn_guardar.setMinimumHeight(40)
        self.btn_guardar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px;")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setMinimumHeight(40)
        self.btn_cerrar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px;")
        self.btn_cerrar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cerrar)
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_widget)
    
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
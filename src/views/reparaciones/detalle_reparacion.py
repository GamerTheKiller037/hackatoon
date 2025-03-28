#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo para mostrar los detalles de una reparación.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QDialogButtonBox, 
                           QFormLayout, QGroupBox, QTextBrowser, QTabWidget,
                           QWidget, QPushButton, QMessageBox, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from database.reparaciones_dao import ReparacionesDAO
from database.camiones_dao import CamionesDAO
from database.usuarios_dao import UsuariosDAO
from models.reparacion import Reparacion
from models.camion import Camion
from models.usuario import Usuario

class DetalleReparacionDialog(QDialog):
    """Diálogo para mostrar los detalles de una reparación"""
    
    def __init__(self, reparacion, parent=None):
        """
        Inicializa el diálogo de detalles de reparación.
        
        Args:
            reparacion (Reparacion): Reparación a mostrar.
            parent (QWidget, optional): Widget padre.
        """
        super().__init__(parent)
        
        self.reparacion = reparacion
        self.reparaciones_dao = ReparacionesDAO()
        self.camiones_dao = CamionesDAO()
        self.usuarios_dao = UsuariosDAO()
        
        self.setup_ui()
        self.load_data()
        
        self.setWindowTitle(f"Detalles de Reparación #{self.reparacion.id_falla}")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setMinimumSize(700, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Establecer fuente más grande para todo el diálogo
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        
        # Layout principal
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
        title_label = QLabel(f"Detalles de la Reparación #{self.reparacion.id_falla}")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Contenido principal con pestañas
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Tabs para organizar la información
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
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
        
        # Tab: Información General
        self.info_tab = QWidget()
        self.setup_info_tab()
        self.tab_widget.addTab(self.info_tab, "Información General")
        
        # Tab: Notas y Seguimiento
        self.notes_tab = QWidget()
        self.setup_notes_tab()
        self.tab_widget.addTab(self.notes_tab, "Notas y Seguimiento")
        
        content_layout.addWidget(self.tab_widget)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Botón para cambiar estado
        self.change_status_button = QPushButton("Cambiar Estado")
        self.change_status_button.setMinimumHeight(40)
        self.change_status_button.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px;")
        self.change_status_button.clicked.connect(self.on_change_status)
        button_layout.addWidget(self.change_status_button)
        
        # Botón cerrar
        self.close_button = QPushButton("Cerrar")
        self.close_button.setMinimumHeight(40)
        self.close_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px;")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_widget)
    
    def setup_info_tab(self):
        """Configura la pestaña de información general"""
        layout = QVBoxLayout(self.info_tab)
        
        # Grupo: Datos básicos
        basic_group = QGroupBox("Datos Básicos")
        basic_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        form_layout = QFormLayout(basic_group)
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        
        # Estilos
        label_style = "font-weight: bold; color: #444444; font-size: 18px;"
        value_style = "font-size: 16px;"
        
        # ID de falla
        self.id_falla_label = QLabel()
        self.id_falla_label.setStyleSheet(value_style)
        id_falla_title = QLabel("ID de falla:")
        id_falla_title.setStyleSheet(label_style)
        form_layout.addRow(id_falla_title, self.id_falla_label)
        
        # Camión
        self.camion_label = QLabel()
        self.camion_label.setStyleSheet(value_style)
        camion_title = QLabel("Camión:")
        camion_title.setStyleSheet(label_style)
        form_layout.addRow(camion_title, self.camion_label)
        
        # Motivo de falla
        self.motivo_falla_label = QLabel()
        self.motivo_falla_label.setStyleSheet(value_style)
        motivo_title = QLabel("Motivo de falla:")
        motivo_title.setStyleSheet(label_style)
        form_layout.addRow(motivo_title, self.motivo_falla_label)
        
        layout.addWidget(basic_group)
        
        # Grupo: Descripción
        desc_group = QGroupBox("Descripción")
        desc_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        desc_layout = QVBoxLayout(desc_group)
        
        self.descripcion_browser = QTextBrowser()
        self.descripcion_browser.setReadOnly(True)
        self.descripcion_browser.setStyleSheet("font-size: 16px;")
        desc_layout.addWidget(self.descripcion_browser)
        
        layout.addWidget(desc_group)
        
        # Grupo: Estado y Fechas
        status_group = QGroupBox("Estado y Fechas")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        status_layout = QFormLayout(status_group)
        status_layout.setVerticalSpacing(12)
        status_layout.setLabelAlignment(Qt.AlignLeft)
        status_layout.setFormAlignment(Qt.AlignLeft)
        
        # Estado
        self.estado_label = QLabel()
        self.estado_label.setStyleSheet(value_style)
        estado_title = QLabel("Estado:")
        estado_title.setStyleSheet(label_style)
        status_layout.addRow(estado_title, self.estado_label)
        
        # Mecánico
        self.mecanico_label = QLabel()
        self.mecanico_label.setStyleSheet(value_style)
        mecanico_title = QLabel("Mecánico responsable:")
        mecanico_title.setStyleSheet(label_style)
        status_layout.addRow(mecanico_title, self.mecanico_label)
        
        # Tiempo estimado
        self.tiempo_estimado_label = QLabel()
        self.tiempo_estimado_label.setStyleSheet(value_style)
        tiempo_title = QLabel("Tiempo estimado:")
        tiempo_title.setStyleSheet(label_style)
        status_layout.addRow(tiempo_title, self.tiempo_estimado_label)
        
        # Fecha de entrada
        self.fecha_entrada_label = QLabel()
        self.fecha_entrada_label.setStyleSheet(value_style)
        fecha_entrada_title = QLabel("Fecha de entrada:")
        fecha_entrada_title.setStyleSheet(label_style)
        status_layout.addRow(fecha_entrada_title, self.fecha_entrada_label)
        
        # Fecha de salida
        self.fecha_salida_label = QLabel()
        self.fecha_salida_label.setStyleSheet(value_style)
        fecha_salida_title = QLabel("Fecha de salida:")
        fecha_salida_title.setStyleSheet(label_style)
        status_layout.addRow(fecha_salida_title, self.fecha_salida_label)
        
        layout.addWidget(status_group)
    
    def setup_notes_tab(self):
        """Configura la pestaña de notas y seguimiento"""
        layout = QVBoxLayout(self.notes_tab)
        
        # Título
        notes_title = QLabel("Notas y Seguimiento")
        notes_title.setAlignment(Qt.AlignCenter)
        notes_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(notes_title)
        
        # Notas adicionales
        notes_group = QGroupBox("Notas Adicionales")
        notes_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notas_browser = QTextBrowser()
        self.notas_browser.setReadOnly(True)
        self.notas_browser.setStyleSheet("font-size: 16px;")
        notes_layout.addWidget(self.notas_browser)
        
        layout.addWidget(notes_group)
    
    def load_data(self):
        """Carga los datos de la reparación"""
        # Datos básicos
        self.id_falla_label.setText(self.reparacion.id_falla)
        self.motivo_falla_label.setText(self.reparacion.motivo_falla)
        
        # Buscar información del camión
        camion = self.camiones_dao.obtener_por_id(self.reparacion.camion_id)
        if camion:
            self.camion_label.setText(f"{camion.matricula} - {camion.modelo}")
        else:
            self.camion_label.setText("Camión no encontrado")
        
        # Descripción
        self.descripcion_browser.setText(self.reparacion.descripcion)
        
        # Estado (con formato de color)
        estado_text = self.reparacion.estado
        if self.reparacion.estado == Reparacion.ESTADO_EN_ESPERA:
            estado_text = f'<span style="color: orange;">{estado_text}</span>'
        elif self.reparacion.estado == Reparacion.ESTADO_EN_REPARACION:
            estado_text = f'<span style="color: red;">{estado_text}</span>'
        elif self.reparacion.estado == Reparacion.ESTADO_REPARADO:
            estado_text = f'<span style="color: green;">{estado_text}</span>'
        
        self.estado_label.setText(estado_text)
        self.estado_label.setTextFormat(Qt.RichText)
        
        # Mecánico
        if self.reparacion.mecanico_id:
            mecanico = self.usuarios_dao.obtener_por_id(self.reparacion.mecanico_id)
            if mecanico:
                self.mecanico_label.setText(f"{mecanico.nombre} {mecanico.apellido}")
            else:
                self.mecanico_label.setText("Mecánico no encontrado")
        else:
            self.mecanico_label.setText("No asignado")
        
        # Tiempo estimado
        if self.reparacion.tiempo_estimado is not None:
            self.tiempo_estimado_label.setText(f"{self.reparacion.tiempo_estimado} horas")
        else:
            self.tiempo_estimado_label.setText("No especificado")
        
        # Fechas
        self.fecha_entrada_label.setText(
            self.reparacion.fecha_entrada.strftime("%d/%m/%Y %H:%M")
        )
        
        if self.reparacion.fecha_salida:
            self.fecha_salida_label.setText(
                self.reparacion.fecha_salida.strftime("%d/%m/%Y %H:%M")
            )
        else:
            self.fecha_salida_label.setText("Pendiente")
        
        # Notas
        if self.reparacion.notas_adicionales:
            self.notas_browser.setText(self.reparacion.notas_adicionales)
        else:
            self.notas_browser.setText("No hay notas adicionales.")
    
    def on_change_status(self):
        """Maneja el evento de cambio de estado"""
        from PyQt5.QtWidgets import QInputDialog
        
        # Crear un diálogo para cambiar el estado
        estados = Reparacion.ESTADOS_VALIDOS
        estado_actual_index = estados.index(self.reparacion.estado)
        
        estado_seleccionado, ok = QInputDialog.getItem(
            self,
            "Cambiar Estado",
            "Seleccione el nuevo estado:",
            estados,
            estado_actual_index,
            False
        )
        
        if ok and estado_seleccionado != self.reparacion.estado:
            # Solicitar notas adicionales
            notas, ok = QInputDialog.getText(
                self,
                "Notas",
                "Agregar notas sobre este cambio (opcional):"
            )
            
            # Cambiar el estado
            if self.reparaciones_dao.cambiar_estado(
                self.reparacion.id, 
                estado_seleccionado,
                notas if ok and notas else None
            ):
                QMessageBox.information(
                    self,
                    "Estado actualizado",
                    f"El estado de la reparación ha sido actualizado a '{estado_seleccionado}'."
                )
                
                # Recargar la reparación para ver los cambios
                self.reparacion = self.reparaciones_dao.obtener_por_id(self.reparacion.id)
                self.load_data()
            else:
                QMessageBox.warning(
                    self,
                    "Error al actualizar",
                    "No se pudo actualizar el estado de la reparación."
                )
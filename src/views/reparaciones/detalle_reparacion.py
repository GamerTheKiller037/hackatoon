#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo para mostrar los detalles de una reparación.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QDialogButtonBox, 
                           QFormLayout, QGroupBox, QTextBrowser, QTabWidget,
                           QWidget, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
        
        self.setWindowTitle(f"Detalles de Reparación - {self.reparacion.id_falla}")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setMinimumSize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Tabs para organizar la información
        self.tab_widget = QTabWidget()
        
        # Tab: Información General
        self.info_tab = QWidget()
        self.setup_info_tab()
        self.tab_widget.addTab(self.info_tab, "Información General")
        
        # Tab: Notas y Seguimiento
        self.notes_tab = QWidget()
        self.setup_notes_tab()
        self.tab_widget.addTab(self.notes_tab, "Notas y Seguimiento")
        
        main_layout.addWidget(self.tab_widget)
        
        # Botones
        buttons_layout = QVBoxLayout()
        
        # Botón para cambiar estado
        self.change_status_button = QPushButton("Cambiar Estado")
        self.change_status_button.clicked.connect(self.on_change_status)
        buttons_layout.addWidget(self.change_status_button)
        
        # Botones estándar
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(button_box)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_info_tab(self):
        """Configura la pestaña de información general"""
        layout = QVBoxLayout(self.info_tab)
        
        # Título
        title_label = QLabel("Información de la Reparación")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Grupo: Datos básicos
        basic_group = QGroupBox("Datos Básicos")
        form_layout = QFormLayout(basic_group)
        
        # ID de falla
        self.id_falla_label = QLabel()
        self.id_falla_label.setStyleSheet("font-weight: bold;")
        form_layout.addRow("ID de falla:", self.id_falla_label)
        
        # Camión
        self.camion_label = QLabel()
        form_layout.addRow("Camión:", self.camion_label)
        
        # Motivo de falla
        self.motivo_falla_label = QLabel()
        form_layout.addRow("Motivo de falla:", self.motivo_falla_label)
        
        layout.addWidget(basic_group)
        
        # Grupo: Descripción
        desc_group = QGroupBox("Descripción")
        desc_layout = QVBoxLayout(desc_group)
        
        self.descripcion_browser = QTextBrowser()
        self.descripcion_browser.setReadOnly(True)
        desc_layout.addWidget(self.descripcion_browser)
        
        layout.addWidget(desc_group)
        
        # Grupo: Estado y Fechas
        status_group = QGroupBox("Estado y Fechas")
        status_layout = QFormLayout(status_group)
        
        # Estado
        self.estado_label = QLabel()
        status_layout.addRow("Estado:", self.estado_label)
        
        # Mecánico
        self.mecanico_label = QLabel()
        status_layout.addRow("Mecánico responsable:", self.mecanico_label)
        
        # Tiempo estimado
        self.tiempo_estimado_label = QLabel()
        status_layout.addRow("Tiempo estimado:", self.tiempo_estimado_label)
        
        # Fecha de entrada
        self.fecha_entrada_label = QLabel()
        status_layout.addRow("Fecha de entrada:", self.fecha_entrada_label)
        
        # Fecha de salida
        self.fecha_salida_label = QLabel()
        status_layout.addRow("Fecha de salida:", self.fecha_salida_label)
        
        layout.addWidget(status_group)
    
    def setup_notes_tab(self):
        """Configura la pestaña de notas y seguimiento"""
        layout = QVBoxLayout(self.notes_tab)
        
        # Título
        title_label = QLabel("Notas y Seguimiento")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Notas adicionales
        notes_group = QGroupBox("Notas Adicionales")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notas_browser = QTextBrowser()
        self.notas_browser.setReadOnly(True)
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

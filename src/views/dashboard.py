#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget para mostrar el panel de control con resumen de datos.
"""

import logging
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QPushButton, QSpacerItem, QSizePolicy,
                            QScrollArea)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QColor

from database.camiones_dao import CamionesDAO
from database.reparaciones_dao import ReparacionesDAO
from models.camion import Camion
from models.reparacion import Reparacion
from models.usuario import Usuario

class DashboardWidget(QWidget):
    """Widget que muestra el panel de control con resúmenes y estadísticas"""
    
    def __init__(self, current_user=None, parent=None):
        """Inicializa el widget de dashboard"""
        super().__init__(parent)
        
        self.current_user = current_user
        self.camiones_dao = CamionesDAO()
        self.reparaciones_dao = ReparacionesDAO()
        
        # Variables para almacenar datos
        self.camiones = []
        self.reparaciones = []
        self.camiones_operativos = 0
        self.camiones_en_reparacion = 0
        self.camiones_fuera_servicio = 0
        
        # Variables para almacenar actividad reciente
        self.actividades_recientes = []
        self.max_actividades = 20  # Máximo número de actividades a mostrar
        
        self.setup_ui()
        self.refresh_data()
        
        # Configurar timer para actualizar datos cada 30 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30000 ms = 30 segundos
        
        # Aplicar estilo base a todo el widget
        self.setStyleSheet("""
            QWidget {
                font-size: 13px;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QLabel {
                font-size: 14px;
            }
        """)
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)  # Aumentar espaciado entre elementos
        
        # Título
        title_label = QLabel("Panel de Control - Sistema de Gestión de Reparaciones")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        # Estilo para el título (sutilmente morado)
        title_label.setStyleSheet("color: #6a0dad; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Espaciador
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Sección de resumen de camiones
        truck_summary_layout = QGridLayout()
        truck_summary_layout.setSpacing(12)  # Espaciado entre widgets
        
        # Total de camiones
        self.total_camiones_widget = self.create_summary_widget(
            "Camiones Total", 
            "0", 
            "#3498db"  # Azul
        )
        truck_summary_layout.addWidget(self.total_camiones_widget, 0, 0)
        
        # Camiones operativos
        self.operativos_widget = self.create_summary_widget(
            "En Operación", 
            "0", 
            "#2ecc71"  # Verde
        )
        truck_summary_layout.addWidget(self.operativos_widget, 0, 1)
        
        # Camiones en reparación
        self.en_reparacion_widget = self.create_summary_widget(
            "En Reparación", 
            "0", 
            "#e74c3c"  # Rojo
        )
        truck_summary_layout.addWidget(self.en_reparacion_widget, 0, 2)
        
        # Camiones fuera de servicio
        self.fuera_servicio_widget = self.create_summary_widget(
            "Fuera de Servicio", 
            "0", 
            "#95a5a6"  # Gris
        )
        truck_summary_layout.addWidget(self.fuera_servicio_widget, 0, 3)
        
        main_layout.addLayout(truck_summary_layout)
        
        
        # Sección de actividad reciente
        activity_layout = QVBoxLayout()
        
        # Título de sección
        activity_title = QLabel("Actividad Reciente")
        activity_title.setFont(QFont("Arial", 16, QFont.Bold))
        activity_title.setStyleSheet("margin-top: 15px; margin-bottom: 8px;")
        activity_layout.addWidget(activity_title)
        
        # Crear área con scroll para actividades recientes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(180)  # Altura mínima aumentada
        scroll_area.setMaximumHeight(250)  # Altura máxima aumentada
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: #f8f8f8;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # Widget contenedor para las actividades
        self.actividad_container_widget = QWidget()
        self.actividad_container_widget.setStyleSheet("background-color: #f8f8f8;")
        
        self.actividad_container = QVBoxLayout(self.actividad_container_widget)
        self.actividad_container.setSpacing(4)  # Espacio entre elementos
        self.actividad_container.setContentsMargins(8, 8, 8, 8)  # Márgenes
        
        # Etiqueta para mostrar cuando no hay actividad
        self.no_actividad_label = QLabel("No hay actividad reciente para mostrar")
        self.no_actividad_label.setAlignment(Qt.AlignCenter)
        self.no_actividad_label.setStyleSheet("color: #888; font-style: italic;")
        self.actividad_container.addWidget(self.no_actividad_label)
        
        # Añadir widget al área de scroll
        scroll_area.setWidget(self.actividad_container_widget)
        activity_layout.addWidget(scroll_area)
        
        main_layout.addLayout(activity_layout)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)  # Espaciado entre botones
        
        self.nuevo_camion_btn = QPushButton("Nuevo Camión")
        self.nuevo_camion_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        self.nuevo_camion_btn.clicked.connect(self.on_nuevo_camion)
        button_layout.addWidget(self.nuevo_camion_btn)
        
        self.nueva_reparacion_btn = QPushButton("Nueva Reparación")
        self.nueva_reparacion_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        self.nueva_reparacion_btn.clicked.connect(self.on_nueva_reparacion)
        button_layout.addWidget(self.nueva_reparacion_btn)
        
        # Botón de actualizar
        self.actualizar_btn = QPushButton("Actualizar Datos")
        self.actualizar_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                font-weight: bold;
                padding: 8px 16px;
                border: 1px solid #d0d0d0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.actualizar_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.actualizar_btn)
        
        main_layout.addLayout(button_layout)
        
        # Fecha y hora actual
        self.fecha_label = QLabel()
        self.fecha_label.setAlignment(Qt.AlignRight)
        self.fecha_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        main_layout.addWidget(self.fecha_label)
        
        # Actualizar fecha y hora
        self.actualizar_fecha_hora()
        
        # Timer para actualizar fecha y hora cada segundo
        self.fecha_timer = QTimer(self)
        self.fecha_timer.timeout.connect(self.actualizar_fecha_hora)
        self.fecha_timer.start(1000)  # 1000 ms = 1 segundo
    
    def create_summary_widget(self, title, value, color):
        """Crea un widget para mostrar un resumen con formato"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            background-color: {color}; 
            border-radius: 8px; 
            color: white;
        """)
        widget.setMinimumHeight(140)  # Altura aumentada
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 15, 10, 15)  # Márgenes aumentados
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14))  # Tamaño de fuente aumentado
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 36, QFont.Bold))  # Tamaño de fuente aumentado
        value_label.setStyleSheet("color: white; margin-top: 5px;")
        layout.addWidget(value_label)
        
        return widget
    
    def actualizar_fecha_hora(self):
        """Actualiza la fecha y hora en la interfaz"""
        fecha_actual = datetime.now().strftime("Fecha actual: %d/%m/%Y %H:%M:%S")
        self.fecha_label.setText(fecha_actual)
    
    def refresh_data(self):
        """Actualiza los datos mostrados en el dashboard"""
        try:
            # Obtener datos actualizados
            self.camiones = self.camiones_dao.obtener_todos()
            self.reparaciones = self.reparaciones_dao.obtener_todas()
            
            # Calcular estadísticas de camiones
            self.camiones_operativos = sum(1 for c in self.camiones if c.estado == Camion.ESTADO_OPERATIVO)
            self.camiones_en_reparacion = sum(1 for c in self.camiones if c.estado == Camion.ESTADO_EN_REPARACION)
            self.camiones_fuera_servicio = sum(1 for c in self.camiones if c.estado == Camion.ESTADO_FUERA_SERVICIO)
            
            # Actualizar widgets de resumen
            self.actualizar_widgets_camiones()
            
            # Calcular estadísticas de reparaciones
            # Ajustar estos conteos según los estados usados en el sistema actualizado
            
            # Mostrar actividad reciente
            self.actualizar_actividad_reciente()
            
        except Exception as e:
            logging.error(f"Error al actualizar el dashboard: {str(e)}")
    
    def actualizar_widgets_camiones(self):
        """Actualiza los widgets con la información de camiones"""
        # Actualizar widgets con los números obtenidos
        total_camiones = len(self.camiones)
        
        # Encuentra todos los QLabels dentro de cada widget y actualiza el segundo (el valor)
        total_label = self.total_camiones_widget.findChildren(QLabel)[1]
        total_label.setText(str(total_camiones))
        
        operativos_label = self.operativos_widget.findChildren(QLabel)[1]
        operativos_label.setText(str(self.camiones_operativos))
        
        reparacion_label = self.en_reparacion_widget.findChildren(QLabel)[1]
        reparacion_label.setText(str(self.camiones_en_reparacion))
        
        fuera_servicio_label = self.fuera_servicio_widget.findChildren(QLabel)[1]
        fuera_servicio_label.setText(str(self.camiones_fuera_servicio))
    
    def actualizar_actividad_reciente(self):
        """Actualiza la sección de actividad reciente"""
        # Limpiar widgets existentes excepto el label de "no hay actividad"
        self.no_actividad_label.setVisible(False)
        for i in reversed(range(self.actividad_container.count())):
            if self.actividad_container.itemAt(i).widget() != self.no_actividad_label:
                widget = self.actividad_container.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        # Combinamos actividades recientes registradas con las actuales
        actividades = self.actividades_recientes.copy()
        
        # Si no hay actividades registradas, crear unas basadas en los datos actuales
        if not actividades:
            # Añadir actividades de reparaciones
            for reparacion in self.reparaciones:
                fecha_act = reparacion.fecha_entrada
                if hasattr(reparacion, 'fecha_actualizacion') and reparacion.fecha_actualizacion:
                    fecha_act = reparacion.fecha_actualizacion
                
                # Crear un objeto de actividad
                actividad = {
                    'fecha': fecha_act,
                    'tipo': 'reparacion',
                    'id': str(reparacion.id),
                    'estado': reparacion.estado,
                    'accion': 'Registro existente',
                    'descripcion': f"Reparación {reparacion.id_falla} - {reparacion.motivo_falla[:30]}..."
                }
                actividades.append(actividad)
            
            # Añadir actividades de camiones
            for camion in self.camiones:
                # Crear un objeto de actividad
                actividad = {
                    'fecha': camion.ultima_actualizacion,
                    'tipo': 'camion',
                    'id': str(camion.id),
                    'estado': camion.estado,
                    'accion': 'Registro existente',
                    'descripcion': f"Camión {camion.matricula} - {camion.modelo}"
                }
                actividades.append(actividad)
        
        # Ordenar actividades por fecha (más reciente primero)
        actividades.sort(key=lambda x: x['fecha'], reverse=True)
        
        # Limitar a las últimas actividades según max_actividades
        actividades = actividades[:self.max_actividades]
        
        if not actividades:
            self.no_actividad_label.setVisible(True)
            return
        
        # Añadir actividades al contenedor
        for actividad in actividades:
            fecha_str = actividad['fecha'].strftime("%d/%m/%Y %H:%M")
            
            # Definir el estilo basado en el tipo y estado
            estilo = "QLabel { padding: 8px; border-radius: 4px; margin-bottom: 4px; font-size: 14px; }"
            if actividad['tipo'] == 'camion':
                if actividad['estado'] == Camion.ESTADO_OPERATIVO:
                    estilo += "background-color: #d5f5e3;" # Verde claro
                elif actividad['estado'] == Camion.ESTADO_EN_REPARACION:
                    estilo += "background-color: #fadbd8;" # Rojo claro
                else:
                    estilo += "background-color: #f2f3f4;" # Gris claro
            else:  # reparacion
                if actividad['estado'] == "Pendiente":
                    estilo += "background-color: #fdebd0;" # Naranja claro
                elif actividad['estado'] in ["En Diagnóstico", "Esperando Repuestos", "En Reparación"]:
                    estilo += "background-color: #ebf5fb;" # Azul claro
                elif actividad['estado'] in ["Reparado", "Entregado"]:
                    estilo += "background-color: #d5f5e3;" # Verde claro
                elif actividad['estado'] == "Cancelado":
                    estilo += "background-color: #fadbd8;" # Rojo claro
                else:
                    estilo += "background-color: #f2f3f4;" # Gris claro
            
            # Crear etiqueta con la actividad y acción
            accion_str = actividad.get('accion', 'Actualización')
            texto_actividad = f"[{fecha_str}] {accion_str}: {actividad['descripcion']} - Estado: {actividad['estado']}"
            actividad_label = QLabel(texto_actividad)
            actividad_label.setStyleSheet(estilo)
            actividad_label.setWordWrap(True)
            
            self.actividad_container.addWidget(actividad_label)
    
    @pyqtSlot()
    def on_nuevo_camion(self):
        """Maneja el evento de crear un nuevo camión"""
        # Esta función será conectada desde la ventana principal
        parent = self.parent()
        if hasattr(parent, 'on_new_truck'):
            parent.on_new_truck()
    
    @pyqtSlot()
    def on_nueva_reparacion(self):
        """Maneja el evento de crear una nueva reparación"""
        # Esta función será conectada desde la ventana principal
        parent = self.parent()
        if hasattr(parent, 'on_new_repair'):
            parent.on_new_repair()
            
    def agregar_actividad(self, tipo, objeto, accion):
        """
        Agrega una nueva actividad al historial
        
        Args:
            tipo (str): 'camion' o 'reparacion'
            objeto: Objeto camion o reparacion
            accion (str): Descripción de la acción realizada
        """
        # Crear una nueva actividad
        if tipo == 'camion':
            actividad = {
                'fecha': datetime.now(),
                'tipo': 'camion',
                'id': str(objeto.id),
                'estado': objeto.estado,
                'accion': accion,
                'descripcion': f"{objeto.matricula} - {objeto.modelo}"
            }
        else:  # reparacion
            actividad = {
                'fecha': datetime.now(),
                'tipo': 'reparacion',
                'id': str(objeto.id),
                'estado': objeto.estado,
                'accion': accion,
                'descripcion': f"{objeto.id_falla} - {objeto.motivo_falla[:30]}..."
            }
        
        # Agregar al inicio de la lista de actividades
        self.actividades_recientes.insert(0, actividad)
        
        # Limitar el número de actividades
        if len(self.actividades_recientes) > self.max_actividades:
            self.actividades_recientes = self.actividades_recientes[:self.max_actividades]
        
        # Actualizar la visualización
        self.actualizar_actividad_reciente()
        
        # También actualizamos los conteos y datos
        self.refresh_data()
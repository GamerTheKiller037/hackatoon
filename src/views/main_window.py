#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ventana principal de la aplicación.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QAction, QToolBar, QStatusBar, QLabel, 
                            QMessageBox, QFileDialog, QDesktopWidget, QPushButton)
from PyQt5.QtCore import Qt, QSize, QDateTime, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

from models.usuario import Usuario
from controllers.reparacion_controller import ReparacionController
from controllers.camion_controller import CamionController
from controllers.mecanico_controller import MecanicoController
from views.camiones.lista_camiones import ListaCamionesWidget
from views.mecanicos.lista_mecanicos import ListaMecanicosWidget
from views.reparaciones.lista_reparaciones import ListaReparaciones
from views.dashboard import DashboardWidget

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    # Señal para notificar cambios en los datos
    data_changed = pyqtSignal()
    
    def __init__(self, current_user=None, parent=None):
        """Inicializa la ventana principal"""
        super().__init__(parent)
        
        self.current_user = current_user
        self.reparacion_controller = ReparacionController()
        self.camion_controller = CamionController()
        self.mecanico_controller = MecanicoController()
        
        self.setupUI()
        self.centerOnScreen()
        
        # Conectar señales para comunicación entre componentes
        self.data_changed.connect(self.refresh_data)
        
        # Mostrar mensaje de bienvenida
        if self.current_user:
            self.statusBar.showMessage(
                f"Bienvenido, {self.current_user.nombre_completo()} ({self.current_user.rol})"
            )
            
        # Aplicar estilo para la barra de título
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QMainWindow::title {
                background-color: #6a1b9a;
                color: white;
            }
            QStatusBar {
                font-size: 12px;
            }
        """)
    
    def setupUI(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Sistema de Gestión de Reparaciones de Camiones")
        self.setMinimumSize(1600, 900)  # Tamaño mínimo aumentado
        
        # Establecer fuente más grande
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        
        # Crear menú
        self.createMenu()
        
        # Crear barra de herramientas
        self.createToolbar()
        
        # Crear barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Sistema listo")
        
        # Widget central con pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 10px 15px;
                margin-right: 2px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #b26af3;
                color: white;
            }
        """)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Pestaña del panel de control (dashboard)
        self.dashboard = DashboardWidget(self.current_user, self)
        self.tabs.addTab(self.dashboard, "Panel de Control")
        
        # Conectar los botones del dashboard con acciones en MainWindow
        if hasattr(self.dashboard, 'nuevo_camion_btn'):
            self.dashboard.nuevo_camion_btn.clicked.disconnect()
            self.dashboard.nuevo_camion_btn.clicked.connect(self.on_new_truck)
            
        if hasattr(self.dashboard, 'nueva_reparacion_btn'):
            self.dashboard.nueva_reparacion_btn.clicked.disconnect()
            self.dashboard.nueva_reparacion_btn.clicked.connect(self.on_new_repair)
        
        # Pestaña de camiones
        self.camiones_widget = ListaCamionesWidget(self.current_user)
        self.tabs.addTab(self.camiones_widget, "Camiones")
        
        # Conectar señales del widget de camiones
        if hasattr(self.camiones_widget, 'camion_seleccionado'):
            self.camiones_widget.camion_seleccionado.connect(self.on_camion_seleccionado)
        
        # Pestaña de mecánicos
        self.mecanicos_widget = ListaMecanicosWidget(self.current_user)
        self.tabs.addTab(self.mecanicos_widget, "Mecánicos")
        
        # Conectar señales del widget de mecánicos
        if hasattr(self.mecanicos_widget, 'mecanico_seleccionado'):
            self.mecanicos_widget.mecanico_seleccionado.connect(self.on_mecanico_seleccionado)
        
        # Pestaña de reparaciones
        self.reparaciones_widget = ListaReparaciones(self.reparacion_controller)
        self.tabs.addTab(self.reparaciones_widget, "Reparaciones")
        
        # Si el usuario es administrador, añadir pestaña de administración
        if self.current_user and self.current_user.rol == Usuario.ROL_ADMIN:
            self.create_admin_tab()
        
        # Configurar el widget central
        self.setCentralWidget(self.tabs)
    



    
    def create_admin_tab(self):
        """Crea la pestaña de administración"""
        admin_widget = QWidget()
        layout = QVBoxLayout(admin_widget)
        
        # Aquí se añadirán widgets para la administración del sistema
        layout.addWidget(QLabel("Administración del Sistema"))
        
        self.tabs.addTab(admin_widget, "Administración")
    
    def createMenu(self):
        """Crea la barra de menú de la aplicación"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        new_truck_action = QAction("&Nuevo Camión", self)
        new_truck_action.setShortcut("Ctrl+T")
        new_truck_action.setStatusTip("Registrar un nuevo camión")
        new_truck_action.triggered.connect(self.on_new_truck)
        file_menu.addAction(new_truck_action)
        
        # Acción para nuevo mecánico (NUEVO)
        new_mechanic_action = QAction("Nuevo &Mecánico", self)
        new_mechanic_action.setShortcut("Ctrl+M")
        new_mechanic_action.setStatusTip("Registrar un nuevo mecánico")
        new_mechanic_action.triggered.connect(self.on_new_mechanic)
        file_menu.addAction(new_mechanic_action)
        
        new_repair_action = QAction("Nueva &Reparación", self)
        new_repair_action.setShortcut("Ctrl+N")
        new_repair_action.setStatusTip("Registrar una nueva reparación")
        new_repair_action.triggered.connect(self.on_new_repair)
        file_menu.addAction(new_repair_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exportar Datos", self)
        export_action.setStatusTip("Exportar datos a un archivo CSV")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        print_action = QAction("&Imprimir Lista", self)
        print_action.setShortcut("Ctrl+P")
        print_action.setStatusTip("Imprimir lista de reparaciones o camiones")
        print_action.triggered.connect(self.print_list)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.setStatusTip("Salir de la aplicación")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        dashboard_action = QAction("&Panel de Control", self)
        dashboard_action.setStatusTip("Ver el panel de control")
        dashboard_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(dashboard_action)
        
        trucks_action = QAction("&Camiones", self)
        trucks_action.setStatusTip("Ver lista de camiones")
        trucks_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(trucks_action)
        
        # Acción para ver mecánicos (NUEVO)
        mechanics_action = QAction("&Mecánicos", self)
        mechanics_action.setStatusTip("Ver lista de mecánicos")
        mechanics_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(mechanics_action)
        
        repairs_action = QAction("&Reparaciones", self)
        repairs_action.setStatusTip("Ver lista de reparaciones")
        repairs_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))  # Cambiar índice
        view_menu.addAction(repairs_action)
        
        view_menu.addSeparator()
        
        refresh_action = QAction("&Actualizar", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Actualizar datos")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("A&yuda")
        
        help_action = QAction("&Ayuda", self)
        help_action.setStatusTip("Mostrar ayuda")
        help_action.triggered.connect(self.on_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("&Acerca de", self)
        about_action.setStatusTip("Mostrar información sobre la aplicación")
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
    
    def createToolbar(self):
        """Crea la barra de herramientas de la aplicación"""
        toolbar = QToolBar("Barra Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Botón nuevo camión
        new_truck_action = QAction("Nuevo Camión", self)
        new_truck_action.triggered.connect(self.on_new_truck)
        toolbar.addAction(new_truck_action)
        
        # Botón nuevo mecánico (NUEVO)
        new_mechanic_action = QAction("Nuevo Mecánico", self)
        new_mechanic_action.triggered.connect(self.on_new_mechanic)
        toolbar.addAction(new_mechanic_action)
        
        # Botón nueva reparación
        new_repair_action = QAction("Nueva Reparación", self)
        new_repair_action.triggered.connect(self.on_new_repair)
        toolbar.addAction(new_repair_action)
        
        toolbar.addSeparator()
        
        # Botón actualizar
        refresh_action = QAction("Actualizar", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
    
    @pyqtSlot()
    def on_new_truck(self):
        """Maneja la acción de crear un nuevo camión"""
        from views.camiones.form_camion import FormCamionDialog
        
        dialog = FormCamionDialog(parent=self)
        if dialog.exec_():
            # Notificar cambio en los datos
            self.data_changed.emit()
            
            # Registrar actividad en el dashboard
            if hasattr(self, 'dashboard') and hasattr(self.dashboard, 'agregar_actividad'):
                # Obtener el camión recién creado
                try:
                    nuevos_camiones = self.camiones_widget.camiones_dao.obtener_todos()
                    if nuevos_camiones:
                        nuevo_camion = nuevos_camiones[-1]  # Asumiendo que el último es el recién creado
                        self.dashboard.agregar_actividad('camion', nuevo_camion, "Nuevo camión creado")
                except Exception as e:
                    logging.error(f"Error al registrar actividad de nuevo camión: {str(e)}")
            
            self.statusBar.showMessage("Nuevo camión registrado correctamente", 3000)

    @pyqtSlot()
    def on_new_mechanic(self):
        """Maneja la acción de crear un nuevo mecánico"""
        from views.mecanicos.form_mecanico import FormMecanicoDialog
        
        dialog = FormMecanicoDialog(parent=self)
        if dialog.exec_():
            # Notificar cambio en los datos
            self.data_changed.emit()
            self.statusBar.showMessage("Nuevo mecánico registrado correctamente", 3000)
    
    @pyqtSlot()
    def on_new_repair(self):
        """Maneja la acción de crear una nueva reparación"""
        from views.reparaciones.form_reparacion import FormReparaciones        
        dialog = FormReparaciones(self.reparacion_controller, parent=self)
        if dialog.exec_():
            # Notificar cambio en los datos
            self.data_changed.emit()
            
            # Registrar actividad en el dashboard
            if hasattr(self, 'dashboard') and hasattr(self.dashboard, 'agregar_actividad'):
                try:
                    # Obtener la reparación recién creada
                    nuevas_reparaciones = self.reparacion_controller.obtener_todas_reparaciones()
                    if nuevas_reparaciones:
                        nueva_reparacion = nuevas_reparaciones[-1]  # Asumiendo que la última es la recién creada
                        
                        # Crear un objeto Reparacion básico con los datos mínimos necesarios
                        from models.reparacion import Reparacion
                        from bson import ObjectId
                        
                        # Crear un objeto Reparacion básico para el registro de actividad
                        reparacion_obj = Reparacion(
                            camion_id=ObjectId(nueva_reparacion.get('camion_id', '')),
                            id_falla=str(nueva_reparacion.get('id', 'N/A')),
                            motivo_falla=nueva_reparacion.get('problema', 'Sin especificar'),
                            descripcion=nueva_reparacion.get('diagnostico', 'Sin descripción')
                        )
                        # Establecer estado y otros atributos necesarios
                        reparacion_obj.estado = nueva_reparacion.get('estado', 'Pendiente')
                        
                        self.dashboard.agregar_actividad('reparacion', reparacion_obj, "Nueva reparación creada")
                except Exception as e:
                    logging.error(f"Error al registrar actividad de nueva reparación: {str(e)}")
            
            self.statusBar.showMessage("Nueva reparación registrada correctamente", 3000)

    @pyqtSlot()
    def refresh_data(self):
        """Actualiza los datos en todas las pestañas"""
        if hasattr(self, 'dashboard') and hasattr(self.dashboard, 'refresh_data'):
            self.dashboard.refresh_data()
        
        camiones_widget_names = ['camiones_widget', 'camionesWidget', 'lista_camiones']
        for widget_name in camiones_widget_names:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                if hasattr(widget, 'refresh_data'):
                    widget.refresh_data()
                break
        
        # Actualizar mecánicos
        mecanicos_widget_names = ['mecanicos_widget', 'mecanicosWidget', 'lista_mecanicos']
        for widget_name in mecanicos_widget_names:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                if hasattr(widget, 'refresh_data'):
                    widget.refresh_data()
                break
        
        reparaciones_widget_names = ['reparaciones_widget', 'reparacionesWidget', 'lista_reparaciones']
        for widget_name in reparaciones_widget_names:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                if hasattr(widget, 'cargarReparaciones'):
                    widget.cargarReparaciones()
                break
    
    @pyqtSlot(int)
    def on_tab_changed(self, index):
        """Maneja el evento de cambio de pestaña"""
        # Actualizar datos cuando se cambia de pestaña
        self.refresh_data()
    
    def on_camion_actualizado(self, camion):
        """Maneja el evento de actualización de un camión"""
        # Notificar cambio en los datos
        self.data_changed.emit()
        
        # Registrar actividad en el dashboard
        if hasattr(self, 'dashboard') and hasattr(self.dashboard, 'agregar_actividad'):
            self.dashboard.agregar_actividad('camion', camion, "Camión actualizado")
        
        self.statusBar.showMessage(f"Camión {camion.matricula} actualizado correctamente", 3000)

    def on_reparacion_actualizada(self, reparacion):
        """Maneja el evento de actualización de una reparación"""
        # Notificar cambio en los datos
        self.data_changed.emit()
        
        # Registrar actividad en el dashboard
        if hasattr(self, 'dashboard') and hasattr(self.dashboard, 'agregar_actividad'):
            self.dashboard.agregar_actividad('reparacion', reparacion, "Reparación actualizada")
        
        self.statusBar.showMessage(f"Reparación actualizada correctamente", 3000)
        
    @pyqtSlot(object)
    def on_camion_seleccionado(self, camion):
        """Maneja el evento de selección de un camión"""
        if camion:
            self.statusBar.showMessage(f"Camión seleccionado: {camion.matricula} ({camion.modelo})", 3000)
    
    @pyqtSlot(object)
    def on_mecanico_seleccionado(self, mecanico):
        """Maneja el evento de selección de un mecánico"""
        if mecanico:
            self.statusBar.showMessage(f"Mecánico seleccionado: {mecanico.nombre} {mecanico.apellidos}", 3000)
    
    def export_data(self):
        """Exporta los datos a un archivo CSV"""
        current_index = self.tabs.currentIndex()
        
        if current_index == 1:  # Pestaña de camiones
            self.export_trucks_data()
        elif current_index == 2:  # Pestaña de mecánicos
            self.export_mechanics_data()
        elif current_index == 3:  # Pestaña de reparaciones
            self.export_repairs_data()
        else:
            QMessageBox.information(
                self,
                "Exportar Datos",
                "Por favor, seleccione la pestaña de Camiones, Mecánicos o Reparaciones para exportar datos."
            )
    
    def export_trucks_data(self):
        """Exporta los datos de camiones a un archivo CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Datos de Camiones", 
            "", 
            "Archivos CSV (*.csv);;Todos los archivos (*)"
        )
        
        if filename:
            try:
                # Implementar la exportación de datos de camiones
                self.camion_controller.exportar_a_csv(filename)
                QMessageBox.information(
                    self,
                    "Exportar Datos",
                    f"Los datos se han exportado correctamente a: {filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al exportar datos: {str(e)}"
                )
    
    def export_mechanics_data(self):
        """Exporta los datos de mecánicos a un archivo CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Datos de Mecánicos", 
            "", 
            "Archivos CSV (*.csv);;Todos los archivos (*)"
        )
        
        if filename:
            try:
                # Implementar la exportación de datos de mecánicos
                self.mecanico_controller.exportar_a_csv(filename)
                QMessageBox.information(
                    self,
                    "Exportar Datos",
                    f"Los datos se han exportado correctamente a: {filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al exportar datos: {str(e)}"
                )
    
    def print_list(self):
        """Imprime la lista actual"""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.handle_print_request)
        preview.exec_()
    
    def handle_print_request(self, printer):
        """Maneja la solicitud de impresión"""
        current_index = self.tabs.currentIndex()
        
        if current_index == 1:  # Pestaña de camiones
            # Si el widget de camiones implementa una función para imprimir Panel de Control
            if hasattr(self.camiones_widget, 'print_data'):
                self.camiones_widget.print_data(printer)
            else:
                self.statusBar.showMessage("La funcionalidad de impresión para camiones no está implementada", 3000)
        elif current_index == 2:  # Pestaña de mecánicos
            # Si el widget de mecánicos implementa una función para imprimir
            if hasattr(self.mecanicos_widget, 'print_data'):
                self.mecanicos_widget.print_data(printer)
            else:
                self.statusBar.showMessage("La funcionalidad de impresión para mecánicos no está implementada", 3000)
        elif current_index == 3:  # Pestaña de reparaciones
            # Si el widget de reparaciones implementa una función para imprimir
            if hasattr(self.reparaciones_widget, 'print_data'):
                self.reparaciones_widget.print_data(printer)
            else:
                self.statusBar.showMessage("La funcionalidad de impresión para reparaciones no está implementada", 3000)
        else:
            self.statusBar.showMessage("No hay datos para imprimir en esta pestaña", 3000)
    
    def on_help(self):
        """Maneja la acción de mostrar ayuda"""
        QMessageBox.information(
            self,
            "Ayuda",
            "Sistema de Gestión de Reparaciones de Camiones\n\n"
            "Esta aplicación permite gestionar el registro y seguimiento "
            "de reparaciones de una flota de camiones.\n\n"
            "- Panel de Control: Muestra resumen de datos y estadísticas\n"
            "- Camiones: Gestiona la flota de vehículos\n"
            "- Mecánicos: Gestiona el personal de mantenimiento\n"
            "- Reparaciones: Registro y seguimiento de reparaciones\n"
            "- F5: Actualiza los datos en todas las vistas"
        )
    
    def on_about(self):
        """Maneja la acción de mostrar acerca de"""
        QMessageBox.about(
            self,
            "Acerca de",
            "Sistema de Gestión de Reparaciones de Camiones\n"
            "Versión 1.0.1\n\n"
            "Desarrollado como solución de software para gestionar "
            "el mantenimiento y reparaciones de una flota de camiones."
        )
    
    def centerOnScreen(self):
        """Centra la ventana en la pantalla"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2, 
            (screen.height() - size.height()) // 2
        )
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro que desea salir de la aplicación?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def export_repairs_data(self):
        """Exporta los datos de reparaciones a un archivo CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Datos de Reparaciones", 
            "", 
            "Archivos CSV (*.csv);;Todos los archivos (*)"
        )
        
        if filename:
            try:
                # Implementar la exportación de datos de reparaciones
                self.reparacion_controller.exportar_a_csv(filename)
                QMessageBox.information(
                    self,
                    "Exportar Datos",
                    f"Los datos se han exportado correctamente a: {filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al exportar datos: {str(e)}"
                )
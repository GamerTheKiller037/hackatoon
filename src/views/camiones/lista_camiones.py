#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget para mostrar la lista de camiones.
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                            QComboBox, QHeaderView, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush

from database.camiones_dao import CamionesDAO
from models.camion import Camion
from models.usuario import Usuario
from views.camiones.detalle_camion import DetalleCamionDialog
from views.camiones.form_camion import FormCamionDialog

class ListaCamionesWidget(QWidget):
    """Widget para mostrar y gestionar la lista de camiones"""
    
    # Señales
    camion_seleccionado = pyqtSignal(Camion)
    
    def __init__(self, current_user=None, parent=None):
        """Inicializa el widget de lista de camiones"""
        super().__init__(parent)
        
        self.current_user = current_user
        self.camiones_dao = CamionesDAO()
        self.camiones = []
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Sección de filtros
        filter_layout = QHBoxLayout()
        
        # Filtro por matrícula
        filter_layout.addWidget(QLabel("Matrícula:"))
        self.matricula_filter = QLineEdit()
        self.matricula_filter.setPlaceholderText("Filtrar por matrícula")
        self.matricula_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.matricula_filter)
        
        # Filtro por estado
        filter_layout.addWidget(QLabel("Estado:"))
        self.estado_filter = QComboBox()
        self.estado_filter.addItem("Todos", "")
        for estado in Camion.ESTADOS_VALIDOS:
            self.estado_filter.addItem(estado, estado)
        self.estado_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.estado_filter)
        
        # Botón de limpiar filtros
        self.clear_filter_button = QPushButton("Limpiar Filtros")
        self.clear_filter_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(self.clear_filter_button)
        
        main_layout.addLayout(filter_layout)
        
        # Tabla de camiones
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Matrícula", "Modelo", "Año", "Estado", "Última Actualización"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.on_table_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.table)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Agregar Camión")
        self.add_button.clicked.connect(self.on_add_button_clicked)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Editar Camión")
        self.edit_button.clicked.connect(self.on_edit_button_clicked)
        button_layout.addWidget(self.edit_button)
        
        self.details_button = QPushButton("Ver Detalles")
        self.details_button.clicked.connect(self.on_details_button_clicked)
        button_layout.addWidget(self.details_button)
        
        if self.current_user and self.current_user.rol == Usuario.ROL_ADMIN:
            self.delete_button = QPushButton("Eliminar Camión")
            self.delete_button.clicked.connect(self.on_delete_button_clicked)
            button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
        
        # Deshabilitar botones hasta que se seleccione un camión
        self.edit_button.setEnabled(False)
        self.details_button.setEnabled(False)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(False)
        
        # Conectar señal de selección
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Etiqueta de información
        self.info_label = QLabel("Haga doble clic en un camión para ver sus detalles")
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)
    
    def refresh_data(self):
        """Actualiza los datos de la tabla"""
        self.camiones = self.camiones_dao.obtener_todos()
        self.populate_table(self.camiones)
    
    def populate_table(self, camiones):
        """Rellena la tabla con los datos de los camiones"""
        self.table.setRowCount(0)
        
        for camion in camiones:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Matrícula
            item_matricula = QTableWidgetItem(camion.matricula)
            item_matricula.setData(Qt.UserRole, camion.id)
            self.table.setItem(row_position, 0, item_matricula)
            
            # Modelo
            self.table.setItem(row_position, 1, QTableWidgetItem(camion.modelo))
            
            # Año
            self.table.setItem(row_position, 2, QTableWidgetItem(str(camion.año)))
            
            # Estado
            item_estado = QTableWidgetItem(camion.estado)
            
            # Colorear según el estado
            if camion.estado == Camion.ESTADO_OPERATIVO:
                item_estado.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
            elif camion.estado == Camion.ESTADO_EN_REPARACION:
                item_estado.setBackground(QBrush(QColor(255, 200, 200)))  # Rojo claro
            elif camion.estado == Camion.ESTADO_FUERA_SERVICIO:
                item_estado.setBackground(QBrush(QColor(200, 200, 200)))  # Gris claro
            
            self.table.setItem(row_position, 3, item_estado)
            
            # Última actualización
            fecha_str = camion.ultima_actualizacion.strftime("%d/%m/%Y %H:%M")
            self.table.setItem(row_position, 4, QTableWidgetItem(fecha_str))
        
        self.info_label.setText(f"Total: {len(camiones)} camiones")
    
    def apply_filters(self):
        """Aplica los filtros a la tabla"""
        matricula_filter = self.matricula_filter.text().strip().lower()
        estado_filter = self.estado_filter.currentData()
        
        filtered_camiones = []
        
        for camion in self.camiones:
            # Filtrar por matrícula
            if matricula_filter and matricula_filter not in camion.matricula.lower():
                continue
            
            # Filtrar por estado
            if estado_filter and camion.estado != estado_filter:
                continue
            
            filtered_camiones.append(camion)
        
        self.populate_table(filtered_camiones)
    
    def clear_filters(self):
        """Limpia los filtros"""
        self.matricula_filter.clear()
        self.estado_filter.setCurrentIndex(0)
        self.populate_table(self.camiones)
    
    def get_selected_camion(self):
        """Obtiene el camión seleccionado"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        index = selected_rows[0].row()
        camion_id = self.table.item(index, 0).data(Qt.UserRole)
        
        return self.camiones_dao.obtener_por_id(camion_id)
    
    def on_selection_changed(self):
        """Maneja el evento de cambio de selección"""
        camion = self.get_selected_camion()
        
        # Habilitar o deshabilitar botones según si hay selección
        enabled = camion is not None
        self.edit_button.setEnabled(enabled)
        self.details_button.setEnabled(enabled)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(enabled)
        
        if camion:
            self.camion_seleccionado.emit(camion)
    
    def on_table_double_clicked(self, index):
        """Maneja el evento de doble clic en la tabla"""
        camion = self.get_selected_camion()
        if camion:
            self.show_camion_details(camion)
    
    def on_add_button_clicked(self):
        """Maneja el evento de clic en el botón de agregar"""
        dialog = FormCamionDialog(parent=self)
        if dialog.exec_():
            # Refrescar datos después de agregar
            self.refresh_data()
    
    def on_edit_button_clicked(self):
        """Maneja el evento de clic en el botón de editar"""
        camion = self.get_selected_camion()
        if camion:
            dialog = FormCamionDialog(camion=camion, parent=self)
            if dialog.exec_():
                # Refrescar datos después de editar
                self.refresh_data()
    
    def on_details_button_clicked(self):
        """Maneja el evento de clic en el botón de detalles"""
        camion = self.get_selected_camion()
        if camion:
            self.show_camion_details(camion)
    
    def on_delete_button_clicked(self):
        """Maneja el evento de clic en el botón de eliminar"""
        camion = self.get_selected_camion()
        if not camion:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el camión {camion.matricula}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Eliminar el camión
            if self.camiones_dao.eliminar(camion.id):
                QMessageBox.information(
                    self,
                    "Eliminación exitosa",
                    f"El camión {camion.matricula} ha sido eliminado correctamente."
                )
                self.refresh_data()
            else:
                QMessageBox.warning(
                    self,
                    "Error al eliminar",
                    f"No se pudo eliminar el camión {camion.matricula}."
                )
    
    def show_camion_details(self, camion):
        """Muestra el diálogo de detalles de un camión"""
        dialog = DetalleCamionDialog(camion, parent=self)
        dialog.exec_()
    
    def show_context_menu(self, position):
        """Muestra el menú contextual"""
        camion = self.get_selected_camion()
        if not camion:
            return
        
        context_menu = QMenu(self)
        
        # Acciones del menú
        ver_action = context_menu.addAction("Ver Detalles")
        editar_action = context_menu.addAction("Editar")
        
        if self.current_user and self.current_user.rol == Usuario.ROL_ADMIN:
            context_menu.addSeparator()
            eliminar_action = context_menu.addAction("Eliminar")
        
        # Mostrar el menú y obtener la acción seleccionada
        action = context_menu.exec_(self.table.mapToGlobal(position))
        
        if action == ver_action:
            self.show_camion_details(camion)
        elif action == editar_action:
            dialog = FormCamionDialog(camion=camion, parent=self)
            if dialog.exec_():
                self.refresh_data()
        elif self.current_user and self.current_user.rol == Usuario.ROL_ADMIN and action == eliminar_action:
            self.on_delete_button_clicked()

if __name__ == "__main__":
    # Prueba del widget
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Crear un usuario de prueba
    admin_user = Usuario("Admin", "Test", "admin", "admin", rol=Usuario.ROL_ADMIN)
    
    widget = ListaCamionesWidget(admin_user)
    widget.show()
    
    sys.exit(app.exec_())
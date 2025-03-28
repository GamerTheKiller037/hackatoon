#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget para mostrar la lista de tareas de mantenimiento preventivo.
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                            QComboBox, QHeaderView, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush, QFont

from database.preventivas_dao import PreventivasDAO
from models.preventiva import Preventiva
from models.usuario import Usuario
from views.preventivas.detalle_preventiva import DetallePreventiva
from views.preventivas.form_preventiva import FormPreventivaDialog

class ListaPreventivasWidget(QWidget):
    """Widget para mostrar y gestionar la lista de tareas preventivas"""
    
    # Señales
    preventiva_seleccionada = pyqtSignal(Preventiva)
    
    def __init__(self, current_user=None, parent=None):
        """Inicializa el widget de lista de preventivas"""
        super().__init__(parent)
        
        self.current_user = current_user
        self.preventivas_dao = PreventivasDAO()
        self.preventivas = []
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Gestión de Mantenimientos Preventivos")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6a1b9a;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Sección de filtros
        filter_layout = QHBoxLayout()
        
        # Filtro por matrícula
        filter_layout.addWidget(QLabel("Matrícula:"))
        self.matricula_filter = QLineEdit()
        self.matricula_filter.setPlaceholderText("Filtrar por matrícula:")
        self.matricula_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.matricula_filter)
        
        # Filtro por estado
        filter_layout.addWidget(QLabel("Estado:"))
        self.estado_filter = QComboBox()
        self.estado_filter.addItem("Todos", "")
        for estado in Preventiva.ESTADOS_VALIDOS:
            self.estado_filter.addItem(estado, estado)
        self.estado_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.estado_filter)
        
        # Filtro por nivel de urgencia
        filter_layout.addWidget(QLabel("Urgencia:"))
        self.urgencia_filter = QComboBox()
        self.urgencia_filter.addItem("Todos", "")
        for urgencia in Preventiva.NIVELES_URGENCIA:
            self.urgencia_filter.addItem(urgencia, urgencia)
        self.urgencia_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.urgencia_filter)
        
        # Botón de limpiar filtros
        self.clear_filter_button = QPushButton("Limpiar Filtros")
        self.clear_filter_button.setStyleSheet("background-color: #e1bee7; font-weight: bold; border-radius: 4px;")
        self.clear_filter_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(self.clear_filter_button)
        
        main_layout.addLayout(filter_layout)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Agregar Preventiva")
        self.add_button.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; border-radius: 4px;")
        self.add_button.clicked.connect(self.on_add_button_clicked)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Editar Preventiva")
        self.edit_button.clicked.connect(self.on_edit_button_clicked)
        button_layout.addWidget(self.edit_button)
        
        self.details_button = QPushButton("Ver Detalles")
        self.details_button.clicked.connect(self.on_details_button_clicked)
        button_layout.addWidget(self.details_button)
        
        if self.current_user and self.current_user.rol == Usuario.ROL_ADMIN:
            self.delete_button = QPushButton("Eliminar Preventiva")
            self.delete_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; border-radius: 4px;")
            self.delete_button.clicked.connect(self.on_delete_button_clicked)
            button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
        
        # Tabla de preventivas
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Matrícula", "Modelo", "Tipo", "Estado", "Nivel Urgencia", "Última Actualización"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.on_table_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Establecer fuente más grande para la tabla
        font = QFont()
        font.setPointSize(11)
        self.table.setFont(font)
        
        main_layout.addWidget(self.table)
        
        # Deshabilitar botones hasta que se seleccione una preventiva
        self.edit_button.setEnabled(False)
        self.details_button.setEnabled(False)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(False)
        
        # Conectar señal de selección
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Etiqueta de información
        self.info_label = QLabel("Haga doble clic en una preventiva para ver sus detalles")
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # Establecer margen y espaciado
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
    
    def refresh_data(self):
        """Actualiza los datos de la tabla"""
        self.preventivas = self.preventivas_dao.obtener_todas()
        self.populate_table(self.preventivas)
    
    def populate_table(self, preventivas):
        """Rellena la tabla con los datos de las preventivas"""
        self.table.setRowCount(0)
        
        for preventiva in preventivas:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Matrícula
            item_matricula = QTableWidgetItem(preventiva.matricula)
            item_matricula.setData(Qt.UserRole, preventiva.id)
            self.table.setItem(row_position, 0, item_matricula)
            
            # Modelo
            self.table.setItem(row_position, 1, QTableWidgetItem(preventiva.modelo))
            
            # Tipo
            self.table.setItem(row_position, 2, QTableWidgetItem(preventiva.tipo))
            
            # Estado
            item_estado = QTableWidgetItem(preventiva.estado)
            
            # Colorear según el estado
            if preventiva.estado == Preventiva.ESTADO_PROGRAMADO:
                item_estado.setBackground(QBrush(QColor(255, 255, 200)))  # Amarillo claro
            elif preventiva.estado == Preventiva.ESTADO_EN_REPARACION:
                item_estado.setBackground(QBrush(QColor(255, 200, 200)))  # Rojo claro
            elif preventiva.estado == Preventiva.ESTADO_COMPLETADO:
                item_estado.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
            elif preventiva.estado == Preventiva.ESTADO_CANCELADO:
                item_estado.setBackground(QBrush(QColor(200, 200, 200)))  # Gris claro
            
            self.table.setItem(row_position, 3, item_estado)
            
            # Nivel de urgencia
            item_urgencia = QTableWidgetItem(preventiva.nivel_urgencia)
            
            # Colorear según el nivel de urgencia
            if preventiva.nivel_urgencia == Preventiva.URGENCIA_ALTA:
                item_urgencia.setBackground(QBrush(QColor(255, 180, 180)))  # Rojo más intenso
            elif preventiva.nivel_urgencia == Preventiva.URGENCIA_MEDIA:
                item_urgencia.setBackground(QBrush(QColor(255, 220, 180)))  # Naranja claro
            elif preventiva.nivel_urgencia == Preventiva.URGENCIA_BAJA:
                item_urgencia.setBackground(QBrush(QColor(180, 255, 180)))  # Verde muy claro
            
            self.table.setItem(row_position, 4, item_urgencia)
            
            # Última actualización
            fecha_str = "Sin actualizaciones"
            if hasattr(preventiva, 'ultima_actualizacion_reparacion') and preventiva.ultima_actualizacion_reparacion:
                fecha_str = preventiva.ultima_actualizacion_reparacion.strftime("%d/%m/%Y %H:%M")
            self.table.setItem(row_position, 5, QTableWidgetItem(fecha_str))
        
        self.info_label.setText(f"Total: {len(preventivas)} preventivas")
    
    def apply_filters(self):
        """Aplica los filtros a la tabla"""
        matricula_filter = self.matricula_filter.text().strip().lower()
        estado_filter = self.estado_filter.currentData()
        urgencia_filter = self.urgencia_filter.currentData()
        
        filtered_preventivas = []
        
        for preventiva in self.preventivas:
            # Filtrar por matrícula
            if matricula_filter and matricula_filter not in preventiva.matricula.lower():
                continue
            
            # Filtrar por estado
            if estado_filter and preventiva.estado != estado_filter:
                continue
            
            # Filtrar por nivel de urgencia
            if urgencia_filter and preventiva.nivel_urgencia != urgencia_filter:
                continue
            
            filtered_preventivas.append(preventiva)
        
        self.populate_table(filtered_preventivas)
    
    def clear_filters(self):
        """Limpia los filtros"""
        self.matricula_filter.clear()
        self.estado_filter.setCurrentIndex(0)
        self.urgencia_filter.setCurrentIndex(0)
        self.populate_table(self.preventivas)
    
    def get_selected_preventiva(self):
        """Obtiene la preventiva seleccionada"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        index = selected_rows[0].row()
        preventiva_id = self.table.item(index, 0).data(Qt.UserRole)
        
        return self.preventivas_dao.obtener_por_id(preventiva_id)
    
    def on_selection_changed(self):
        """Maneja el evento de cambio de selección"""
        preventiva = self.get_selected_preventiva()
        
        # Habilitar o deshabilitar botones según si hay selección
        enabled = preventiva is not None
        self.edit_button.setEnabled(enabled)
        self.details_button.setEnabled(enabled)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(enabled)
        
        if preventiva:
            self.preventiva_seleccionada.emit(preventiva)
    
    def on_table_double_clicked(self, index):
        """Maneja el evento de doble clic en la tabla"""
        preventiva = self.get_selected_preventiva()
        if preventiva:
            self.show_preventiva_details(preventiva)
    
    def on_add_button_clicked(self):
        """Maneja el evento de clic en el botón de agregar"""
        dialog = FormPreventivaDialog(parent=self)
        if dialog.exec_():
            # Refrescar datos después de agregar
            self.refresh_data()
    
    def on_edit_button_clicked(self):
        """Maneja el evento de clic en el botón de editar"""
        preventiva = self.get_selected_preventiva()
        if preventiva:
            dialog = FormPreventivaDialog(preventiva=preventiva, parent=self)
            if dialog.exec_():
                # Refrescar datos después de editar
                self.refresh_data()
    
    def on_details_button_clicked(self):
        """Maneja el evento de clic en el botón de detalles"""
        preventiva = self.get_selected_preventiva()
        if preventiva:
            self.show_preventiva_details(preventiva)
    
    def on_delete_button_clicked(self):
        """Maneja el evento de clic en el botón de eliminar"""
        preventiva = self.get_selected_preventiva()
        if not preventiva:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la preventiva de {preventiva.matricula}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Eliminar la preventiva
            if self.preventivas_dao.eliminar(preventiva.id):
                QMessageBox.information(
                    self,
                    "Eliminación exitosa",
                    f"La preventiva de {preventiva.matricula} ha sido eliminada correctamente."
                )
                self.refresh_data()
            else:
                QMessageBox.warning(
                    self,
                    "Error al eliminar",
                    f"No se pudo eliminar la preventiva de {preventiva.matricula}."
                )
    
    def show_preventiva_details(self, preventiva):
        """Muestra el diálogo de detalles de una preventiva"""
        dialog = DetallePreventiva(preventiva, parent=self)
        dialog.exec_()
    
    def show_context_menu(self, position):
        """Muestra el menú contextual"""
        preventiva = self.get_selected_preventiva()
        if not preventiva:
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
            self.show_preventiva_details(preventiva)
        elif action == editar_action:
            dialog = FormPreventivaDialog(preventiva=preventiva, parent=self)
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
    
    widget = ListaPreventivasWidget(admin_user)
    widget.show()
    
    sys.exit(app.exec_())
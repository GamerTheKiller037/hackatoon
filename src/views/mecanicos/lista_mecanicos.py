import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                            QComboBox, QHeaderView, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush, QFont

from database.mecanicos_dao import MecanicosDAO
from models.mecanico import Mecanico
from models.usuario import Usuario
from views.mecanicos.detalle_mecanico import DetalleMecanicoDialog
from views.mecanicos.form_mecanico import FormMecanicoDialog

class ListaMecanicosWidget(QWidget):
    """Widget para mostrar y gestionar la lista de mecánicos"""
    
    # Señales
    mecanico_seleccionado = pyqtSignal(Mecanico)
    
    def __init__(self, current_user=None, parent=None):
        """Inicializa el widget de lista de mecánicos"""
        super().__init__(parent)
        
        self.current_user = current_user
        self.mecanicos_dao = MecanicosDAO()
        self.mecanicos = []
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Gestión de Mecánicos")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6a1b9a;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Sección de filtros
        filter_layout = QHBoxLayout()
        
        # Filtro por nombre
        filter_layout.addWidget(QLabel("Nombre:"))
        self.nombre_filter = QLineEdit()
        self.nombre_filter.setPlaceholderText("Filtrar por nombre")
        self.nombre_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.nombre_filter)
        
        # Filtro por actividad
        filter_layout.addWidget(QLabel("Actividad:"))
        self.actividad_filter = QComboBox()
        self.actividad_filter.addItem("Todas", "")
        for actividad in Mecanico.ACTIVIDADES_VALIDAS:
            self.actividad_filter.addItem(actividad, actividad)
        self.actividad_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.actividad_filter)
        
        # Botón de limpiar filtros
        self.clear_filter_button = QPushButton("Limpiar Filtros")
        self.clear_filter_button.setStyleSheet("background-color: #e1bee7; font-weight: bold; border-radius: 4px;")
        self.clear_filter_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(self.clear_filter_button)
        
        main_layout.addLayout(filter_layout)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Agregar Mecánico")
        self.add_button.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; border-radius: 4px;")
        self.add_button.clicked.connect(self.on_add_button_clicked)
        action_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Editar Mecánico")
        self.edit_button.clicked.connect(self.on_edit_button_clicked)
        action_layout.addWidget(self.edit_button)
        
        self.details_button = QPushButton("Ver Detalles")
        self.details_button.clicked.connect(self.on_details_button_clicked)
        action_layout.addWidget(self.details_button)
        
        if self.current_user and self.current_user.rol == Usuario.ROL_ADMIN:
            self.delete_button = QPushButton("Eliminar Mecánico")
            self.delete_button.setStyleSheet("background-color: #f44336; color: white font-weight: bold; border-radius: 4px;")
            self.delete_button.clicked.connect(self.on_delete_button_clicked)
            action_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(action_layout)
        
        # Tabla de mecánicos
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellidos", "Actividad"])
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
        
        # Deshabilitar botones hasta que se seleccione un mecánico
        self.edit_button.setEnabled(False)
        self.details_button.setEnabled(False)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(False)
        
        # Conectar señal de selección
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Etiqueta de información
        self.info_label = QLabel("Haga doble clic en un mecánico para ver sus detalles")
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        # Establecer margen y espaciado
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
    
    def refresh_data(self):
        """Actualiza los datos de la tabla"""
        self.mecanicos = self.mecanicos_dao.obtener_todos()
        self.populate_table(self.mecanicos)
    
    def populate_table(self, mecanicos):
        """Rellena la tabla con los datos de los mecánicos"""
        self.table.setRowCount(0)
        
        for mecanico in mecanicos:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # ID
            item_id = QTableWidgetItem(str(mecanico.id))
            item_id.setData(Qt.UserRole, mecanico.id)
            self.table.setItem(row_position, 0, item_id)
            
            # Nombre
            self.table.setItem(row_position, 1, QTableWidgetItem(mecanico.nombre))
            
            # Apellidos
            self.table.setItem(row_position, 2, QTableWidgetItem(mecanico.apellidos))
            
            # Actividad
            item_actividad = QTableWidgetItem(mecanico.actividad)
            
            # Colorear según la actividad
            if mecanico.actividad == Mecanico.ACTIVIDAD_SIN_ACTIVIDAD:
                item_actividad.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
            elif mecanico.actividad == Mecanico.ACTIVIDAD_REPARACION:
                item_actividad.setBackground(QBrush(QColor(255, 200, 200)))  # Rojo claro
            elif mecanico.actividad == Mecanico.ACTIVIDAD_MANTENIMIENTO:
                item_actividad.setBackground(QBrush(QColor(255, 230, 180)))  # Naranja claro
            
            self.table.setItem(row_position, 3, item_actividad)
        
        self.info_label.setText(f"Total: {len(mecanicos)} mecánicos")
    



    def apply_filters(self):
        """Aplica los filtros a la tabla"""
        nombre_filter = self.nombre_filter.text().strip().lower()
        actividad_filter = self.actividad_filter.currentData()
        
        filtered_mecanicos = []
        
        for mecanico in self.mecanicos:
            # Filtrar por nombre
            if nombre_filter and nombre_filter not in mecanico.nombre.lower() and nombre_filter not in mecanico.apellidos.lower():
                continue
            
            # Filtrar por actividad
            if actividad_filter and mecanico.actividad != actividad_filter:
                continue
            
            filtered_mecanicos.append(mecanico)
        
        self.populate_table(filtered_mecanicos)
    
    def clear_filters(self):
        """Limpia los filtros"""
        self.nombre_filter.clear()
        self.actividad_filter.setCurrentIndex(0)
        self.populate_table(self.mecanicos)
    
    def get_selected_mecanico(self):
        """Obtiene el mecánico seleccionado"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        index = selected_rows[0].row()
        mecanico_id = self.table.item(index, 0).data(Qt.UserRole)
        
        return self.mecanicos_dao.obtener_por_id(mecanico_id)
    
    def on_selection_changed(self):
        """Maneja el evento de cambio de selección"""
        mecanico = self.get_selected_mecanico()
        
        # Habilitar o deshabilitar botones según si hay selección
        enabled = mecanico is not None
        self.edit_button.setEnabled(enabled)
        self.details_button.setEnabled(enabled)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(enabled)
        
        if mecanico:
            self.mecanico_seleccionado.emit(mecanico)
    
    def on_table_double_clicked(self, index):
        """Maneja el evento de doble clic en la tabla"""
        mecanico = self.get_selected_mecanico()
        if mecanico:
            self.show_mecanico_details(mecanico)
    
    def on_add_button_clicked(self):
        """Maneja el evento de clic en el botón de agregar"""
        dialog = FormMecanicoDialog(parent=self)
        if dialog.exec_():
            # Refrescar datos después de agregar
            self.refresh_data()
    
    def on_edit_button_clicked(self):
        """Maneja el evento de clic en el botón de editar"""
        mecanico = self.get_selected_mecanico()
        if mecanico:
            dialog = FormMecanicoDialog(mecanico=mecanico, parent=self)
            if dialog.exec_():
                # Refrescar datos después de editar
                self.refresh_data()
    
    def on_details_button_clicked(self):
        """Maneja el evento de clic en el botón de detalles"""
        mecanico = self.get_selected_mecanico()
        if mecanico:
            self.show_mecanico_details(mecanico)
    
    def on_delete_button_clicked(self):
        """Maneja el evento de clic en el botón de eliminar"""
        mecanico = self.get_selected_mecanico()
        if not mecanico:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al mecánico {mecanico.nombre} {mecanico.apellidos}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Eliminar el mecánico
            if self.mecanicos_dao.eliminar(mecanico.id):
                QMessageBox.information(
                    self,
                    "Eliminación exitosa",
                    f"El mecánico {mecanico.nombre} {mecanico.apellidos} ha sido eliminado correctamente."
                )
                self.refresh_data()
            else:
                QMessageBox.warning(
                    self,
                    "Error al eliminar",
                    f"No se pudo eliminar al mecánico {mecanico.nombre} {mecanico.apellidos}."
                )
    
    def show_mecanico_details(self, mecanico):
        """Muestra el diálogo de detalles de un mecánico"""
        dialog = DetalleMecanicoDialog(mecanico, parent=self)
        dialog.exec_()
    
    def show_context_menu(self, position):
        """Muestra el menú contextual"""
        mecanico = self.get_selected_mecanico()
        if not mecanico:
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
            self.show_mecanico_details(mecanico)
        elif action == editar_action:
            dialog = FormMecanicoDialog(mecanico=mecanico, parent=self)
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
    
    widget = ListaMecanicosWidget(admin_user)
    widget.show()
    
    sys.exit(app.exec_())
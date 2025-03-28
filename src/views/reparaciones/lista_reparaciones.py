from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QLabel, QComboBox, QHeaderView, QMessageBox, QMenu,
                            QLineEdit, QDateEdit, QDialog, QFormLayout, QTextEdit, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from src.controllers.reparacion_controller import ReparacionController
from src.views.reparaciones.form_reparacion import FormReparaciones
import logging
import datetime

try:
    from PyQt5.QtWidgets import QStyle
except ImportError:
    from PyQt5.QtWidgets import QCommonStyle as QStyle

class ListaReparaciones(QWidget):
    def __init__(self, controller=None, parent=None):
        """
        Widget para mostrar y gestionar la lista de reparaciones
        
        Args:
            controller: Controlador de reparaciones (si None, se crea uno nuevo)
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Inicializar controlador
        self.controller = controller if controller is not None else ReparacionController()
        
        self.initUI()
        self.cargarReparaciones()
        
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Gestión de Reparaciones")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6a1b9a;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Controles de filtrado
        filter_layout = QHBoxLayout()
        
        # Filtro por estado
        filter_layout.addWidget(QLabel("Filtrar por estado:"))
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos", "En Espera", "En Reparación", "Reparado"])
        self.combo_filtro.currentTextChanged.connect(lambda: self.cargarReparaciones(self.combo_filtro.currentText()))
        filter_layout.addWidget(self.combo_filtro)
        
        # Filtro por matrícula
        filter_layout.addWidget(QLabel("Filtrar por matrícula:"))
        self.filtro_matricula = QLineEdit()
        self.filtro_matricula.setPlaceholderText("Ingrese matrícula")
        self.filtro_matricula.textChanged.connect(self.aplicarFiltros)
        filter_layout.addWidget(self.filtro_matricula)
        
        # Filtro por fechas
        filter_layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.dateChanged.connect(self.aplicarFiltros)
        filter_layout.addWidget(self.fecha_desde)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.dateChanged.connect(self.aplicarFiltros)
        filter_layout.addWidget(self.fecha_hasta)
        
        # Botón para limpiar filtros
        self.btn_limpiar_filtros = QPushButton("Limpiar Filtros")
        self.btn_limpiar_filtros.setStyleSheet("background-color: #e1bee7; font-weight: bold; border-radius: 4px;")
        self.btn_limpiar_filtros.clicked.connect(self.limpiarFiltros)
        filter_layout.addWidget(self.btn_limpiar_filtros)
        
        main_layout.addLayout(filter_layout)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.btn_nueva = QPushButton("Nueva Reparación")
        self.btn_nueva.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; border-radius: 4px; padding: 5px;")
        self.btn_nueva.clicked.connect(self.nuevaReparacion)
        action_layout.addWidget(self.btn_nueva)
        
        self.btn_ver_detalles = QPushButton("Ver Detalles")
        self.btn_ver_detalles.clicked.connect(self.verDetalles)
        action_layout.addWidget(self.btn_ver_detalles)
        
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editarReparacion)
        action_layout.addWidget(self.btn_editar)
        
        self.btn_cambiar_estado = QPushButton("Cambiar Estado")
        self.btn_cambiar_estado.clicked.connect(self.cambiarEstadoReparacion)
        action_layout.addWidget(self.btn_cambiar_estado)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;border-radius: 4px; padding: 5px;")
        self.btn_eliminar.clicked.connect(self.eliminarReparacion)
        action_layout.addWidget(self.btn_eliminar)
        
        main_layout.addLayout(action_layout)
        
        # Tabla de reparaciones
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)  # Ajustado el número de columnas
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Matrícula", "Modelo", "Estado", "Fecha Ingreso", 
            "Fecha Estimada", "Problema", "Total"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.doubleClicked.connect(self.verDetalles)
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self.mostrarMenuContextual)
        main_layout.addWidget(self.tabla)
        
        # Etiqueta de información
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.info_label)
        
        self.setLayout(main_layout)
        
        # Deshabilitar botones hasta que se seleccione una reparación
        self.btn_ver_detalles.setEnabled(False)
        self.btn_editar.setEnabled(False)
        self.btn_cambiar_estado.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
        
        # Conectar señal de selección
        self.tabla.itemSelectionChanged.connect(self.on_selection_changed)
        
    def cargarReparaciones(self, filtro_estado="Todos"):
        """
        Carga las reparaciones en la tabla según el filtro seleccionado
        
        Args:
            filtro_estado: Filtro de estado (opcional)
        """
        try:
            
            # Obtener todas las reparaciones
            todas_reparaciones = self.controller.obtener_todas_reparaciones()
            
            # Aplicar filtro por estado si es necesario
            if filtro_estado != "Todos":
                reparaciones_filtradas = [r for r in todas_reparaciones if r.get('estado') == filtro_estado]
            else:
                reparaciones_filtradas = todas_reparaciones
            
            # Almacenar las reparaciones filtradas para uso posterior
            self.reparaciones_actuales = reparaciones_filtradas
            
            # Aplicar los otros filtros activos
            self.aplicarFiltros()
            
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error al cargar reparaciones: {str(e)}")
            print(f"Traza detallada: {error_detallado}")
            QMessageBox.critical(self, "Error", f"Error al cargar reparaciones: {str(e)}")
    
    def aplicarFiltros(self):
        """Aplica todos los filtros activos a las reparaciones"""
        try:
            # Verificar si tenemos reparaciones para filtrar
            if not hasattr(self, 'reparaciones_actuales'):
                return
                
            # Obtener valores de filtros
            texto_matricula = self.filtro_matricula.text().strip().lower()
            fecha_desde = self.fecha_desde.date().toString("yyyy-MM-dd")
            fecha_hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")
            
            # Aplicar filtros a las reparaciones actuales
            reparaciones_filtradas = []
            
            for r in self.reparaciones_actuales:
                # Filtro por matrícula
                if texto_matricula and texto_matricula not in r.get('matricula', '').lower():
                    continue
                
                # Filtro por fecha de ingreso
                fecha_ingreso = r.get('fecha_ingreso', '')
                if fecha_ingreso:
                    if fecha_ingreso < fecha_desde or fecha_ingreso > fecha_hasta:
                        continue
                
                # Pasó todos los filtros
                reparaciones_filtradas.append(r)
            
            # Mostrar reparaciones en la tabla
            self.mostrarReparacionesEnTabla(reparaciones_filtradas)
            
        except Exception as e:
            print(f"Error al aplicar filtros: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def limpiarFiltros(self):
        """Limpia todos los filtros aplicados"""
        self.combo_filtro.setCurrentIndex(0)  # "Todos"
        self.filtro_matricula.clear()
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_hasta.setDate(QDate.currentDate())
        
        # Recargar todas las reparaciones
        self.cargarReparaciones()
    
    def mostrarReparacionesEnTabla(self, reparaciones):
        """
        Muestra las reparaciones en la tabla
        
        Args:
            reparaciones: Lista de reparaciones a mostrar
        """
        # Limpiar tabla
        self.tabla.setRowCount(0)
        
        # Agregar filas a la tabla
        for reparacion in reparaciones:
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            
            # Llenar celdas
            self.tabla.setItem(row_position, 0, QTableWidgetItem(str(reparacion.get('id', ''))))
            self.tabla.setItem(row_position, 1, QTableWidgetItem(reparacion.get('matricula', '')))
            self.tabla.setItem(row_position, 2, QTableWidgetItem(reparacion.get('modelo', '')))
            self.tabla.setItem(row_position, 3, QTableWidgetItem(reparacion.get('estado', '')))
            self.tabla.setItem(row_position, 4, QTableWidgetItem(reparacion.get('fecha_ingreso', '')))
            self.tabla.setItem(row_position, 5, QTableWidgetItem(reparacion.get('fecha_entrega_estimada', '')))
            
            # Acortar el problema si es muy largo
            problema = reparacion.get('problema', '')
            if len(problema) > 30:
                problema = problema[:27] + '...'
            self.tabla.setItem(row_position, 6, QTableWidgetItem(problema))
            
            # Formatear el total como moneda
            total = reparacion.get('total', 0)
            self.tabla.setItem(row_position, 7, QTableWidgetItem(f"${total:.2f}"))
            
            # Guardar el objeto reparación en el item para uso posterior
            self.tabla.item(row_position, 0).setData(Qt.UserRole, reparacion)
            
            # Colorear según estado
            estado = reparacion.get('estado')
            
            if estado == "En Espera":
                color = QColor(255, 255, 200)  # Amarillo claro
            elif estado == "En Reparación":
                color = QColor(255, 200, 200)  # Rojo claro
            elif estado == "Reparado":
                color = QColor(200, 255, 200)  # Verde claro
            else:
                color = QColor(Qt.white)
            
            # Aplicar color a todas las celdas de la fila
            for col in range(self.tabla.columnCount()):
                self.tabla.item(row_position, col).setBackground(QBrush(color))
        
        # Actualizar etiqueta de información
        self.info_label.setText(f"Total: {self.tabla.rowCount()} reparaciones")
    
    def on_selection_changed(self):
        """Maneja el evento de cambio de selección en la tabla"""
        # Verificar si hay una fila seleccionada
        selected = len(self.tabla.selectedItems()) > 0
        
        # Habilitar/deshabilitar botones según la selección
        self.btn_ver_detalles.setEnabled(selected)
        self.btn_editar.setEnabled(selected)
        self.btn_cambiar_estado.setEnabled(selected)
        self.btn_eliminar.setEnabled(selected)
    
    def obtenerReparacionSeleccionada(self):
        """
        Obtiene la reparación seleccionada en la tabla
        
        Returns:
            dict: Datos de la reparación seleccionada o None si no hay selección
        """
        selected_rows = self.tabla.selectionModel().selectedRows()
        if not selected_rows:
            return None
            
        # Obtener la reparación del ítem seleccionado
        row = selected_rows[0].row()
        return self.tabla.item(row, 0).data(Qt.UserRole)
    
    def nuevaReparacion(self):
        """Abre el formulario para crear una nueva reparación"""
        try:
            # Mostrar formulario
            form = FormReparaciones(self.controller, parent=self)
            if form.exec_():
                # Recargar lista tras agregar
                self.cargarReparaciones(self.combo_filtro.currentText())
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def editarReparacion(self):
        """Edita la reparación seleccionada"""
        reparacion = self.obtenerReparacionSeleccionada()
        if not reparacion:
            QMessageBox.warning(self, "Selección", "Debe seleccionar una reparación para editar")
            return
            
        try:
            # Mostrar formulario para editar
            form = FormReparaciones(self.controller, reparacion, self)
            if form.exec_():
                # Recargar lista tras editar
                self.cargarReparaciones(self.combo_filtro.currentText())
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el formulario: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def verDetalles(self):
        """Muestra los detalles de la reparación seleccionada"""
        reparacion = self.obtenerReparacionSeleccionada()
        if not reparacion:
            QMessageBox.warning(self, "Selección", "Debe seleccionar una reparación para ver sus detalles")
            return
            
        try:
            # Para este ejemplo, mostramos un diálogo simple con los detalles
            detalles = f"""
            <h2>Detalles de la Reparación #{reparacion['id']}</h2>
            <p><b>Camión:</b> {reparacion['matricula']} - {reparacion['modelo']} ({reparacion['anio']})</p>
            <p><b>Estado:</b> {reparacion['estado']}</p>
            <p><b>Fechas:</b> Ingreso: {reparacion['fecha_ingreso']} | Entrega Est.: {reparacion['fecha_entrega_estimada']}</p>
            <p><b>Problema:</b> {reparacion['problema']}</p>
            <p><b>Diagnóstico:</b> {reparacion['diagnostico']}</p>
            <p><b>Costos:</b> Repuestos: ${reparacion['costo_repuestos']:.2f} | Mano de Obra: ${reparacion['costo_mano_obra']:.2f}</p>
            <p><b>Total:</b> ${reparacion['total']:.2f}</p>
            <p><b>Notas:</b> {reparacion.get('notas', 'Sin notas adicionales')}</p>
            """
            
            QMessageBox.information(self, f"Detalles de Reparación #{reparacion['id']}", detalles)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron mostrar los detalles: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def cambiarEstadoReparacion(self):
        """Cambia el estado de la reparación seleccionada"""
        reparacion = self.obtenerReparacionSeleccionada()
        if not reparacion:
            QMessageBox.warning(self, "Selección", "Debe seleccionar una reparación para cambiar su estado")
            return
            
        # Diálogo para seleccionar el nuevo estado
        estados = ["En Espera", "En Reparación", "Reparado"]
        estado_actual = reparacion.get('estado', '')
        index_actual = estados.index(estado_actual) if estado_actual in estados else 0
        
        from PyQt5.QtWidgets import QInputDialog
        
        nuevo_estado, ok = QInputDialog.getItem(
            self, 
            "Cambiar Estado", 
            "Seleccione el nuevo estado:", 
            estados, 
            index_actual, 
            False
        )
        
        if ok and nuevo_estado != estado_actual:
            try:
                # Crear copia de los datos actuales
                datos_actualizados = reparacion.copy()
                # Actualizar el estado
                datos_actualizados['estado'] = nuevo_estado
                
                # Guardar cambios
                if self.controller.actualizar_reparacion(reparacion['id'], datos_actualizados):
                    QMessageBox.information(
                        self, 
                        "Estado actualizado", 
                        f"El estado de la reparación #{reparacion['id']} ha sido actualizado a '{nuevo_estado}'"
                    )
                    # Recargar lista
                    self.cargarReparaciones(self.combo_filtro.currentText())
                else:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "No se pudo actualizar el estado de la reparación"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cambiar el estado: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def eliminarReparacion(self):
        """Elimina la reparación seleccionada"""
        reparacion = self.obtenerReparacionSeleccionada()
        if not reparacion:
            QMessageBox.warning(self, "Selección", "Debe seleccionar una reparación para eliminar")
            return
            
        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Está seguro de eliminar la reparación #{reparacion['id']} del camión {reparacion.get('matricula')}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                # Eliminar reparación
                if self.controller.eliminar_reparacion(reparacion['id']):
                    QMessageBox.information(self, "Éxito", "Reparación eliminada correctamente")
                    # Recargar lista
                    self.cargarReparaciones(self.combo_filtro.currentText())
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar la reparación")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def mostrarMenuContextual(self, position):
        """Muestra el menú contextual en la tabla"""
        # Verificar si hay una reparación seleccionada
        reparacion = self.obtenerReparacionSeleccionada()
        if not reparacion:
            return
            
        # Crear menú contextual
        menu = QMenu(self)
        
        # Acciones
        accion_ver = menu.addAction("Ver Detalles")
        accion_editar = menu.addAction("Editar")
        accion_cambiar_estado = menu.addAction("Cambiar Estado")
        menu.addSeparator()
        accion_eliminar = menu.addAction("Eliminar")
        
        # Colorear la acción de eliminar en rojo
        try:
            accion_eliminar.setIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton))
        except:
            pass
        
        # Mostrar menú y obtener acción seleccionada
        accion = menu.exec_(self.tabla.viewport().mapToGlobal(position))
        
        # Procesar acción seleccionada
        if accion == accion_ver:
            self.verDetalles()
        elif accion == accion_editar:
            self.editarReparacion()
        elif accion == accion_cambiar_estado:
            self.cambiarEstadoReparacion()
        elif accion == accion_eliminar:
            self.eliminarReparacion()
            
    def print_data(self, printer):
        """
        Imprime los datos de la tabla
        
        Args:
            printer: Objeto QPrinter para imprimir
        """
        from PyQt5.QtGui import QTextDocument
        from PyQt5.QtCore import QDate
        
        try:
            doc = QTextDocument()
            
            # Crear contenido HTML para imprimir
            html = """
            <html>
            <head>
                <style>
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid black; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .header { font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 20px; }
                    .footer { font-size: 12px; text-align: right; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="header">Reporte de Reparaciones</div>
                <p>Fecha de impresión: {}</p>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Matrícula</th>
                        <th>Estado</th>
                        <th>Fecha Ingreso</th>
                        <th>Problema</th>
                        <th>Total</th>
                    </tr>
            """.format(QDate.currentDate().toString("dd/MM/yyyy"))
            
            # Agregar filas
            for row in range(self.tabla.rowCount()):
                html += "<tr>"
                html += f"<td>{self.tabla.item(row, 0).text()}</td>"  # ID
                html += f"<td>{self.tabla.item(row, 1).text()}</td>"  # Matrícula
                html += f"<td>{self.tabla.item(row, 3).text()}</td>"  # Estado
                html += f"<td>{self.tabla.item(row, 4).text()}</td>"  # Fecha Ingreso
                html += f"<td>{self.tabla.item(row, 6).text()}</td>"  # Problema
                html += f"<td>{self.tabla.item(row, 7).text()}</td>"  # Total
                html += "</tr>"
            
            # Cerrar tabla y agregar footer
            html += """
                </table>
                <div class="footer">
                    Total de reparaciones: {}
                </div>
            </body>
            </html>
            """.format(self.tabla.rowCount())
            
            # Establecer el contenido HTML en el documento
            doc.setHtml(html)
            
            # Imprimir el documento
            doc.print_(printer)
            
            print("Datos impresos correctamente")
            return True
        except Exception as e:
            print(f"Error al imprimir datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QFormLayout, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QTextEdit, QComboBox, 
                           QPushButton, QDateEdit, QLabel, QSpinBox, QDoubleSpinBox, 
                           QMessageBox, QFrame, QGridLayout, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from database.camiones_dao import CamionesDAO
from database.mecanicos_dao import MecanicosDAO
from models.camion import Camion
from models.mecanico import Mecanico

class FormReparaciones(QDialog):
    def __init__(self, controller, reparacion=None, parent=None):
        """
        Formulario para agregar o editar una reparación
        
        Args:
            controller: Controlador de reparaciones
            reparacion: Diccionario con datos de reparación (None para nueva)
            parent: Widget padre
        """
        super().__init__(parent)
        self.controller = controller
        self.reparacion = reparacion
        self.setWindowTitle("Nueva Reparación" if reparacion is None else "Editar Reparación")
        self.resize(700, 750)  # Ventana más grande
        
        # Inicializar DAOs
        self.camiones_dao = CamionesDAO()
        self.mecanicos_dao = MecanicosDAO()
        
        # Cargar datos necesarios
        self.camiones = self.cargarCamiones()
        self.mecanicos = self.cargarMecanicos()
        
        self.initUI()
        
        # Si estamos editando, llenar el formulario con los datos
        if reparacion is not None:
            self.cargarDatosReparacion()
            
    def cargarCamiones(self):
        """
        Carga la lista de camiones desde la base de datos
        
        Returns:
            list: Lista de diccionarios con datos de camiones
        """
        try:
            # Obtener todos los camiones
            camiones_obj = self.camiones_dao.obtener_todos()
            
            # Convertir objetos Camion a diccionarios y filtrar los que están en reparación
            # excepto si estamos editando (en este caso, incluir también el camión actualmente en reparación)
            camiones_list = []
            camion_actual_id = None
            
            # Si estamos editando una reparación, obtener el ID del camión actual
            if self.reparacion and 'camion_id' in self.reparacion:
                camion_actual_id = self.reparacion.get('camion_id')
            
            for camion in camiones_obj:
                # Incluir solo camiones que no estén en reparación O el camión de la reparación actual (en caso de edición)
                camion_id_str = str(camion.id)
                if camion.estado != "En Reparación" or camion_id_str == camion_actual_id:
                    camiones_list.append({
                        "id": camion_id_str,
                        "matricula": camion.matricula,
                        "modelo": camion.modelo,
                        "anio": camion.año,
                        "estado": camion.estado
                    })
            
            print(f"Camiones cargados (excluyendo los que ya están en reparación): {len(camiones_list)}")
            return camiones_list
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error al cargar camiones: {str(e)}")
            print(f"Traza detallada: {error_detallado}")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los camiones: {str(e)}")
            return []
            
    def cargarMecanicos(self):
        """Carga la lista de mecánicos desde la base de datos"""
        try:
            # Usar el DAO de mecánicos para obtener todos los mecánicos de la base de datos
            mecanicos_obj = self.mecanicos_dao.obtener_todos()
            
            # Convertir objetos Mecanico a diccionarios
            mecanicos_list = []
            for mecanico in mecanicos_obj:
                mecanicos_list.append({
                    "id": str(mecanico.id),  # Convertir ObjectId a string para compatibilidad
                    "nombre": mecanico.nombre,
                    "apellidos": mecanico.apellidos,
                    "actividad": mecanico.actividad
                })
            
            # Imprimir información para depuración
            print(f"Mecánicos cargados: {len(mecanicos_list)}")
            for m in mecanicos_list[:3]:  # Mostrar los primeros 3 como ejemplo
                print(f"  - {m['nombre']} {m['apellidos']} - {m['actividad']}")
            
            # Si no hay mecánicos en la base de datos, mostrar advertencia
            if not mecanicos_list:
                QMessageBox.warning(
                    self, 
                    "Sin mecánicos", 
                    "No se encontraron mecánicos en la base de datos. Por favor, agregue mecánicos primero."
                )
            
            return mecanicos_list
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error al cargar mecánicos: {str(e)}")
            print(f"Traza detallada: {error_detallado}")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los mecánicos: {str(e)}")
            return []
            
    def initUI(self):
        """Inicializa la interfaz de usuario"""
        # Establecer una fuente más grande para todo el diálogo
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Barra superior morada
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #6a1b9a;")
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Título en la barra morada
        title_label = QLabel("Formulario de Reparación")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Label informativo
        info_label = QLabel("Complete el formulario con los datos de la reparación")
        info_label.setStyleSheet("font-weight: bold; color: #6a1b9a; font-size: 14px;")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)  # Alineación a la izquierda 
        form_layout.setFormAlignment(Qt.AlignLeft)   # Alineación a la izquierda
        form_layout.setVerticalSpacing(15)  # Más espacio entre campos
        
        # Estilo para las etiquetas del formulario
        label_style = "font-size: 18px; font-weight: bold;"
        
        
        
        # Contenedor para el filtro y selector
        camion_container = QVBoxLayout()
        
        # Añadir campo de filtro por matrícula
        self.filtro_matricula = QLineEdit()
        self.filtro_matricula.setPlaceholderText("Buscar camión")
        self.filtro_matricula.setMaxLength(20)
        self.filtro_matricula.setMinimumHeight(35)
        self.filtro_matricula.setStyleSheet("font-size: 18px; padding: 5px; border: 1px solid #ccc; border-radius: 4px;")
        self.filtro_matricula.textChanged.connect(self.filtrar_camiones)
        camion_container.addWidget(self.filtro_matricula)
        

        # Selector de camión
        self.combo_camion = QComboBox()
        self.combo_camion.setMinimumWidth(300)
        self.combo_camion.setMinimumHeight(35)
        self.combo_camion.setStyleSheet("font-size: 18px;")
        
        # Verificar si hay camiones disponibles
        if not self.camiones:
            QMessageBox.warning(self, "Advertencia", "No hay camiones disponibles. Por favor, agregue camiones primero.")
        
        # Guardar una copia de los camiones para poder filtrarlos
        self.todos_camiones = self.camiones.copy()

        # Crear campos para el filtro y selector de camión
        camion_label = QLabel("Buscar Camión:")
        camion_label.setStyleSheet(label_style)
        
        camion_label = QLabel("Camión seleccionado:")
        camion_label.setStyleSheet(label_style)

        # Agregar los camiones al combo
        self.cargar_camiones_en_combo()
        
        camion_container.addWidget(self.combo_camion)
        form_layout.addRow(camion_label, camion_container)
        
        # Selector de mecánico responsable
        mecanico_label = QLabel("Mecánico Responsable:")
        mecanico_label.setStyleSheet(label_style)
        
        self.combo_mecanico = QComboBox()
        self.combo_mecanico.setMinimumWidth(300)
        self.combo_mecanico.setMinimumHeight(35)
        self.combo_mecanico.setStyleSheet("font-size: 18px;")
        
        # Verificar si hay mecánicos disponibles
        if not self.mecanicos:
            QMessageBox.warning(self, "Advertencia", "No hay mecánicos disponibles. Por favor, agregue mecánicos primero.")
        else:
            # Agregar los mecánicos al combo
            for mecanico in self.mecanicos:
                display_text = f"{mecanico['nombre']} {mecanico['apellidos']}"
                if 'actividad' in mecanico and mecanico['actividad']:
                    display_text += f" - {mecanico['actividad']}"
                self.combo_mecanico.addItem(display_text, mecanico['id'])
        
        form_layout.addRow(mecanico_label, self.combo_mecanico)
        
        # Campos para datos de la reparación
        fecha_ingreso_label = QLabel("Fecha de Ingreso:")
        fecha_ingreso_label.setStyleSheet(label_style)
        self.fecha_ingreso = QDateEdit()
        self.fecha_ingreso.setDate(QDate.currentDate())
        self.fecha_ingreso.setCalendarPopup(True)
        self.fecha_ingreso.setMinimumHeight(35)
        form_layout.addRow(fecha_ingreso_label, self.fecha_ingreso)
        
        fecha_entrega_label = QLabel("Fecha Estimada de Entrega:")
        fecha_entrega_label.setStyleSheet(label_style)
        self.fecha_entrega_estimada = QDateEdit()
        self.fecha_entrega_estimada.setDate(QDate.currentDate().addDays(7))
        self.fecha_entrega_estimada.setCalendarPopup(True)
        self.fecha_entrega_estimada.setMinimumHeight(35)
        form_layout.addRow(fecha_entrega_label, self.fecha_entrega_estimada)
        
        estado_label = QLabel("Estado:")
        estado_label.setStyleSheet(label_style)
        self.estado = QComboBox()
        self.estado.setMinimumHeight(35)
        self.estado.setStyleSheet("font-size: 18px;")
        
        # Usar los estados definidos en el modelo
        try:
            from models.reparacion import Reparacion
            self.estados_disponibles = ["En Espera", "En Reparación", "Reparado"]
        except ImportError:
            self.estados_disponibles = ["En Espera", "En Reparación", "Reparado"]
            
        self.estado.addItems(self.estados_disponibles)
        form_layout.addRow(estado_label, self.estado)
        
        problema_label = QLabel("Problema Reportado:")
        problema_label.setStyleSheet(label_style)
        self.problema = QTextEdit()
        self.problema.setPlaceholderText("Describa el problema reportado por el cliente")
        self.problema.setMinimumHeight(80)
        self.problema.setStyleSheet("font-size: 18px;")
        form_layout.addRow(problema_label, self.problema)
        
        diagnostico_label = QLabel("Diagnóstico:")
        diagnostico_label.setStyleSheet(label_style)
        self.diagnostico = QTextEdit()
        self.diagnostico.setPlaceholderText("Escriba el diagnóstico técnico del problema")
        self.diagnostico.setMinimumHeight(80)
        self.diagnostico.setStyleSheet("font-size: 18px;")
        form_layout.addRow(diagnostico_label, self.diagnostico)
        
        # Campos para costos
        costo_repuestos_label = QLabel("Costo de Repuestos:")
        costo_repuestos_label.setStyleSheet(label_style)
        self.costo_repuestos = QDoubleSpinBox()
        self.costo_repuestos.setRange(0, 999999.99)
        self.costo_repuestos.setDecimals(2)
        self.costo_repuestos.setPrefix("$ ")
        self.costo_repuestos.setMinimumHeight(35)
        self.costo_repuestos.setStyleSheet("font-size: 18px;")
        form_layout.addRow(costo_repuestos_label, self.costo_repuestos)
        
        costo_mano_obra_label = QLabel("Costo de Mano de Obra:")
        costo_mano_obra_label.setStyleSheet(label_style)
        self.costo_mano_obra = QDoubleSpinBox()
        self.costo_mano_obra.setRange(0, 999999.99)
        self.costo_mano_obra.setDecimals(2)
        self.costo_mano_obra.setPrefix("$ ")
        self.costo_mano_obra.setMinimumHeight(35)
        self.costo_mano_obra.setStyleSheet("font-size: 18px;")
        form_layout.addRow(costo_mano_obra_label, self.costo_mano_obra)
        
        total_label = QLabel("Total:")
        total_label.setStyleSheet(label_style)
        self.total = QDoubleSpinBox()
        self.total.setRange(0, 999999.99)
        self.total.setDecimals(2)
        self.total.setReadOnly(True)
        self.total.setPrefix("$ ")
        self.total.setMinimumHeight(35)
        self.total.setStyleSheet("font-size: 18px; background-color: #f0f0f0; font-weight: bold;")
        form_layout.addRow(total_label, self.total)
        
        # Conectar eventos para calcular total
        self.costo_repuestos.valueChanged.connect(self.calcularTotal)
        self.costo_mano_obra.valueChanged.connect(self.calcularTotal)
        
        # Notas adicionales
        notas_label = QLabel("Notas Adicionales:")
        notas_label.setStyleSheet(label_style)
        self.notas = QTextEdit()
        self.notas.setPlaceholderText("Notas adicionales sobre la reparación")
        self.notas.setMinimumHeight(80)
        self.notas.setStyleSheet("font-size: 18px;")
        form_layout.addRow(notas_label, self.notas)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # Más espacio entre botones
        
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setMinimumHeight(40)  # Altura mínima aumentada
        self.btn_guardar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px; border-radius: 4px;")
        self.btn_guardar.clicked.connect(self.guardar)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setMinimumHeight(40)  # Altura mínima aumentada
        self.btn_cancelar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px; font-size: 14px; border-radius: 4px;")
        self.btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cancelar)
        
        main_layout.addLayout(button_layout)
        
        # Calcular total inicial
        self.calcularTotal()
    
    def cargar_camiones_en_combo(self):
        """Carga los camiones en el combo box"""
        # Limpiar el combo
        self.combo_camion.clear()
        
        # Agregar los camiones al combo
        for camion in self.camiones:
            # Mostrar estado del camión en el texto del combo
            estado_camion = camion['estado']
            texto_item = f"{camion['matricula']} - {camion['modelo']} ({camion['anio']})"
            
            # Si el camión está en reparación, indicarlo claramente
            if estado_camion == "En Reparación":
                texto_item += " [YA EN REPARACIÓN]"
                
            self.combo_camion.addItem(texto_item, camion['id'])
        
        # Si no hay camiones después de filtrar, mostrar un mensaje apropiado
        if self.combo_camion.count() == 0:
            self.combo_camion.addItem("No hay camiones disponibles que coincidan con el filtro", None)

    def filtrar_camiones(self):
        """Filtra los camiones según el texto ingresado en el campo de búsqueda"""
        texto_filtro = self.filtro_matricula.text().strip().lower()
        
        if not texto_filtro:
            # Si no hay texto de filtro, mostrar todos los camiones
            self.camiones = self.todos_camiones.copy()
        else:
            # Filtrar los camiones por matrícula
            self.camiones = [c for c in self.todos_camiones if texto_filtro in c['matricula'].lower()]
        
        # Actualizar el combo box con los camiones filtrados
        self.cargar_camiones_en_combo()
        
        # Si hay un solo camión que coincide con el filtro, seleccionarlo
        if len(self.camiones) == 1:
            self.combo_camion.setCurrentIndex(0)
    
    def calcularTotal(self):
        """Calcula el total sumando repuestos y mano de obra"""
        total = self.costo_repuestos.value() + self.costo_mano_obra.value()
        self.total.setValue(total)
        
    def cargarDatosReparacion(self):
        """Carga los datos de la reparación en el formulario"""
        try:
            print(f"Cargando datos de reparación: {self.reparacion}")
            
            # Seleccionar el camión
            camion_id = self.reparacion.get('camion_id')
            if camion_id:
                index = self.combo_camion.findData(camion_id)
                if index >= 0:
                    self.combo_camion.setCurrentIndex(index)
                    print(f"Camión seleccionado: {self.combo_camion.currentText()}")
                else:
                    print(f"No se encontró el camión con ID: {camion_id}")
            
            # Seleccionar el mecánico
            mecanico_id = self.reparacion.get('mecanico_id')
            if mecanico_id:
                index = self.combo_mecanico.findData(mecanico_id)
                if index >= 0:
                    self.combo_mecanico.setCurrentIndex(index)
                    print(f"Mecánico seleccionado: {self.combo_mecanico.currentText()}")
                else:
                    print(f"No se encontró el mecánico con ID: {mecanico_id}")
            
            # Datos de la reparación
            fecha_ingreso = QDate.fromString(self.reparacion.get('fecha_ingreso', ''), 'yyyy-MM-dd')
            if fecha_ingreso.isValid():
                self.fecha_ingreso.setDate(fecha_ingreso)
                print(f"Fecha de ingreso: {fecha_ingreso.toString('dd/MM/yyyy')}")
                
            fecha_entrega = QDate.fromString(self.reparacion.get('fecha_entrega_estimada', ''), 'yyyy-MM-dd')
            if fecha_entrega.isValid():
                self.fecha_entrega_estimada.setDate(fecha_entrega)
                print(f"Fecha estimada de entrega: {fecha_entrega.toString('dd/MM/yyyy')}")
                
            estado = self.reparacion.get('estado', '')
            if estado in self.estados_disponibles:
                index = self.estado.findText(estado)
                if index >= 0:
                    self.estado.setCurrentIndex(index)
                    print(f"Estado seleccionado: {estado}")
                
            self.problema.setText(self.reparacion.get('problema', ''))
            self.diagnostico.setText(self.reparacion.get('diagnostico', ''))
            
            # Costos
            costo_repuestos = float(self.reparacion.get('costo_repuestos', 0))
            self.costo_repuestos.setValue(costo_repuestos)
            print(f"Costo de repuestos: ${costo_repuestos:.2f}")
            
            costo_mano_obra = float(self.reparacion.get('costo_mano_obra', 0))
            self.costo_mano_obra.setValue(costo_mano_obra)
            print(f"Costo de mano de obra: ${costo_mano_obra:.2f}")
            
            self.calcularTotal()
            
            # Notas
            self.notas.setText(self.reparacion.get('notas', ''))
            
            print("Datos de reparación cargados correctamente")
        except Exception as e:
            print(f"Error al cargar datos de reparación: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def validarFormulario(self):
        """Valida que los campos requeridos estén completos"""
        if self.combo_camion.currentIndex() < 0 or self.combo_camion.currentData() is None:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un camión válido")
            self.filtro_matricula.setFocus()
            return False
            
        if self.combo_mecanico.currentIndex() < 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un mecánico responsable")
            return False
            
        if not self.problema.toPlainText().strip():
            QMessageBox.warning(self, "Validación", "Debe indicar el problema reportado")
            self.problema.setFocus()
            return False
            
        return True
    
    def obtenerDatosFormulario(self):
        """Obtiene los datos del formulario en formato de diccionario"""
        # Obtener IDs seleccionados
        camion_id = self.combo_camion.currentData()
        mecanico_id = self.combo_mecanico.currentData()
        
        # Obtener datos del camión para incluirlos en el registro
        camion = next((c for c in self.camiones if c['id'] == camion_id), {})
        
        datos = {
            # No incluimos 'id' aquí para nuevas reparaciones
            'camion_id': camion_id,
            'matricula': camion.get('matricula', ''),
            'modelo': camion.get('modelo', ''),
            'anio': camion.get('anio', 0),
            'mecanico_id': mecanico_id,
            'fecha_ingreso': self.fecha_ingreso.date().toString('yyyy-MM-dd'),
            'fecha_entrega_estimada': self.fecha_entrega_estimada.date().toString('yyyy-MM-dd'),
            'estado': self.estado.currentText(),
            'problema': self.problema.toPlainText(),
            'diagnostico': self.diagnostico.toPlainText(),
            'costo_repuestos': self.costo_repuestos.value(),
            'costo_mano_obra': self.costo_mano_obra.value(),
            'total': self.total.value(),
            'notas': self.notas.toPlainText()
        }
        
        # Solo agregar ID si estamos editando y existe un ID válido
        if self.reparacion is not None and 'id' in self.reparacion:
            datos['id'] = self.reparacion['id']
            
        return datos
        
    def guardar(self):
        """Guarda los datos de la reparación"""
        if not self.validarFormulario():
            return
            
        datos = self.obtenerDatosFormulario()
        
        try:
            print(f"DEBUG - Guardando datos de reparación: {datos}")
            
            if self.reparacion is None:
                # Nueva reparación - asegurarnos de no enviar un ID
                if 'id' in datos:
                    del datos['id']
                
                # También actualizar el estado del camión a "En Reparación"
                self.actualizarEstadoCamion(datos['camion_id'], "En Reparación")
                
                id_reparacion = self.controller.agregar_reparacion(datos)
                print(f"DEBUG - Nueva reparación creada con ID: {id_reparacion}")
                QMessageBox.information(self, "Éxito", f"Reparación #{id_reparacion} registrada correctamente")
            else:
                # Actualizar reparación existente
                if 'id' in self.reparacion and self.reparacion['id'] is not None:
                    id_reparacion = self.reparacion['id']
                    
                    # Si el estado cambia a "Reparado", actualizar el estado del camión
                    if datos['estado'] == "Reparado" and self.reparacion.get('estado') != "Reparado":
                        self.actualizarEstadoCamion(datos['camion_id'], "Operativo")
                    
                    self.controller.actualizar_reparacion(id_reparacion, datos)
                    print(f"DEBUG - Reparación #{id_reparacion} actualizada correctamente")
                    QMessageBox.information(self, "Éxito", f"Reparación #{id_reparacion} actualizada correctamente")
                else:
                    # Si no hay ID, tratar como nueva reparación
                    if 'id' in datos:
                        del datos['id']
                    
                    # También actualizar el estado del camión a "En Reparación"
                    self.actualizarEstadoCamion(datos['camion_id'], "En Reparación")
                    
                    id_reparacion = self.controller.agregar_reparacion(datos)
                    print(f"DEBUG - Nueva reparación creada con ID: {id_reparacion}")
                    QMessageBox.information(self, "Éxito", f"Reparación #{id_reparacion} registrada como nueva")
            
            # Asegurarnos de que la lista de reparaciones se actualice en la ventana principal
            try:
                # Buscar el widget de reparaciones en la jerarquía de padres
                parent_window = self.parent()
                while parent_window and not hasattr(parent_window, 'reparaciones_widget'):
                    parent_window = parent_window.parent()
                    
                if parent_window and hasattr(parent_window, 'reparaciones_widget') and parent_window.reparaciones_widget:
                    print("DEBUG - Actualizando lista de reparaciones...")
                    parent_window.reparaciones_widget.cargarReparaciones()
                else:
                    # Si no encontramos el widget directamente, intentar encontrar la ventana principal
                    print("DEBUG - Buscando ventana principal para actualizar reparaciones...")
                    main_window = self.parent()
                    while main_window and not hasattr(main_window, 'refresh_data'):
                        main_window = main_window.parent()
                    
                    if main_window and hasattr(main_window, 'refresh_data'):
                        print("DEBUG - Refrescando datos de la aplicación...")
                        main_window.refresh_data()
            except Exception as e:
                print(f"DEBUG - Advertencia al actualizar UI después de guardar: {str(e)}")
                # No mostrar este error al usuario, solo registrarlo
            
            self.accept()
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"DEBUG - Error detallado al guardar reparación: {error_detallado}")
            QMessageBox.critical(self, "Error", f"No se pudo guardar la reparación: {str(e)}")
    
    def actualizarEstadoCamion(self, camion_id, nuevo_estado):
        """
        Actualiza el estado del camión
        
        Args:
            camion_id: ID del camión
            nuevo_estado: Nuevo estado para el camión
        """
        try:
            # Obtener el camión
            camion = self.camiones_dao.obtener_por_id(camion_id)
            if camion:
                # Actualizar el estado
                camion.estado = nuevo_estado
                # Guardar en la base de datos
                self.camiones_dao.actualizar(camion)
                print(f"Estado del camión {camion.matricula} actualizado a: {nuevo_estado}")
        except Exception as e:
            print(f"Error al actualizar estado del camión: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Solo para pruebas
    from src.controllers.reparacion_controller import ReparacionController
    controller = ReparacionController()
    form = FormReparaciones(controller)
    form.show()
    sys.exit(app.exec_())

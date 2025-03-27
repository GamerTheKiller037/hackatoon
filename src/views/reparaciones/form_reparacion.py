import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QFormLayout, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QTextEdit, QComboBox, 
                           QPushButton, QDateEdit, QLabel, QSpinBox, QDoubleSpinBox, 
                           QMessageBox)
from PyQt5.QtCore import Qt, QDate
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
        self.resize(500, 600)
        
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
            
            # Convertir objetos Camion a diccionarios para mantener la compatibilidad
            camiones_list = []
            for camion in camiones_obj:
                camiones_list.append({
                    "id": str(camion.id),
                    "matricula": camion.matricula,
                    "modelo": camion.modelo,
                    "anio": camion.año,
                    "estado": camion.estado
                })
            
            # Imprimir información para depuración
            
            
            return camiones_list
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error al cargar camiones: {str(e)}")
            print(f"Traza detallada: {error_detallado}")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los camiones: {str(e)}")
            return []
            
    def cargarMecanicos(self):
        """
        Carga la lista de mecánicos desde la base de datos
        
        Returns:
            list: Lista de diccionarios con datos de mecánicos
        """
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
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        # Label informativo
        info_label = QLabel("Complete el formulario con los datos de la reparación")
        info_label.setStyleSheet("font-weight: bold; color: #3f51b5;")
        main_layout.addWidget(info_label)
        
        # Selector de camión
        self.combo_camion = QComboBox()
        self.combo_camion.setMinimumWidth(300)
        
        # Verificar si hay camiones disponibles
        if not self.camiones:
            QMessageBox.warning(self, "Advertencia", "No hay camiones disponibles. Por favor, agregue camiones primero.")
        
        # Agregar los camiones al combo
        for camion in self.camiones:
            self.combo_camion.addItem(f"{camion['matricula']} - {camion['modelo']} ({camion['anio']})", camion['id'])
        
        # Selector de mecánico responsable
        self.combo_mecanico = QComboBox()
        self.combo_mecanico.setMinimumWidth(300)
        
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
        
        # Campos para datos de la reparación
        self.fecha_ingreso = QDateEdit()
        self.fecha_ingreso.setDate(QDate.currentDate())
        self.fecha_ingreso.setCalendarPopup(True)
        
        self.fecha_entrega_estimada = QDateEdit()
        self.fecha_entrega_estimada.setDate(QDate.currentDate().addDays(7))
        self.fecha_entrega_estimada.setCalendarPopup(True)
        
        self.estado = QComboBox()
        
        # Usar los estados definidos en el modelo
        try:
            from models.reparacion import Reparacion
            self.estados_disponibles = ["En Espera", "En Reparación", "Reparado"]
        except ImportError:
            self.estados_disponibles = ["En Espera", "En Reparación", "Reparado"]
            
        self.estado.addItems(self.estados_disponibles)
        
        self.problema = QTextEdit()
        self.problema.setPlaceholderText("Describa el problema reportado por el cliente")
        self.problema.setMinimumHeight(100)
        
        self.diagnostico = QTextEdit()
        self.diagnostico.setPlaceholderText("Escriba el diagnóstico técnico del problema")
        self.diagnostico.setMinimumHeight(100)
        
        # Campos para costos
        self.costo_repuestos = QDoubleSpinBox()
        self.costo_repuestos.setRange(0, 999999.99)
        self.costo_repuestos.setDecimals(2)
        self.costo_repuestos.setPrefix("$ ")
        
        self.costo_mano_obra = QDoubleSpinBox()
        self.costo_mano_obra.setRange(0, 999999.99)
        self.costo_mano_obra.setDecimals(2)
        self.costo_mano_obra.setPrefix("$ ")
        
        self.total = QDoubleSpinBox()
        self.total.setRange(0, 999999.99)
        self.total.setDecimals(2)
        self.total.setReadOnly(True)
        self.total.setPrefix("$ ")
        self.total.setStyleSheet("background-color: #f0f0f0; font-weight: bold;")
        
        # Conectar eventos para calcular total
        self.costo_repuestos.valueChanged.connect(self.calcularTotal)
        self.costo_mano_obra.valueChanged.connect(self.calcularTotal)
        
        # Notas adicionales
        self.notas = QTextEdit()
        self.notas.setPlaceholderText("Notas adicionales sobre la reparación")
        self.notas.setMinimumHeight(80)
        
        # Agregar campos al formulario
        form_layout.addRow("Seleccionar Camión:", self.combo_camion)
        form_layout.addRow("Mecánico Responsable:", self.combo_mecanico)
        form_layout.addRow("Fecha de Ingreso:", self.fecha_ingreso)
        form_layout.addRow("Fecha Estimada de Entrega:", self.fecha_entrega_estimada)
        form_layout.addRow("Estado:", self.estado)
        form_layout.addRow("Problema Reportado:", self.problema)
        form_layout.addRow("Diagnóstico:", self.diagnostico)
        form_layout.addRow("Costo de Repuestos:", self.costo_repuestos)
        form_layout.addRow("Costo de Mano de Obra:", self.costo_mano_obra)
        form_layout.addRow("Total:", self.total)
        form_layout.addRow("Notas Adicionales:", self.notas)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 16px;")
        self.btn_guardar.clicked.connect(self.guardar)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px 16px;")
        self.btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_guardar)
        button_layout.addWidget(self.btn_cancelar)
        
        # Armar layout final
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Calcular total inicial
        self.calcularTotal()
        
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
        if self.combo_camion.currentIndex() < 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un camión")
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
            print(f"Guardando datos de reparación: {datos}")
            
            if self.reparacion is None:
                # Nueva reparación - asegurarnos de no enviar un ID
                if 'id' in datos:
                    del datos['id']
                
                # También actualizar el estado del camión a "En Reparación"
                self.actualizarEstadoCamion(datos['camion_id'], "En Reparación")
                
                id_reparacion = self.controller.agregar_reparacion(datos)
                print(f"Nueva reparación creada con ID: {id_reparacion}")
                QMessageBox.information(self, "Éxito", f"Reparación #{id_reparacion} registrada correctamente")
            else:
                # Actualizar reparación existente
                if 'id' in self.reparacion and self.reparacion['id'] is not None:
                    id_reparacion = self.reparacion['id']
                    
                    # Si el estado cambia a "Reparado", actualizar el estado del camión
                    if datos['estado'] == "Reparado" and self.reparacion.get('estado') != "Reparado":
                        self.actualizarEstadoCamion(datos['camion_id'], "Operativo")
                    
                    self.controller.actualizar_reparacion(id_reparacion, datos)
                    print(f"Reparación #{id_reparacion} actualizada correctamente")
                    QMessageBox.information(self, "Éxito", f"Reparación #{id_reparacion} actualizada correctamente")
                else:
                    # Si no hay ID, tratar como nueva reparación
                    if 'id' in datos:
                        del datos['id']
                    
                    # También actualizar el estado del camión a "En Reparación"
                    self.actualizarEstadoCamion(datos['camion_id'], "En Reparación")
                    
                    id_reparacion = self.controller.agregar_reparacion(datos)
                    print(f"Nueva reparación creada con ID: {id_reparacion}")
                    QMessageBox.information(self, "Éxito", f"Reparación #{id_reparacion} registrada como nueva")
            
            self.accept()
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error detallado al guardar reparación: {error_detallado}")
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
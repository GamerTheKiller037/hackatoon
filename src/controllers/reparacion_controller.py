import os
import json
import datetime
import csv
from bson import ObjectId

class ReparacionController:
    """Controlador para manejar las reparaciones"""
    
    def __init__(self, archivo_db=None):
        """
        Inicializa el controlador
        
        Args:
            archivo_db (str, optional): Ruta al archivo de base de datos. 
                                       Por defecto se usa 'data/reparaciones.json'
        """
        # Definir la ruta al archivo de base de datos
        if archivo_db is None:
            # Usar ruta por defecto
            self.archivo_db = os.path.join('data', 'reparaciones.json')
        else:
            self.archivo_db = archivo_db
            
        # Cargar datos existentes
        self.reparaciones = []
        self.ultimo_id = 0
        
        self.cargar_datos()
        
    def cargar_datos(self):
        """Carga los datos del archivo JSON"""
        try:
            # Verificar si el directorio existe, si no, crearlo
            directorio = os.path.dirname(self.archivo_db)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)
                
            # Verificar si el archivo existe
            if os.path.exists(self.archivo_db):
                with open(self.archivo_db, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reparaciones = data.get('reparaciones', [])
                    self.ultimo_id = data.get('ultimo_id', 0)
            else:
                # Archivo no existe, inicializar con datos vacíos
                self.reparaciones = []
                self.ultimo_id = 0
                # Guardar para crear el archivo
                self.guardar_datos()
                print(f"Archivo {self.archivo_db} no encontrado. Se ha creado uno nuevo.")
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            # Inicializar con datos vacíos en caso de error
            self.reparaciones = []
            self.ultimo_id = 0
            
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        try:
            # Convertir ObjectId a string antes de serializar a JSON
            reparaciones_serializables = []
            for reparacion in self.reparaciones:
                reparacion_serializable = {}
                for key, value in reparacion.items():
                    # Convertir ObjectId a string si es necesario
                    if key == 'camion_id' or key == 'mecanico_id' or key == 'id':
                        if isinstance(value, ObjectId):
                            reparacion_serializable[key] = str(value)
                        else:
                            reparacion_serializable[key] = value
                    else:
                        reparacion_serializable[key] = value
                reparaciones_serializables.append(reparacion_serializable)
            
            # Preparar datos para guardar
            data = {
                'reparaciones': reparaciones_serializables,
                'ultimo_id': self.ultimo_id
            }
            
            # Guardar en el archivo
            directorio = os.path.dirname(self.archivo_db)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)
                
            with open(self.archivo_db, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
                
        except Exception as e:
            import traceback
            error_detallado = traceback.format_exc()
            print(f"Error al guardar datos: {str(e)}")
            print(f"Traza detallada: {error_detallado}")
            raise
            
    def agregar_reparacion(self, datos):
        """
        Agrega una nueva reparación
        
        Args:
            datos: Diccionario con los datos de la reparación
            
        Returns:
            ID de la nueva reparación
        """
        # Generar nuevo ID
        self.ultimo_id += 1
        
        # Crear nueva reparación con el ID asignado
        nueva_reparacion = datos.copy()
        nueva_reparacion['id'] = self.ultimo_id
        
        # Agregar timestamp de creación
        nueva_reparacion['fecha_creacion'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Agregar a la lista
        self.reparaciones.append(nueva_reparacion)
        
        # Guardar cambios
        self.guardar_datos()
        
        print(f"Nueva reparación agregada con ID: {self.ultimo_id}")
        
        return self.ultimo_id
        
    def actualizar_reparacion(self, id_reparacion, datos):
        """
        Actualiza una reparación existente
        
        Args:
            id_reparacion: ID de la reparación a actualizar
            datos: Nuevos datos de la reparación
            
        Returns:
            bool: True si se actualizó correctamente, False si no se encontró
        """
        # Buscar la reparación por ID
        for i, reparacion in enumerate(self.reparaciones):
            if reparacion['id'] == id_reparacion:
                # Actualizar datos manteniendo el ID y la fecha de creación
                datos_actualizados = datos.copy()
                datos_actualizados['id'] = id_reparacion
                if 'fecha_creacion' in reparacion:
                    datos_actualizados['fecha_creacion'] = reparacion['fecha_creacion']
                
                # Agregar timestamp de actualización
                datos_actualizados['fecha_actualizacion'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Reemplazar la reparación en la lista
                self.reparaciones[i] = datos_actualizados
                
                # Guardar cambios
                self.guardar_datos()
                
                
                return True
                
        # No se encontró la reparación
        print(f"No se encontró la reparación con ID {id_reparacion} para actualizar")
        return False
        
    def eliminar_reparacion(self, id_reparacion):
        """
        Elimina una reparación
        
        Args:
            id_reparacion: ID de la reparación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no se encontró
        """
        # Buscar la reparación por ID
        for i, reparacion in enumerate(self.reparaciones):
            if reparacion['id'] == id_reparacion:
                # Eliminar de la lista
                del self.reparaciones[i]
                
                # Guardar cambios
                self.guardar_datos()
                
                
                return True
                
        # No se encontró la reparación
        print(f"No se encontró la reparación con ID {id_reparacion} para eliminar")
        return False
        
    def obtener_reparacion(self, id_reparacion):
        """
        Obtiene una reparación por su ID
        
        Args:
            id_reparacion: ID de la reparación
            
        Returns:
            dict: Datos de la reparación o None si no se encontró
        """
        # Buscar la reparación por ID
        for reparacion in self.reparaciones:
            if reparacion['id'] == id_reparacion:
                return reparacion
                
        # No se encontró la reparación
        print(f"No se encontró la reparación con ID {id_reparacion}")
        return None
        
    def obtener_todas_reparaciones(self):
        """
        Obtiene todas las reparaciones
        
        Returns:
            list: Lista de todas las reparaciones
        """
        return self.reparaciones
        
    def obtener_reparaciones_por_camion(self, camion_id):
        """
        Obtiene las reparaciones de un camión específico
        
        Args:
            camion_id: ID del camión
            
        Returns:
            list: Lista de reparaciones del camión
        """
        reparaciones_camion = [r for r in self.reparaciones if str(r.get('camion_id')) == str(camion_id)]
        print(f"Obteniendo reparaciones del camión {camion_id}: {len(reparaciones_camion)} encontradas")
        return reparaciones_camion
        
    def obtener_reparaciones_por_estado(self, estado):
        """
        Obtiene las reparaciones por estado
        
        Args:
            estado: Estado de la reparación (ej: "Pendiente", "En Reparación", etc.)
            
        Returns:
            list: Lista de reparaciones en ese estado
        """
        reparaciones_estado = [r for r in self.reparaciones if r.get('estado') == estado]
        print(f"Obteniendo reparaciones con estado {estado}: {len(reparaciones_estado)} encontradas")
        return reparaciones_estado
        
    def obtener_reparaciones_por_mecanico(self, mecanico_id):
        """
        Obtiene las reparaciones asignadas a un mecánico específico
        
        Args:
            mecanico_id: ID del mecánico
            
        Returns:
            list: Lista de reparaciones asignadas al mecánico
        """
        reparaciones_mecanico = [r for r in self.reparaciones if str(r.get('mecanico_id')) == str(mecanico_id)]
        print(f"Obteniendo reparaciones del mecánico {mecanico_id}: {len(reparaciones_mecanico)} encontradas")
        return reparaciones_mecanico
        
    def exportar_a_csv(self, ruta_archivo):
        """
        Exporta las reparaciones a un archivo CSV
        
        Args:
            ruta_archivo: Ruta del archivo CSV a generar
            
        Returns:
            bool: True si se exportó correctamente, False en caso contrario
        """
        try:
            # Definir campos a exportar
            campos = [
                'id', 'matricula', 'modelo', 'anio', 'estado', 'problema', 
                'diagnostico', 'costo_repuestos', 'costo_mano_obra', 'total',
                'fecha_ingreso', 'fecha_entrega_estimada', 'fecha_creacion'
            ]
            
            # Escribir el archivo CSV
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                
                # Escribir solo los campos seleccionados para cada reparación
                for reparacion in self.reparaciones:
                    fila = {campo: reparacion.get(campo, '') for campo in campos}
                    writer.writerow(fila)
            
            print(f"Datos exportados a CSV en {ruta_archivo}")
            return True
        except Exception as e:
            print(f"Error al exportar a CSV: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
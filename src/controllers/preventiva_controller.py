import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json

class PreventivaController:
    """Controlador para gestionar operaciones con tareas de mantenimiento preventivo"""
    
    def __init__(self):
        """Inicializa el controlador de preventivas conectando a la base de datos"""
        try:
            # Obtener configuración de la base de datos
            self.config = self._cargar_configuracion()
            
            # Conectar a MongoDB
            self.client = MongoClient(self.config.get('mongodb_uri', 'mongodb://localhost:27017'))
            self.db = self.client[self.config.get('mongodb_db', 'gestion_camiones')]
            self.collection = self.db['preventivas']
            
        except Exception as e:
            logging.error(f"Error al conectar a la base de datos: {str(e)}")
            raise
    
    def _cargar_configuracion(self):
        """Carga la configuración de la aplicación"""
        try:
            # Ruta al archivo de configuración
            config_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'GestionCamiones')
            config_file = os.path.join(config_dir, 'config.json')
            
            # Verificar si existe el archivo y cargarlo
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                # Configuración por defecto
                return {
                    'mongodb_uri': 'mongodb://localhost:27017',
                    'mongodb_db': 'gestion_camiones'
                }
        except Exception as e:
            logging.error(f"Error al cargar configuración: {str(e)}")
            # Configuración por defecto en caso de error
            return {
                'mongodb_uri': 'mongodb://localhost:27017',
                'mongodb_db': 'gestion_camiones'
            }
    
    def obtener_todas_preventivas(self, filtros=None):
        """
        Obtiene las tareas preventivas según los filtros especificados
        
        Args:
            filtros: Diccionario con los criterios de filtrado
        
        Returns:
            Lista de tareas preventivas que coinciden con los filtros
        """
        try:
            query = {}
            
            # Aplicar filtros si existen
            if filtros:
                # Filtro por matrícula
                if 'matricula' in filtros and filtros['matricula']:
                    query['matricula'] = {'$regex': filtros['matricula'], '$options': 'i'}
                
                # Filtro por modelo
                if 'modelo' in filtros and filtros['modelo']:
                    query['modelo'] = {'$regex': filtros['modelo'], '$options': 'i'}
                
                # Filtro por tipo
                if 'tipo' in filtros and filtros['tipo']:
                    query['tipo'] = filtros['tipo']
                    
                # Filtro por estado
                if 'estado' in filtros and filtros['estado']:
                    query['estado'] = filtros['estado']
                    
                # Filtro por nivel de urgencia
                if 'nivel_urgencia' in filtros and filtros['nivel_urgencia']:
                    query['nivel_urgencia'] = filtros['nivel_urgencia']
            
            # Ejecutar consulta
            preventivas = list(self.collection.find(query))
            
            # Convertir ObjectId a string para cada preventiva
            for preventiva in preventivas:
                preventiva['_id'] = str(preventiva['_id'])
            
            return preventivas
        except Exception as e:
            logging.error(f"Error al obtener preventivas: {str(e)}")
            return []
    
    def obtener_preventiva_por_id(self, id_preventiva):
        """
        Obtiene una tarea preventiva por su ID
        
        Args:
            id_preventiva: ID de la tarea preventiva a buscar
        
        Returns:
            Diccionario con los datos de la tarea preventiva o None si no se encuentra
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id_preventiva, str):
                id_preventiva = ObjectId(id_preventiva)
            
            preventiva = self.collection.find_one({'_id': id_preventiva})
            
            if preventiva:
                # Convertir ObjectId a string
                preventiva['_id'] = str(preventiva['_id'])
                return preventiva
            
            return None
        except Exception as e:
            logging.error(f"Error al obtener preventiva por ID: {str(e)}")
            return None
    
    def obtener_preventivas_por_matricula(self, matricula):
        """
        Obtiene todas las tareas preventivas por matrícula del camión
        
        Args:
            matricula: Matrícula del camión a buscar
        
        Returns:
            Lista de tareas preventivas del camión
        """
        try:
            preventivas = list(self.collection.find({'matricula': matricula}))
            
            # Convertir ObjectId a string para cada preventiva
            for preventiva in preventivas:
                preventiva['_id'] = str(preventiva['_id'])
            
            return preventivas
        except Exception as e:
            logging.error(f"Error al obtener preventivas por matrícula: {str(e)}")
            return []
    
    def agregar_preventiva(self, datos_preventiva):
        """
        Agrega una nueva tarea preventiva
        
        Args:
            datos_preventiva: Diccionario con los datos de la tarea preventiva
        
        Returns:
            ID de la nueva tarea preventiva o None si hay error
        """
        try:
            # Validar datos
            self._validar_datos_preventiva(datos_preventiva)
            
            # Agregar fecha de creación
            datos_preventiva['fecha_registro'] = datetime.datetime.now()
            
            # Insertar en la base de datos
            resultado = self.collection.insert_one(datos_preventiva)
            
            if resultado.inserted_id:
                return str(resultado.inserted_id)
            
            return None
        except Exception as e:
            logging.error(f"Error al agregar preventiva: {str(e)}")
            raise
    
    def actualizar_preventiva(self, id_preventiva, datos_preventiva):
        """
        Actualiza una tarea preventiva existente
        
        Args:
            id_preventiva: ID de la tarea preventiva a actualizar
            datos_preventiva: Diccionario con los nuevos datos
        
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Validar datos
            self._validar_datos_preventiva(datos_preventiva, es_actualizacion=True)
            
            # Convertir string a ObjectId si es necesario
            if isinstance(id_preventiva, str):
                id_preventiva = ObjectId(id_preventiva)
            
            # Agregar fecha de actualización
            datos_preventiva['ultima_actualizacion_reparacion'] = datetime.datetime.now()
            
            # Actualizar en la base de datos
            resultado = self.collection.update_one(
                {'_id': id_preventiva},
                {'$set': datos_preventiva}
            )
            
            return resultado.modified_count > 0
        except Exception as e:
            logging.error(f"Error al actualizar preventiva: {str(e)}")
            raise
    
    def eliminar_preventiva(self, id_preventiva):
        """
        Elimina una tarea preventiva
        
        Args:
            id_preventiva: ID de la tarea preventiva a eliminar
        
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id_preventiva, str):
                id_preventiva = ObjectId(id_preventiva)
            
            # Eliminar de la base de datos
            resultado = self.collection.delete_one({'_id': id_preventiva})
            
            return resultado.deleted_count > 0
        except Exception as e:
            logging.error(f"Error al eliminar preventiva: {str(e)}")
            raise
    
    def _validar_datos_preventiva(self, datos, es_actualizacion=False):
        """
        Valida los datos de una tarea preventiva
        
        Args:
            datos: Diccionario con los datos de la tarea preventiva
            es_actualizacion: Indica si es una actualización o un nuevo registro
        
        Raises:
            ValueError: Si los datos no son válidos
        """
        # Validar campos obligatorios
        if not es_actualizacion:
            campos_obligatorios = ['matricula', 'modelo', 'tipo', 'estado', 'nivel_urgencia']
            for campo in campos_obligatorios:
                if campo not in datos or not datos[campo]:
                    raise ValueError(f"El campo '{campo}' es obligatorio")
        
        # Validar estado
        if 'estado' in datos and datos['estado']:
            from models.preventiva import Preventiva
            if datos['estado'] not in Preventiva.ESTADOS_VALIDOS:
                raise ValueError(f"El estado '{datos['estado']}' no es válido")
        
        # Validar nivel de urgencia
        if 'nivel_urgencia' in datos and datos['nivel_urgencia']:
            from models.preventiva import Preventiva
            if datos['nivel_urgencia'] not in Preventiva.NIVELES_URGENCIA:
                raise ValueError(f"El nivel de urgencia '{datos['nivel_urgencia']}' no es válido")
        
        # Validar tipo
        if 'tipo' in datos and datos['tipo']:
            from models.preventiva import Preventiva
            if datos['tipo'] not in Preventiva.TIPOS_VALIDOS:
                raise ValueError(f"El tipo '{datos['tipo']}' no es válido")
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas sobre las tareas preventivas
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Total de preventivas
            total_preventivas = self.collection.count_documents({})
            
            # Preventivas por estado
            preventivas_por_estado = {}
            
            from models.preventiva import Preventiva
            for estado in Preventiva.ESTADOS_VALIDOS:
                preventivas_por_estado[estado] = self.collection.count_documents({'estado': estado})
            
            # Preventivas por nivel de urgencia
            preventivas_por_urgencia = {}
            
            for nivel in Preventiva.NIVELES_URGENCIA:
                preventivas_por_urgencia[nivel] = self.collection.count_documents({'nivel_urgencia': nivel})
            
            # Preventivas por tipo
            preventivas_por_tipo = {}
            
            for tipo in Preventiva.TIPOS_VALIDOS:
                preventivas_por_tipo[tipo] = self.collection.count_documents({'tipo': tipo})
            
            return {
                'total_preventivas': total_preventivas,
                'por_estado': preventivas_por_estado,
                'por_urgencia': preventivas_por_urgencia,
                'por_tipo': preventivas_por_tipo
            }
        except Exception as e:
            logging.error(f"Error al obtener estadísticas de preventivas: {str(e)}")
            return {
                'total_preventivas': 0,
                'por_estado': {},
                'por_urgencia': {},
                'por_tipo': {}
            }
    
    def exportar_a_csv(self, ruta_archivo):
        """
        Exporta todas las preventivas a un archivo CSV.
        
        Args:
            ruta_archivo (str): Ruta del archivo donde se guardará el CSV.
        
        Returns:
            bool: True si se exportó correctamente, False en caso contrario.
        """
        try:
            import csv
            preventivas = self.obtener_todas_preventivas()
            
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                
                # Escribir encabezados
                writer.writerow([
                    'ID', 'Matrícula', 'Modelo', 'Tipo', 'Estado', 
                    'Nivel de Urgencia', 'Fecha de Registro', 
                    'Última Actualización de Reparación'
                ])
                
                # Escribir datos
                for preventiva in preventivas:
                    writer.writerow([
                        preventiva.get('_id', ''),
                        preventiva.get('matricula', ''),
                        preventiva.get('modelo', ''),
                        preventiva.get('tipo', ''),
                        preventiva.get('estado', ''),
                        preventiva.get('nivel_urgencia', ''),
                        preventiva.get('fecha_registro', ''),
                        preventiva.get('ultima_actualizacion_reparacion', '')
                    ])
            
            return True
        except Exception as e:
            logging.error(f"Error al exportar preventivas a CSV: {str(e)}")
            return False
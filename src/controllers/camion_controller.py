import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json

class CamionController:
    """Controlador para gestionar operaciones con camiones"""
    
    def __init__(self):
        """Inicializa el controlador de camiones conectando a la base de datos"""
        try:
            # Obtener configuración de la base de datos
            self.config = self._cargar_configuracion()
            
            # Conectar a MongoDB
            self.client = MongoClient(self.config.get('mongodb_uri', 'mongodb://localhost:27017'))
            self.db = self.client[self.config.get('mongodb_db', 'gestion_camiones')]
            self.collection = self.db['camiones']
            
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
    
    def obtener_camiones(self, filtros=None):
        """
        Obtiene los camiones según los filtros especificados
        
        Args:
            filtros: Diccionario con los criterios de filtrado
        
        Returns:
            Lista de camiones que coinciden con los filtros
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
                
                # Filtro por año
                if 'anio' in filtros and filtros['anio']:
                    query['anio'] = int(filtros['anio'])
            
            # Ejecutar consulta
            camiones = list(self.collection.find(query))
            
            # Convertir ObjectId a string para cada camión
            for camion in camiones:
                camion['_id'] = str(camion['_id'])
            
            return camiones
        except Exception as e:
            logging.error(f"Error al obtener camiones: {str(e)}")
            return []
    
    def obtener_camion_por_id(self, id_camion):
        """
        Obtiene un camión por su ID
        
        Args:
            id_camion: ID del camión a buscar
        
        Returns:
            Diccionario con los datos del camión o None si no se encuentra
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id_camion, str):
                id_camion = ObjectId(id_camion)
            
            camion = self.collection.find_one({'_id': id_camion})
            
            if camion:
                # Convertir ObjectId a string
                camion['_id'] = str(camion['_id'])
                return camion
            
            return None
        except Exception as e:
            logging.error(f"Error al obtener camión por ID: {str(e)}")
            return None
    
    def obtener_camion_por_matricula(self, matricula):
        """
        Obtiene un camión por su matrícula
        
        Args:
            matricula: Matrícula del camión a buscar
        
        Returns:
            Diccionario con los datos del camión o None si no se encuentra
        """
        try:
            camion = self.collection.find_one({'matricula': matricula})
            
            if camion:
                # Convertir ObjectId a string
                camion['_id'] = str(camion['_id'])
                return camion
            
            return None
        except Exception as e:
            logging.error(f"Error al obtener camión por matrícula: {str(e)}")
            return None
    
    def agregar_camion(self, datos_camion):
        """
        Agrega un nuevo camión
        
        Args:
            datos_camion: Diccionario con los datos del camión
        
        Returns:
            ID del nuevo camión o None si hay error
        """
        try:
            # Validar datos
            self._validar_datos_camion(datos_camion)
            
            # Agregar fecha de creación
            datos_camion['fecha_creacion'] = datetime.datetime.now()
            
            # Insertar en la base de datos
            resultado = self.collection.insert_one(datos_camion)
            
            if resultado.inserted_id:
                return str(resultado.inserted_id)
            
            return None
        except Exception as e:
            logging.error(f"Error al agregar camión: {str(e)}")
            raise
    
    def actualizar_camion(self, id_camion, datos_camion):
        """
        Actualiza un camión existente
        
        Args:
            id_camion: ID del camión a actualizar
            datos_camion: Diccionario con los nuevos datos
        
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Validar datos
            self._validar_datos_camion(datos_camion, es_actualizacion=True)
            
            # Convertir string a ObjectId si es necesario
            if isinstance(id_camion, str):
                id_camion = ObjectId(id_camion)
            
            # Agregar fecha de actualización
            datos_camion['fecha_actualizacion'] = datetime.datetime.now()
            
            # Actualizar en la base de datos
            resultado = self.collection.update_one(
                {'_id': id_camion},
                {'$set': datos_camion}
            )
            
            return resultado.modified_count > 0
        except Exception as e:
            logging.error(f"Error al actualizar camión: {str(e)}")
            raise
    
    def eliminar_camion(self, id_camion):
        """
        Elimina un camión
        
        Args:
            id_camion: ID del camión a eliminar
        
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id_camion, str):
                id_camion = ObjectId(id_camion)
            
            # Eliminar de la base de datos
            resultado = self.collection.delete_one({'_id': id_camion})
            
            return resultado.deleted_count > 0
        except Exception as e:
            logging.error(f"Error al eliminar camión: {str(e)}")
            raise
    
    def _validar_datos_camion(self, datos, es_actualizacion=False):
        """
        Valida los datos de un camión
        
        Args:
            datos: Diccionario con los datos del camión
            es_actualizacion: Indica si es una actualización o un nuevo registro
        
        Raises:
            ValueError: Si los datos no son válidos
        """
        # Validar campos obligatorios
        if not es_actualizacion:
            campos_obligatorios = ['matricula', 'modelo', 'anio']
            for campo in campos_obligatorios:
                if campo not in datos or not datos[campo]:
                    raise ValueError(f"El campo '{campo}' es obligatorio")
        
        # Validar matrícula
        if 'matricula' in datos and datos['matricula']:
            # Verificar si ya existe otro camión con la misma matrícula
            camion_existente = self.collection.find_one({
                'matricula': datos['matricula'],
                '_id': {'$ne': ObjectId(datos.get('_id')) if '_id' in datos else None}
            })
            
            if camion_existente:
                raise ValueError(f"Ya existe un camión con la matrícula {datos['matricula']}")
        
        # Validar año
        if 'anio' in datos and datos['anio']:
            try:
                anio = int(datos['anio'])
                if anio < 1900 or anio > datetime.datetime.now().year + 1:
                    raise ValueError(f"El año debe estar entre 1900 y {datetime.datetime.now().year + 1}")
            except ValueError:
                raise ValueError("El año debe ser un número entero")
        
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas sobre los camiones
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Total de camiones
            total_camiones = self.collection.count_documents({})
            
            # Camiones por marca/modelo (agrupados)
            pipeline_modelos = [
                {'$group': {'_id': '$modelo', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 5}
            ]
            modelos_populares = list(self.collection.aggregate(pipeline_modelos))
            
            # Edad promedio de los camiones
            anio_actual = datetime.datetime.now().year
            pipeline_edad = [
                {'$project': {'edad': {'$subtract': [anio_actual, '$anio']}}},
                {'$group': {'_id': None, 'promedio': {'$avg': '$edad'}}}
            ]
            resultado_edad = list(self.collection.aggregate(pipeline_edad))
            edad_promedio = resultado_edad[0]['promedio'] if resultado_edad else 0
            
            
            return {
                'total_camiones': total_camiones,
                'modelos_populares': [{'modelo': item['_id'], 'cantidad': item['count']} for item in modelos_populares],
                'edad_promedio': round(edad_promedio, 1)
            }
        except Exception as e:
            logging.error(f"Error al obtener estadísticas de camiones: {str(e)}")
            return {
                'total_camiones': 0,
                'modelos_populares': [],
                'edad_promedio': 0
            }
    
    def obtener_modelos_populares(self, limite=5):
        """
        Obtiene los modelos de camiones más populares
        
        Args:
            limite: Número máximo de resultados a devolver
        
        Returns:
            Lista de tuplas (modelo, cantidad)
        """
        try:
            # Agregar por modelo y contar
            pipeline = [
                {'$group': {'_id': '$modelo', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': limite}
            ]
            
            resultado = list(self.collection.aggregate(pipeline))
            
            # Convertir a lista de tuplas
            return [(item['_id'], item['count']) for item in resultado]
        except Exception as e:
            logging.error(f"Error al obtener modelos populares: {str(e)}")
            return []
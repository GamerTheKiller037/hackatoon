import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json

class MecanicoController:
    """Controlador para gestionar operaciones con mecánicos"""
    
    def __init__(self):
        """Inicializa el controlador de mecánicos conectando a la base de datos"""
        try:
            # Obtener configuración de la base de datos
            self.config = self._cargar_configuracion()
            
            # Conectar a MongoDB
            self.client = MongoClient(self.config.get('mongodb_uri', 'mongodb://localhost:27017'))
            self.db = self.client[self.config.get('mongodb_db', 'gestion_camiones')]
            self.collection = self.db['mecanicos']
            
            logging.info(f"Conexión establecida a MongoDB: {self.config.get('mongodb_uri')}")
            logging.info(f"Base de datos: {self.config.get('mongodb_db')}")
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
    
    def obtener_mecanicos(self, filtros=None):
        """
        Obtiene los mecánicos según los filtros especificados
        
        Args:
            filtros: Diccionario con los criterios de filtrado
        
        Returns:
            Lista de mecánicos que coinciden con los filtros
        """
        try:
            query = {}
            
            # Aplicar filtros si existen
            if filtros:
                # Filtro por nombre
                if 'nombre' in filtros and filtros['nombre']:
                    query['$or'] = [
                        {'nombre': {'$regex': filtros['nombre'], '$options': 'i'}},
                        {'apellidos': {'$regex': filtros['nombre'], '$options': 'i'}}
                    ]
                
                # Filtro por actividad
                if 'actividad' in filtros and filtros['actividad']:
                    query['actividad'] = filtros['actividad']
            
            # Ejecutar consulta
            mecanicos = list(self.collection.find(query))
            
            # Convertir ObjectId a string para cada mecánico
            for mecanico in mecanicos:
                mecanico['_id'] = str(mecanico['_id'])
            
            return mecanicos
        except Exception as e:
            logging.error(f"Error al obtener mecánicos: {str(e)}")
            return []
    
    def obtener_mecanico_por_id(self, id_mecanico):
        """
        Obtiene un mecánico por su ID
        
        Args:
            id_mecanico: ID del mecánico a buscar
        
        Returns:
            Diccionario con los datos del mecánico o None si no se encuentra
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id_mecanico, str):
                id_mecanico = ObjectId(id_mecanico)
            
            mecanico = self.collection.find_one({'_id': id_mecanico})
            
            if mecanico:
                # Convertir ObjectId a string
                mecanico['_id'] = str(mecanico['_id'])
                return mecanico
            
            return None
        except Exception as e:
            logging.error(f"Error al obtener mecánico por ID: {str(e)}")
            return None
    
    def obtener_mecanico_por_nombre_completo(self, nombre, apellidos):
        """
        Obtiene un mecánico por su nombre y apellidos
        
        Args:
            nombre: Nombre del mecánico
            apellidos: Apellidos del mecánico
        
        Returns:
            Diccionario con los datos del mecánico o None si no se encuentra
        """
        try:
            mecanico = self.collection.find_one({
                'nombre': nombre,
                'apellidos': apellidos
            })
            
            if mecanico:
                # Convertir ObjectId a string
                mecanico['_id'] = str(mecanico['_id'])
                return mecanico
            
            return None
        except Exception as e:
            logging.error(f"Error al obtener mecánico por nombre: {str(e)}")
            return None
    
    def agregar_mecanico(self, datos_mecanico):
        """
        Agrega un nuevo mecánico
        
        Args:
            datos_mecanico: Diccionario con los datos del mecánico
        
        Returns:
            ID del nuevo mecánico o None si hay error
        """
        try:
            # Validar datos
            self._validar_datos_mecanico(datos_mecanico)
            
            # Agregar fecha de creación
            datos_mecanico['fecha_creacion'] = datetime.datetime.now()
            datos_mecanico['ultima_actualizacion'] = datetime.datetime.now()
            
            # Insertar en la base de datos
            resultado = self.collection.insert_one(datos_mecanico)
            
            if resultado.inserted_id:
                return str(resultado.inserted_id)
            
            return None
        except Exception as e:
            logging.error(f"Error al agregar mecánico: {str(e)}")
            raise
    
    def actualizar_mecanico(self, id_mecanico, datos_mecanico):
        """
        Actualiza un mecánico existente
        
        Args:
            id_mecanico: ID del mecánico a actualizar
            datos_mecanico: Diccionario con los nuevos datos
        
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Validar datos
            self._validar_datos_mecanico(datos_mecanico, es_actualizacion=True)
            
            # Convertir string a ObjectId si es necesario
            if isinstance(id_mecanico, str):
                id_mecanico = ObjectId(id_mecanico)
            
            # Agregar fecha de actualización
            datos_mecanico['fecha_actualizacion'] = datetime.datetime.now()
            
            # Actualizar en la base de datos
            resultado = self.collection.update_one(
                {'_id': id_mecanico},
                {'$set': datos_mecanico}
            )
            
            return resultado.modified_count > 0
        except Exception as e:
            logging.error(f"Error al actualizar mecánico: {str(e)}")
            raise
    
    def eliminar_mecanico(self, id_mecanico):
        """
        Elimina un mecánico
        
        Args:
            id_mecanico: ID del mecánico a eliminar
        
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id_mecanico, str):
                id_mecanico = ObjectId(id_mecanico)
            
            # Eliminar de la base de datos
            resultado = self.collection.delete_one({'_id': id_mecanico})
            
            return resultado.deleted_count > 0
        except Exception as e:
            logging.error(f"Error al eliminar mecánico: {str(e)}")
            raise
    
    def _validar_datos_mecanico(self, datos, es_actualizacion=False):
        """
        Valida los datos de un mecánico
        
        Args:
            datos: Diccionario con los datos del mecánico
            es_actualizacion: Indica si es una actualización o un nuevo registro
        
        Raises:
            ValueError: Si los datos no son válidos
        """
        # Validar campos obligatorios
        if not es_actualizacion:
            campos_obligatorios = ['nombre', 'apellidos', 'actividad']
            for campo in campos_obligatorios:
                if campo not in datos or not datos[campo]:
                    raise ValueError(f"El campo '{campo}' es obligatorio")
        
        # Validar que no exista un mecánico con el mismo nombre completo (solo en nuevos registros)
        if not es_actualizacion and 'nombre' in datos and 'apellidos' in datos:
            mecanico_existente = self.collection.find_one({
                'nombre': datos['nombre'],
                'apellidos': datos['apellidos'],
                '_id': {'$ne': ObjectId(datos.get('_id')) if '_id' in datos else None}
            })
            
            if mecanico_existente:
                raise ValueError(f"Ya existe un mecánico con el nombre {datos['nombre']} {datos['apellidos']}")
    
    def obtener_mecanicos_por_actividad(self, actividad):
        """
        Obtiene los mecánicos que tienen una actividad específica
        
        Args:
            actividad: Actividad a filtrar
        
        Returns:
            Lista de mecánicos con la actividad especificada
        """
        return self.obtener_mecanicos({'actividad': actividad})
    
    def obtener_mecanicos_disponibles(self):
        """
        Obtiene los mecánicos que están sin actividad
        
        Returns:
            Lista de mecánicos disponibles
        """
        from models.mecanico import Mecanico
        return self.obtener_mecanicos({'actividad': Mecanico.ACTIVIDAD_SIN_ACTIVIDAD})
    
    def asignar_actividad(self, id_mecanico, actividad):
        """
        Asigna una nueva actividad a un mecánico
        
        Args:
            id_mecanico: ID del mecánico
            actividad: Nueva actividad a asignar
        
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            from models.mecanico import Mecanico
            
            # Validar que la actividad sea válida
            if actividad not in Mecanico.ACTIVIDADES_VALIDAS:
                raise ValueError(f"La actividad '{actividad}' no es válida")
            
            # Actualizar la actividad
            return self.actualizar_mecanico(id_mecanico, {'actividad': actividad})
        except Exception as e:
            logging.error(f"Error al asignar actividad: {str(e)}")
            raise
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas sobre los mecánicos
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Total de mecánicos
            total_mecanicos = self.collection.count_documents({})
            
            # Mecánicos por actividad
            pipeline_actividades = [
                {'$group': {'_id': '$actividad', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            actividades = list(self.collection.aggregate(pipeline_actividades))
            
            # Mecánicos disponibles
            from models.mecanico import Mecanico
            disponibles = self.collection.count_documents({'actividad': Mecanico.ACTIVIDAD_SIN_ACTIVIDAD})
            
            return {
                'total_mecanicos': total_mecanicos,
                'actividades': [{'actividad': item['_id'], 'cantidad': item['count']} for item in actividades],
                'disponibles': disponibles,
                'ocupados': total_mecanicos - disponibles
            }
        except Exception as e:
            logging.error(f"Error al obtener estadísticas de mecánicos: {str(e)}")
            return {
                'total_mecanicos': 0,
                'actividades': [],
                'disponibles': 0,
                'ocupados': 0
            }
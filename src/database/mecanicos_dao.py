#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Objeto de Acceso a Datos (DAO) para mecánicos.
"""

import logging
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from database.connection import DatabaseConnection
from models.mecanico import Mecanico

class MecanicosDAO:
    """Clase para manejar operaciones de base de datos relacionadas con mecánicos"""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        try:
            self.db_connection = DatabaseConnection()
            self.collection = self.db_connection.get_mecanicos_collection()
        except Exception as e:
            logging.error(f"MecanicosDAO: Error al conectar a la base de datos: {str(e)}")
            raise
    
    def obtener_todos(self):
        """
        Obtiene todos los mecánicos de la base de datos.
        
        Returns:
            list: Lista de objetos Mecanico
        """
        try:
            mecanicos_docs = self.collection.find().sort('apellidos', 1)
            mecanicos = []
            
            for doc in mecanicos_docs:
                mecanicos.append(Mecanico.from_dict(doc))
            
            return mecanicos
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al obtener todos los mecánicos: {str(e)}")
            return []
    
    def obtener_por_id(self, id):
        """
        Obtiene un mecánico por su ID.
        
        Args:
            id: ID del mecánico a buscar
            
        Returns:
            Mecanico: Objeto Mecanico si se encuentra, None en caso contrario
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id, str):
                id = ObjectId(id)
            
            doc = self.collection.find_one({'_id': id})
            
            if doc:
                return Mecanico.from_dict(doc)
            
            return None
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al obtener mecánico por ID: {str(e)}")
            return None
    
    def obtener_por_nombre_completo(self, nombre, apellidos):
        """
        Obtiene un mecánico por su nombre y apellidos.
        
        Args:
            nombre: Nombre del mecánico
            apellidos: Apellidos del mecánico
            
        Returns:
            Mecanico: Objeto Mecanico si se encuentra, None en caso contrario
        """
        try:
            doc = self.collection.find_one({
                'nombre': nombre,
                'apellidos': apellidos
            })
            
            if doc:
                return Mecanico.from_dict(doc)
            
            return None
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al obtener mecánico por nombre: {str(e)}")
            return None
    
    def insertar(self, mecanico):
        """
        Inserta un nuevo mecánico en la base de datos.
        
        Args:
            mecanico: Objeto Mecanico a insertar
            
        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario
        """
        try:
            # Verificar si ya existe un mecánico con el mismo nombre completo
            if self.obtener_por_nombre_completo(mecanico.nombre, mecanico.apellidos):
                logging.warning(f"Ya existe un mecánico con nombre {mecanico.nombre} {mecanico.apellidos}")
                return False
                
            resultado = self.collection.insert_one(mecanico.to_dict())
            return resultado.acknowledged
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al insertar mecánico: {str(e)}")
            return False
    
    def actualizar(self, mecanico):
        """
        Actualiza un mecánico existente en la base de datos.
        
        Args:
            mecanico: Objeto Mecanico con los datos actualizados
            
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Actualizar la fecha de última actualización
            mecanico.ultima_actualizacion = datetime.now()
            
            # Convertir a diccionario
            mecanico_dict = mecanico.to_dict()
            
            resultado = self.collection.update_one(
                {'_id': mecanico.id},
                {'$set': mecanico_dict}
            )
            
            return resultado.modified_count > 0
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al actualizar mecánico: {str(e)}")
            return False
    
    def eliminar(self, id):
        """
        Elimina un mecánico de la base de datos.
        
        Args:
            id: ID del mecánico a eliminar
            
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id, str):
                id = ObjectId(id)
            
            resultado = self.collection.delete_one({'_id': id})
            return resultado.deleted_count > 0
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al eliminar mecánico: {str(e)}")
            return False
    
    def buscar(self, filtros=None):
        """
        Busca mecánicos según los filtros especificados.
        
        Args:
            filtros: Diccionario con criterios de búsqueda
            
        Returns:
            list: Lista de objetos Mecanico que coinciden con los filtros
        """
        try:
            # Inicializar consulta
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
            mecanicos_docs = self.collection.find(query).sort('apellidos', 1)
            mecanicos = []
            
            for doc in mecanicos_docs:
                mecanicos.append(Mecanico.from_dict(doc))
            
            return mecanicos
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al buscar mecánicos: {str(e)}")
            return []
    
    def obtener_por_actividad(self, actividad):
        """
        Obtiene todos los mecánicos con una actividad específica.
        
        Args:
            actividad: Actividad a buscar
            
        Returns:
            list: Lista de objetos Mecanico con la actividad especificada
        """
        try:
            return self.buscar({'actividad': actividad})
        except Exception as e:
            logging.error(f"MecanicosDAO: Error al obtener mecánicos por actividad: {str(e)}")
            return []
            
    def obtener_disponibles(self):
        """
        Obtiene todos los mecánicos sin actividad asignada.
        
        Returns:
            list: Lista de objetos Mecanico disponibles
        """
        try:
            return self.obtener_por_actividad(Mecanico.ACTIVIDAD_SIN_ACTIVIDAD)
        except Exception as e:
            logging.error(f"MecanicosDAO: Error al obtener mecánicos disponibles: {str(e)}")
            return []
            
    def cambiar_actividad(self, mecanico_id, nueva_actividad):
        """
        Cambia la actividad de un mecánico.
        
        Args:
            mecanico_id (str or ObjectId): ID del mecánico
            nueva_actividad (str): Nueva actividad
            
        Returns:
            bool: True si se cambió correctamente, False en caso contrario
        """
        try:
            if isinstance(mecanico_id, str):
                mecanico_id = ObjectId(mecanico_id)
                
            # Verificar que la actividad sea válida
            if nueva_actividad not in Mecanico.ACTIVIDADES_VALIDAS:
                logging.warning(f"Actividad no válida: {nueva_actividad}")
                return False
                
            resultado = self.collection.update_one(
                {'_id': mecanico_id},
                {'$set': {
                    'actividad': nueva_actividad,
                    'ultima_actualizacion': datetime.now()
                }}
            )
            return resultado.modified_count > 0
        except PyMongoError as e:
            logging.error(f"MecanicosDAO: Error al cambiar la actividad del mecánico {mecanico_id}: {str(e)}")
            return False
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Access Object (DAO) para operaciones CRUD con camiones.
"""

import logging
from bson import ObjectId
from pymongo.errors import PyMongoError
from database.connection import DatabaseConnection
from models.camion import Camion

class CamionesDAO:
    """Clase para operaciones CRUD con camiones en MongoDB"""
    
    def __init__(self):
        """Inicializa el DAO conectándose a la base de datos"""
        self.db_connection = DatabaseConnection()
        self.collection = self.db_connection.get_camiones_collection()
    
    def obtener_todos(self):
        """
        Obtiene todos los camiones de la base de datos.
        
        Returns:
            list: Lista de objetos Camion
        """
        try:
            camiones = self.collection.find()
            return [Camion.from_dict(c) for c in camiones]
        except PyMongoError as e:
            logging.error(f"Error al obtener los camiones: {str(e)}")
            return []
    
    def obtener_por_id(self, camion_id):
        """
        Obtiene un camión por su ID.
        
        Args:
            camion_id (str or ObjectId): ID del camión
            
        Returns:
            Camion: Objeto Camion si existe, None en caso contrario
        """
        try:
            if isinstance(camion_id, str):
                camion_id = ObjectId(camion_id)
                
            camion = self.collection.find_one({'_id': camion_id})
            if camion:
                return Camion.from_dict(camion)
            return None
        except PyMongoError as e:
            logging.error(f"Error al obtener el camión {camion_id}: {str(e)}")
            return None
    
    def obtener_por_matricula(self, matricula):
        """
        Obtiene un camión por su matrícula.
        
        Args:
            matricula (str): Matrícula del camión
            
        Returns:
            Camion: Objeto Camion si existe, None en caso contrario
        """
        try:
            camion = self.collection.find_one({'matricula': matricula})
            if camion:
                return Camion.from_dict(camion)
            return None
        except PyMongoError as e:
            logging.error(f"Error al obtener el camión con matrícula {matricula}: {str(e)}")
            return None
    
    def insertar(self, camion):
        """
        Inserta un nuevo camión en la base de datos.
        
        Args:
            camion (Camion): Objeto Camion a insertar
            
        Returns:
            bool: True si se insertó correctamente, False en caso contrario
        """
        try:
            # Verificar si ya existe un camión con la misma matrícula
            if self.obtener_por_matricula(camion.matricula):
                logging.warning(f"Ya existe un camión con matrícula {camion.matricula}")
                return False
            
            # Insertar el camión
            result = self.collection.insert_one(camion.to_dict())
            return result.acknowledged
        except PyMongoError as e:
            logging.error(f"Error al insertar el camión: {str(e)}")
            return False
    
    def actualizar(self, camion):
        """
        Actualiza un camión existente en la base de datos.
        
        Args:
            camion (Camion): Objeto Camion con los datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            result = self.collection.update_one(
                {'_id': camion.id},
                {'$set': camion.to_dict()}
            )
            return result.matched_count > 0
        except PyMongoError as e:
            logging.error(f"Error al actualizar el camión {camion.id}: {str(e)}")
            return False
    
    def eliminar(self, camion_id):
        """
        Elimina un camión de la base de datos.
        
        Args:
            camion_id (str or ObjectId): ID del camión a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if isinstance(camion_id, str):
                camion_id = ObjectId(camion_id)
                
            result = self.collection.delete_one({'_id': camion_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logging.error(f"Error al eliminar el camión {camion_id}: {str(e)}")
            return False
    
    def obtener_por_estado(self, estado):
        """
        Obtiene los camiones que tienen un estado específico.
        
        Args:
            estado (str): Estado del camión
            
        Returns:
            list: Lista de objetos Camion
        """
        try:
            camiones = self.collection.find({'estado': estado})
            return [Camion.from_dict(c) for c in camiones]
        except PyMongoError as e:
            logging.error(f"Error al obtener los camiones por estado {estado}: {str(e)}")
            return []
    
    def cambiar_estado(self, camion_id, nuevo_estado):
        """
        Cambia el estado de un camión.
        
        Args:
            camion_id (str or ObjectId): ID del camión
            nuevo_estado (str): Nuevo estado
            
        Returns:
            bool: True si se cambió correctamente, False en caso contrario
        """
        try:
            if isinstance(camion_id, str):
                camion_id = ObjectId(camion_id)
                
            # Verificar que el estado sea válido
            if nuevo_estado not in Camion.ESTADOS_VALIDOS:
                logging.warning(f"Estado no válido: {nuevo_estado}")
                return False
                
            result = self.collection.update_one(
                {'_id': camion_id},
                {'$set': {
                    'estado': nuevo_estado,
                    'ultima_actualizacion': Camion().ultima_actualizacion  # Actualizar fecha
                }}
            )
            return result.matched_count > 0
        except PyMongoError as e:
            logging.error(f"Error al cambiar el estado del camión {camion_id}: {str(e)}")
            return False
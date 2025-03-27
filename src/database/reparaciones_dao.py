#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Objeto de Acceso a Datos (DAO) para reparaciones.
"""

import logging
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from database.connection import DatabaseConnection
from models.reparacion import Reparacion

class ReparacionesDAO:
    """Clase para manejar operaciones de base de datos relacionadas con reparaciones"""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        try:
            self.db_connection = DatabaseConnection()
            self.collection = self.db_connection.get_reparaciones_collection()
            
            logging.info(f"ReparacionesDAO: Conexión establecida a la colección de reparaciones")
        except Exception as e:
            logging.error(f"ReparacionesDAO: Error al conectar a la base de datos: {str(e)}")
            raise
    
    def obtener_todas(self):
        """
        Obtiene todas las reparaciones de la base de datos.
        
        Returns:
            list: Lista de objetos Reparacion
        """
        try:
            reparaciones_docs = self.collection.find().sort('fecha_entrada', -1)
            reparaciones = []
            
            for doc in reparaciones_docs:
                reparaciones.append(Reparacion.from_dict(doc))
            
            return reparaciones
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al obtener todas las reparaciones: {str(e)}")
            return []
    
    def obtener_por_id(self, id):
        """
        Obtiene una reparación por su ID.
        
        Args:
            id: ID de la reparación a buscar
            
        Returns:
            Reparacion: Objeto Reparacion si se encuentra, None en caso contrario
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(id, str):
                id = ObjectId(id)
            
            doc = self.collection.find_one({'_id': id})
            
            if doc:
                return Reparacion.from_dict(doc)
            
            return None
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al obtener reparación por ID: {str(e)}")
            return None
    
    def obtener_por_camion(self, camion_id):
        """
        Obtiene todas las reparaciones de un camión.
        
        Args:
            camion_id: ID del camión
            
        Returns:
            list: Lista de objetos Reparacion
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(camion_id, str):
                camion_id = ObjectId(camion_id)
            
            reparaciones_docs = self.collection.find({'camion_id': camion_id}).sort('fecha_entrada', -1)
            reparaciones = []
            
            for doc in reparaciones_docs:
                reparaciones.append(Reparacion.from_dict(doc))
            
            return reparaciones
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al obtener reparaciones por camión: {str(e)}")
            return []
    
    def obtener_por_mecanico(self, mecanico_id):
        """
        Obtiene todas las reparaciones asignadas a un mecánico.
        
        Args:
            mecanico_id: ID del mecánico
            
        Returns:
            list: Lista de objetos Reparacion
        """
        try:
            # Convertir string a ObjectId si es necesario
            if isinstance(mecanico_id, str):
                mecanico_id = ObjectId(mecanico_id)
            
            reparaciones_docs = self.collection.find({'mecanico_id': mecanico_id}).sort('fecha_entrada', -1)
            reparaciones = []
            
            for doc in reparaciones_docs:
                reparaciones.append(Reparacion.from_dict(doc))
            
            return reparaciones
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al obtener reparaciones por mecánico: {str(e)}")
            return []
    
    def obtener_por_estado(self, estado):
        """
        Obtiene todas las reparaciones con un estado específico.
        
        Args:
            estado: Estado de las reparaciones a buscar
            
        Returns:
            list: Lista de objetos Reparacion
        """
        try:
            reparaciones_docs = self.collection.find({'estado': estado}).sort('fecha_entrada', -1)
            reparaciones = []
            
            for doc in reparaciones_docs:
                reparaciones.append(Reparacion.from_dict(doc))
            
            return reparaciones
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al obtener reparaciones por estado: {str(e)}")
            return []
    
    def insertar(self, reparacion):
        """
        Inserta una nueva reparación en la base de datos.
        
        Args:
            reparacion: Objeto Reparacion a insertar
            
        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario
        """
        try:
            # Asegurar que la reparación tenga fecha de entrada y última actualización
            if not hasattr(reparacion, 'fecha_entrada') or reparacion.fecha_entrada is None:
                reparacion.fecha_entrada = datetime.now()
            
            if not hasattr(reparacion, 'ultima_actualizacion') or reparacion.ultima_actualizacion is None:
                reparacion.ultima_actualizacion = datetime.now()
            
            resultado = self.collection.insert_one(reparacion.to_dict())
            return resultado.acknowledged
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al insertar reparación: {str(e)}")
            return False
    
    def actualizar(self, reparacion):
        """
        Actualiza una reparación existente en la base de datos.
        
        Args:
            reparacion: Objeto Reparacion con los datos actualizados
            
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        try:
            # Asegurar que se actualice la fecha de última actualización
            reparacion.ultima_actualizacion = datetime.now()
            
            # Convertir a diccionario
            reparacion_dict = reparacion.to_dict()
            
            resultado = self.collection.update_one(
                {'_id': reparacion.id},
                {'$set': reparacion_dict}
            )
            
            return resultado.modified_count > 0
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al actualizar reparación: {str(e)}")
            return False
    
    def eliminar(self, id):
        """
        Elimina una reparación de la base de datos.
        
        Args:
            id: ID de la reparación a eliminar
            
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
            logging.error(f"ReparacionesDAO: Error al eliminar reparación: {str(e)}")
            return False
    
    def cambiar_estado(self, reparacion_id, nuevo_estado, notas=None):
        """
        Cambia el estado de una reparación.
        
        Args:
            reparacion_id (str or ObjectId): ID de la reparación
            nuevo_estado (str): Nuevo estado
            notas (str, optional): Notas adicionales sobre el cambio de estado
            
        Returns:
            bool: True si se cambió correctamente, False en caso contrario
        """
        try:
            if isinstance(reparacion_id, str):
                reparacion_id = ObjectId(reparacion_id)
                
            # Obtener la reparación actual
            reparacion = self.obtener_por_id(reparacion_id)
            if not reparacion:
                logging.warning(f"No se encontró la reparación {reparacion_id}")
                return False
                
            # Verificar que el estado sea válido
            if nuevo_estado not in Reparacion.ESTADOS_VALIDOS:
                logging.warning(f"Estado no válido: {nuevo_estado}")
                return False
                
            # Actualizar estado según la lógica del modelo
            if nuevo_estado == Reparacion.ESTADO_REPARADO:
                resultado = reparacion.completar_reparacion(notas=notas)
            elif nuevo_estado == Reparacion.ESTADO_CANCELADO:
                resultado = reparacion.cancelar_reparacion(motivo=notas)
            else:
                # Para otros estados, usar actualizar directamente
                resultado = reparacion.actualizar(estado=nuevo_estado)
                
                # Añadir notas si se proporcionaron
                if notas and resultado:
                    fecha_nota = datetime.now().strftime('%d/%m/%Y %H:%M')
                    if reparacion.notas_adicionales:
                        reparacion.notas_adicionales += f"\n\nCambio a estado {nuevo_estado} ({fecha_nota}):\n{notas}"
                    else:
                        reparacion.notas_adicionales = f"Cambio a estado {nuevo_estado} ({fecha_nota}):\n{notas}"
            
            # Si se actualizó el estado, guardar en la base de datos
            if resultado:
                return self.actualizar(reparacion)
            
            return False
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al cambiar el estado de la reparación {reparacion_id}: {str(e)}")
            return False
    
    def asignar_mecanico(self, reparacion_id, mecanico_id):
        """
        Asigna un mecánico a una reparación.
        
        Args:
            reparacion_id (str or ObjectId): ID de la reparación
            mecanico_id (str or ObjectId): ID del mecánico
            
        Returns:
            bool: True si se asignó correctamente, False en caso contrario
        """
        try:
            if isinstance(reparacion_id, str):
                reparacion_id = ObjectId(reparacion_id)
                
            # Obtener la reparación actual
            reparacion = self.obtener_por_id(reparacion_id)
            if not reparacion:
                logging.warning(f"No se encontró la reparación {reparacion_id}")
                return False
            
            # Usar el método del modelo para asignar mecánico
            resultado = reparacion.asignar_mecanico(mecanico_id)
            
            # Si se asignó correctamente, actualizar en la base de datos
            if resultado:
                return self.actualizar(reparacion)
            
            return False
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al asignar mecánico a la reparación {reparacion_id}: {str(e)}")
            return False
    
    def completar_reparacion(self, reparacion_id, costo=None, notas=None):
        """
        Marca una reparación como completada.
        
        Args:
            reparacion_id (str or ObjectId): ID de la reparación
            costo (float, optional): Costo final de la reparación
            notas (str, optional): Notas sobre la reparación realizada
            
        Returns:
            bool: True si se completó correctamente, False en caso contrario
        """
        try:
            if isinstance(reparacion_id, str):
                reparacion_id = ObjectId(reparacion_id)
                
            # Obtener la reparación actual
            reparacion = self.obtener_por_id(reparacion_id)
            if not reparacion:
                logging.warning(f"No se encontró la reparación {reparacion_id}")
                return False
            
            # Completar la reparación
            resultado = reparacion.completar_reparacion(costo=costo, notas=notas)
            
            # Si se completó correctamente, actualizar en la base de datos
            if resultado:
                return self.actualizar(reparacion)
            
            return False
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al completar la reparación {reparacion_id}: {str(e)}")
            return False
    
    def reabrir_reparacion(self, reparacion_id):
        """
        Reabre una reparación cancelada o completada.
        
        Args:
            reparacion_id (str or ObjectId): ID de la reparación
            
        Returns:
            bool: True si se reabrió correctamente, False en caso contrario
        """
        try:
            if isinstance(reparacion_id, str):
                reparacion_id = ObjectId(reparacion_id)
                
            # Obtener la reparación actual
            reparacion = self.obtener_por_id(reparacion_id)
            if not reparacion:
                logging.warning(f"No se encontró la reparación {reparacion_id}")
                return False
            
            # Reabrir la reparación
            resultado = reparacion.reabrir_reparacion()
            
            # Si se reabrió correctamente, actualizar en la base de datos
            if resultado:
                return self.actualizar(reparacion)
            
            return False
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al reabrir la reparación {reparacion_id}: {str(e)}")
            return False
    
    def buscar(self, filtros=None):
        """
        Busca reparaciones según los filtros especificados.
        
        Args:
            filtros: Diccionario con criterios de búsqueda
            
        Returns:
            list: Lista de objetos Reparacion que coinciden con los filtros
        """
        try:
            # Inicializar consulta
            query = {}
            
            # Aplicar filtros si existen
            if filtros:
                # Filtro por ID de falla
                if 'id_falla' in filtros and filtros['id_falla']:
                    query['id_falla'] = {'$regex': filtros['id_falla'], '$options': 'i'}
                
                # Filtro por motivo de falla
                if 'motivo_falla' in filtros and filtros['motivo_falla']:
                    query['motivo_falla'] = {'$regex': filtros['motivo_falla'], '$options': 'i'}
                
                # Filtro por descripción
                if 'descripcion' in filtros and filtros['descripcion']:
                    query['descripcion'] = {'$regex': filtros['descripcion'], '$options': 'i'}
                
                # Filtro por estado
                if 'estado' in filtros and filtros['estado']:
                    query['estado'] = filtros['estado']
                
                # Filtro por camión
                if 'camion_id' in filtros and filtros['camion_id']:
                    # Convertir a ObjectId si es string
                    if isinstance(filtros['camion_id'], str):
                        query['camion_id'] = ObjectId(filtros['camion_id'])
                    else:
                        query['camion_id'] = filtros['camion_id']
                
                # Filtro por mecánico
                if 'mecanico_id' in filtros and filtros['mecanico_id']:
                    # Convertir a ObjectId si es string
                    if isinstance(filtros['mecanico_id'], str):
                        query['mecanico_id'] = ObjectId(filtros['mecanico_id'])
                    else:
                        query['mecanico_id'] = filtros['mecanico_id']
                
                # Filtro por fecha (rango)
                if 'fecha_desde' in filtros and filtros['fecha_desde']:
                    if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
                        query['fecha_entrada'] = {
                            '$gte': filtros['fecha_desde'],
                            '$lte': filtros['fecha_hasta']
                        }
                    else:
                        query['fecha_entrada'] = {'$gte': filtros['fecha_desde']}
            
            # Ejecutar consulta
            reparaciones_docs = self.collection.find(query).sort('fecha_entrada', -1)
            reparaciones = []
            
            for doc in reparaciones_docs:
                reparaciones.append(Reparacion.from_dict(doc))
            
            return reparaciones
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al buscar reparaciones: {str(e)}")
            return []
    
    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de reparaciones.
        
        Args:
            fecha_desde (datetime, optional): Fecha desde la que contar
            fecha_hasta (datetime, optional): Fecha hasta la que contar
            
        Returns:
            dict: Diccionario con estadísticas
        """
        try:
            # Crear filtro por fecha si es necesario
            match_stage = {}
            if fecha_desde or fecha_hasta:
                match_stage['fecha_entrada'] = {}
                if fecha_desde:
                    match_stage['fecha_entrada']['$gte'] = fecha_desde
                if fecha_hasta:
                    match_stage['fecha_entrada']['$lte'] = fecha_hasta
            
            # Pipeline para estadísticas generales
            pipeline = []
            if match_stage:
                pipeline.append({'$match': match_stage})
            
            pipeline.extend([
                {'$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'en_espera': {'$sum': {'$cond': [{'$eq': ['$estado', Reparacion.ESTADO_EN_ESPERA]}, 1, 0]}},
                    'en_reparacion': {'$sum': {'$cond': [{'$eq': ['$estado', Reparacion.ESTADO_EN_REPARACION]}, 1, 0]}},
                    'reparados': {'$sum': {'$cond': [{'$eq': ['$estado', Reparacion.ESTADO_REPARADO]}, 1, 0]}},
                    'cancelados': {'$sum': {'$cond': [{'$eq': ['$estado', Reparacion.ESTADO_CANCELADO]}, 1, 0]}},
                    'costo_total': {'$sum': '$costo'},
                    'tiempo_promedio': {'$avg': {
                        '$cond': [
                            {'$and': [
                                {'$ne': ['$fecha_salida', None]},
                                {'$ne': ['$fecha_entrada', None]}
                            ]},
                            {'$divide': [
                                {'$subtract': ['$fecha_salida', '$fecha_entrada']},
                                3600000  # Convertir ms a horas
                            ]},
                            0
                        ]
                    }}
                }}
            ])
            
            # Ejecutar pipeline
            result = list(self.collection.aggregate(pipeline))
            
            # Si no hay resultados, devolver estadísticas vacías
            if not result:
                return {
                    'total': 0,
                    'en_espera': 0,
                    'en_reparacion': 0,
                    'reparados': 0,
                    'cancelados': 0,
                    'costo_total': 0,
                    'tiempo_promedio': 0
                }
            
            # Eliminar el campo _id del resultado
            estadisticas = result[0]
            estadisticas.pop('_id', None)
            
            return estadisticas
        except PyMongoError as e:
            logging.error(f"ReparacionesDAO: Error al obtener estadísticas: {str(e)}")
            return {
                'total': 0,
                'en_espera': 0,
                'en_reparacion': 0,
                'reparados': 0,
                'cancelados': 0,
                'costo_total': 0,
                'tiempo_promedio': 0
            }
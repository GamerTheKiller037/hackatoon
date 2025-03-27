#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo para representar un mecánico en el sistema.
"""

from datetime import datetime
from bson import ObjectId

class Mecanico:
    """Clase que representa un mecánico en el sistema"""
    
    # Actividades posibles para un mecánico
    ACTIVIDAD_SIN_ACTIVIDAD = "Sin actividad"
    ACTIVIDAD_REPARACION = "En Reparación"
    ACTIVIDAD_MANTENIMIENTO = "En Mantenimiento"
    ACTIVIDAD_DIAGNOSTICO = "En Diagnóstico"
    
    ACTIVIDADES_VALIDAS = [ 
        ACTIVIDAD_SIN_ACTIVIDAD,
        ACTIVIDAD_REPARACION,
        ACTIVIDAD_MANTENIMIENTO,
        ACTIVIDAD_DIAGNOSTICO
    ]
    
    def __init__(self, nombre, apellidos, actividad=ACTIVIDAD_SIN_ACTIVIDAD, 
                 id=None, fecha_registro=None, ultima_actualizacion=None,
                 fecha_contratacion=None):
        """
        Inicializa un nuevo mecánico.
        
        Args:
            nombre (str): Nombre del mecánico
            apellidos (str): Apellidos del mecánico
            actividad (str, optional): Actividad actual del mecánico. Por defecto: "Sin actividad"
            id (ObjectId, optional): ID del documento en MongoDB
            fecha_registro (datetime, optional): Fecha de registro
            ultima_actualizacion (datetime, optional): Última fecha de actualización
            fecha_contratacion (datetime, optional): Fecha de contratación
        """
        self.id = id if id else ObjectId()
        self.nombre = nombre
        self.apellidos = apellidos
        self.actividad = actividad if actividad in self.ACTIVIDADES_VALIDAS else self.ACTIVIDAD_SIN_ACTIVIDAD
        self.fecha_registro = fecha_registro if fecha_registro else datetime.now()
        self.ultima_actualizacion = ultima_actualizacion if ultima_actualizacion else datetime.now()
        self.fecha_contratacion = fecha_contratacion
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Mecanico a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del mecánico
            
        Returns:
            Mecanico: Instancia de Mecanico
        """
        return cls(
            nombre=data.get('nombre'),
            apellidos=data.get('apellidos'),
            actividad=data.get('actividad'),
            id=data.get('_id'),
            fecha_registro=data.get('fecha_registro'),
            ultima_actualizacion=data.get('ultima_actualizacion'),
            fecha_contratacion=data.get('fecha_contratacion')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a un diccionario para almacenar en MongoDB.
        
        Returns:
            dict: Diccionario con los datos del mecánico
        """
        return {
            '_id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'actividad': self.actividad,
            'fecha_registro': self.fecha_registro,
            'ultima_actualizacion': datetime.now(),  # Actualizar la fecha
            'fecha_contratacion': self.fecha_contratacion
        }
    
    def __str__(self):
        """
        Representación en string del mecánico.
        
        Returns:
            str: String con los datos principales del mecánico
        """
        return f"{self.nombre} {self.apellidos} - {self.actividad}"
    
    def actualizar(self, nombre=None, apellidos=None, actividad=None, fecha_contratacion=None):
        """
        Actualiza los datos del mecánico.
        
        Args:
            nombre (str, optional): Nuevo nombre
            apellidos (str, optional): Nuevos apellidos
            actividad (str, optional): Nueva actividad
            fecha_contratacion (datetime, optional): Nueva fecha de contratación
            
        Returns:
            bool: True si se actualizó algún dato, False en caso contrario
        """
        actualizado = False
        
        if nombre is not None and nombre != self.nombre:
            self.nombre = nombre
            actualizado = True
        
        if apellidos is not None and apellidos != self.apellidos:
            self.apellidos = apellidos
            actualizado = True
        
        if actividad is not None and actividad in self.ACTIVIDADES_VALIDAS and actividad != self.actividad:
            self.actividad = actividad
            actualizado = True
        
        if fecha_contratacion is not None and fecha_contratacion != self.fecha_contratacion:
            self.fecha_contratacion = fecha_contratacion
            actualizado = True
        
        if actualizado:
            self.ultima_actualizacion = datetime.now()
        
        return actualizado
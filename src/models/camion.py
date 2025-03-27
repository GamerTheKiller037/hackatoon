#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo para representar un camión en el sistema.
"""

from datetime import datetime
from bson import ObjectId

class Camion:
    """Clase que representa un camión en el sistema"""
    
    # Estados posibles para un camión
    ESTADO_OPERATIVO = "Operativo"
    ESTADO_EN_REPARACION = "En Reparación"
    ESTADO_FUERA_SERVICIO = "Fuera de Servicio"
    
    ESTADOS_VALIDOS = [ 
        ESTADO_OPERATIVO,
        ESTADO_EN_REPARACION,
        ESTADO_FUERA_SERVICIO
    ]
    
    def __init__(self, matricula, modelo, año, estado=ESTADO_OPERATIVO, 
                 id=None, fecha_registro=None, ultima_actualizacion=None):
        """
        Inicializa un nuevo camión.
        
        Args:
            matricula (str): Matrícula del camión
            modelo (str): Modelo del camión
            año (int): Año de fabricación
            estado (str, optional): Estado actual del camión. Por defecto: "Operativo"
            id (ObjectId, optional): ID del documento en MongoDB
            fecha_registro (datetime, optional): Fecha de registro
            ultima_actualizacion (datetime, optional): Última fecha de actualización
        """
        self.id = id if id else ObjectId()
        self.matricula = matricula
        self.modelo = modelo
        self.año = año
        self.estado = estado if estado in self.ESTADOS_VALIDOS else self.ESTADO_OPERATIVO
        self.fecha_registro = fecha_registro if fecha_registro else datetime.now()
        self.ultima_actualizacion = ultima_actualizacion if ultima_actualizacion else datetime.now()
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Camion a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del camión
            
        Returns:
            Camion: Instancia de Camion
        """
        return cls(
            matricula=data.get('matricula'),
            modelo=data.get('modelo'),
            año=data.get('año'),
            estado=data.get('estado'),
            id=data.get('_id'),
            fecha_registro=data.get('fecha_registro'),
            ultima_actualizacion=data.get('ultima_actualizacion')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a un diccionario para almacenar en MongoDB.
        
        Returns:
            dict: Diccionario con los datos del camión
        """
        return {
            '_id': self.id,
            'matricula': self.matricula,
            'modelo': self.modelo,
            'año': self.año,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro,
            'ultima_actualizacion': datetime.now()  # Actualizar la fecha
        }
    
    def __str__(self):
        """
        Representación en string del camión.
        
        Returns:
            str: String con los datos principales del camión
        """
        return f"{self.matricula} | {self.modelo} ({self.año}) - {self.estado}"
    
    def actualizar(self, matricula=None, modelo=None, año=None, estado=None):
        """
        Actualiza los datos del camión.
        
        Args:
            matricula (str, optional): Nueva matrícula
            modelo (str, optional): Nuevo modelo
            año (int, optional): Nuevo año
            estado (str, optional): Nuevo estado
            
        Returns:
            bool: True si se actualizó algún dato, False en caso contrario
        """
        actualizado = False
        
        if matricula is not None and matricula != self.matricula:
            self.matricula = matricula
            actualizado = True
        
        if modelo is not None and modelo != self.modelo:
            self.modelo = modelo
            actualizado = True
        
        if año is not None and año != self.año:
            self.año = año
            actualizado = True
        
        if estado is not None and estado in self.ESTADOS_VALIDOS and estado != self.estado:
            self.estado = estado
            actualizado = True
        
        if actualizado:
            self.ultima_actualizacion = datetime.now()
        
        return actualizado
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo de datos para tareas de mantenimiento preventivo.
"""

from datetime import datetime
from bson import ObjectId

class Preventiva:
    """
    Clase que representa una tarea de mantenimiento preventivo de camiones
    """
    
    # Estados válidos
    ESTADO_PROGRAMADO = "Programado"
    ESTADO_EN_REPARACION = "En Reparación"
    ESTADO_COMPLETADO = "Completado"
    ESTADO_CANCELADO = "Cancelado"
    
    ESTADOS_VALIDOS = [
        ESTADO_PROGRAMADO,
        ESTADO_EN_REPARACION,
        ESTADO_COMPLETADO,
        ESTADO_CANCELADO
    ]
    
    # Niveles de urgencia
    URGENCIA_ALTA = "Alta"
    URGENCIA_MEDIA = "Media"
    URGENCIA_BAJA = "Baja"
    
    NIVELES_URGENCIA = [
        URGENCIA_ALTA,
        URGENCIA_MEDIA,
        URGENCIA_BAJA
    ]
    
    # Tipos de mantenimiento preventivo
    TIPO_CAMBIO_ACEITE = "Cambio de Aceite"
    TIPO_FRENOS = "Revisión de Frenos"
    TIPO_SUSPENSION = "Revisión de Suspensión"
    TIPO_MOTOR = "Revisión de Motor"
    TIPO_ELECTRICO = "Sistema Eléctrico"
    TIPO_GENERAL = "Revisión General"
    
    TIPOS_VALIDOS = [
        TIPO_CAMBIO_ACEITE,
        TIPO_FRENOS,
        TIPO_SUSPENSION,
        TIPO_MOTOR,
        TIPO_ELECTRICO,
        TIPO_GENERAL
    ]
    
    def __init__(self, matricula=None, modelo=None, tipo=None, estado=None, nivel_urgencia=None, id=None):
        """
        Inicializa una nueva tarea de mantenimiento preventivo.
        
        Args:
            matricula (str, optional): Matrícula del camión
            modelo (str, optional): Modelo del camión
            tipo (str, optional): Tipo de mantenimiento preventivo
            estado (str, optional): Estado actual. Por defecto, "Programado".
            nivel_urgencia (str, optional): Nivel de urgencia. Por defecto, "Media".
            id (ObjectId, optional): ID del documento en MongoDB.
        """
        self.id = id if id else ObjectId()
        self.matricula = matricula
        self.modelo = modelo
        self.tipo = tipo if tipo in self.TIPOS_VALIDOS else self.TIPO_GENERAL
        self.estado = estado if estado in self.ESTADOS_VALIDOS else self.ESTADO_PROGRAMADO
        self.nivel_urgencia = nivel_urgencia if nivel_urgencia in self.NIVELES_URGENCIA else self.URGENCIA_MEDIA
        self.fecha_registro = datetime.now()
        self.ultima_actualizacion_reparacion = None
    
    def actualizar(self, matricula=None, modelo=None, tipo=None, estado=None, nivel_urgencia=None):
        """
        Actualiza los datos de la tarea preventiva.
        
        Args:
            matricula (str, optional): Nueva matrícula.
            modelo (str, optional): Nuevo modelo.
            tipo (str, optional): Nuevo tipo.
            estado (str, optional): Nuevo estado.
            nivel_urgencia (str, optional): Nuevo nivel de urgencia.
        """
        if matricula is not None:
            self.matricula = matricula
        
        if modelo is not None:
            self.modelo = modelo
        
        if tipo is not None and tipo in self.TIPOS_VALIDOS:
            self.tipo = tipo
        
        if estado is not None and estado in self.ESTADOS_VALIDOS:
            self.estado = estado
        
        if nivel_urgencia is not None and nivel_urgencia in self.NIVELES_URGENCIA:
            self.nivel_urgencia = nivel_urgencia
        
        # Actualizar fecha de última actualización
        self.ultima_actualizacion_reparacion = datetime.now()
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para almacenamiento.
        
        Returns:
            dict: Representación en diccionario de la tarea preventiva.
        """
        return {
            "_id": self.id,
            "matricula": self.matricula,
            "modelo": self.modelo,
            "tipo": self.tipo,
            "estado": self.estado,
            "nivel_urgencia": self.nivel_urgencia,
            "fecha_registro": self.fecha_registro,
            "ultima_actualizacion_reparacion": self.ultima_actualizacion_reparacion
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Preventiva a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos de la tarea preventiva.
        
        Returns:
            Preventiva: Nueva instancia de Preventiva.
        """
        if not data:
            return None
        
        preventiva = cls(
            id=data.get("_id"),
            matricula=data.get("matricula"),
            modelo=data.get("modelo"),
            tipo=data.get("tipo"),
            estado=data.get("estado"),
            nivel_urgencia=data.get("nivel_urgencia")
        )
        
        # Actualizar las fechas si existen en los datos
        if "fecha_registro" in data:
            preventiva.fecha_registro = data["fecha_registro"]
        
        if "ultima_actualizacion_reparacion" in data:
            preventiva.ultima_actualizacion_reparacion = data["ultima_actualizacion_reparacion"]
        
        return preventiva
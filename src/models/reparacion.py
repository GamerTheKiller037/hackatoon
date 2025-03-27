#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo para representar una reparación en el sistema.
"""

from datetime import datetime
from bson import ObjectId

class Reparacion:
    """Clase que representa una reparación en el sistema"""
    
    # Estados posibles para una reparación
    ESTADO_EN_ESPERA = "En Espera"
    ESTADO_EN_REPARACION = "En Reparación"
    ESTADO_REPARADO = "Reparado"
    ESTADO_CANCELADO = "Cancelado"
    
    ESTADOS_VALIDOS = [
        ESTADO_EN_ESPERA,
        ESTADO_EN_REPARACION,
        ESTADO_REPARADO,
        ESTADO_CANCELADO
    ]
    
    def __init__(self, camion_id, id_falla, motivo_falla, descripcion, 
                 estado=ESTADO_EN_ESPERA, mecanico_id=None, tiempo_estimado=None,
                 fecha_entrada=None, fecha_salida=None, notas_adicionales=None,
                 costo=0.0, id=None):
        """
        Inicializa una nueva reparación.
        
        Args:
            camion_id (ObjectId): ID del camión a reparar
            id_falla (str): Identificador de la falla
            motivo_falla (str): Motivo o causa de la falla
            descripcion (str): Descripción detallada de la falla
            estado (str, optional): Estado de la reparación. Por defecto: "En Espera"
            mecanico_id (ObjectId, optional): ID del mecánico asignado
            tiempo_estimado (float, optional): Tiempo estimado en horas
            fecha_entrada (datetime, optional): Fecha de entrada a reparación
            fecha_salida (datetime, optional): Fecha de salida de reparación
            notas_adicionales (str, optional): Notas adicionales
            costo (float, optional): Costo de la reparación
            id (ObjectId, optional): ID del documento en MongoDB
        """
        self.id = id if id else ObjectId()
        
        # Convertir camion_id a ObjectId si no es None
        if camion_id:
            self.camion_id = camion_id if isinstance(camion_id, ObjectId) else ObjectId(camion_id)
        else:
            self.camion_id = None
            
        self.id_falla = id_falla
        self.motivo_falla = motivo_falla
        self.descripcion = descripcion
        self.estado = estado if estado in self.ESTADOS_VALIDOS else self.ESTADO_EN_ESPERA
        
        # Convertir mecanico_id a ObjectId si no es None
        if mecanico_id:
            self.mecanico_id = mecanico_id if isinstance(mecanico_id, ObjectId) else ObjectId(mecanico_id)
        else:
            self.mecanico_id = None
            
        self.tiempo_estimado = tiempo_estimado
        self.fecha_entrada = fecha_entrada if fecha_entrada else datetime.now()
        self.fecha_salida = fecha_salida
        self.notas_adicionales = notas_adicionales
        self.costo = costo
        self.ultima_actualizacion = datetime.now()
    
    @property
    def esta_en_espera(self):
        """Indica si la reparación está en espera"""
        return self.estado == self.ESTADO_EN_ESPERA
    
    @property
    def esta_en_reparacion(self):
        """Indica si la reparación está en proceso de reparación"""
        return self.estado == self.ESTADO_EN_REPARACION
    
    @property
    def esta_reparado(self):
        """Indica si la reparación está completada"""
        return self.estado == self.ESTADO_REPARADO
    
    @property
    def esta_cancelado(self):
        """Indica si la reparación está cancelada"""
        return self.estado == self.ESTADO_CANCELADO
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Reparacion a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos de la reparación
            
        Returns:
            Reparacion: Instancia de Reparacion
        """
        return cls(
            camion_id=data.get('camion_id'),
            id_falla=data.get('id_falla'),
            motivo_falla=data.get('motivo_falla'),
            descripcion=data.get('descripcion'),
            estado=data.get('estado'),
            mecanico_id=data.get('mecanico_id'),
            tiempo_estimado=data.get('tiempo_estimado'),
            fecha_entrada=data.get('fecha_entrada'),
            fecha_salida=data.get('fecha_salida'),
            notas_adicionales=data.get('notas_adicionales'),
            costo=data.get('costo', 0.0),
            id=data.get('_id')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a un diccionario para almacenar en MongoDB.
        
        Returns:
            dict: Diccionario con los datos de la reparación
        """
        return {
            '_id': self.id,
            'camion_id': self.camion_id,
            'id_falla': self.id_falla,
            'motivo_falla': self.motivo_falla,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'mecanico_id': self.mecanico_id,
            'tiempo_estimado': self.tiempo_estimado,
            'fecha_entrada': self.fecha_entrada,
            'fecha_salida': self.fecha_salida,
            'notas_adicionales': self.notas_adicionales,
            'costo': self.costo,
            'ultima_actualizacion': self.ultima_actualizacion
        }
    
    def __str__(self):
        """
        Representación en string de la reparación.
        
        Returns:
            str: String con los datos principales de la reparación
        """
        return f"Falla: {self.id_falla} | Motivo: {self.motivo_falla} | Estado: {self.estado}"
    
    def actualizar(self, id_falla=None, motivo_falla=None, descripcion=None,
                  estado=None, mecanico_id=None, tiempo_estimado=None,
                  fecha_salida=None, notas_adicionales=None, costo=None):
        """
        Actualiza los datos de la reparación.
        
        Args:
            id_falla (str, optional): Nuevo ID de falla
            motivo_falla (str, optional): Nuevo motivo de falla
            descripcion (str, optional): Nueva descripción
            estado (str, optional): Nuevo estado
            mecanico_id (ObjectId, optional): Nuevo mecánico asignado
            tiempo_estimado (float, optional): Nuevo tiempo estimado
            fecha_salida (datetime, optional): Nueva fecha de salida
            notas_adicionales (str, optional): Nuevas notas adicionales
            costo (float, optional): Nuevo costo de reparación
            
        Returns:
            bool: True si se actualizó algún dato, False en caso contrario
        """
        actualizado = False
        
        if id_falla is not None and id_falla != self.id_falla:
            self.id_falla = id_falla
            actualizado = True
        
        if motivo_falla is not None and motivo_falla != self.motivo_falla:
            self.motivo_falla = motivo_falla
            actualizado = True
        
        if descripcion is not None and descripcion != self.descripcion:
            self.descripcion = descripcion
            actualizado = True
        
        if estado is not None and estado in self.ESTADOS_VALIDOS and estado != self.estado:
            # Si cambia a estado "Reparado", establecer fecha de salida si no existe
            if estado == self.ESTADO_REPARADO and self.fecha_salida is None:
                self.fecha_salida = datetime.now()
            
            self.estado = estado
            actualizado = True
        
        if mecanico_id is not None:
            if isinstance(mecanico_id, str):
                mecanico_id = ObjectId(mecanico_id)
                
            if mecanico_id != self.mecanico_id:
                self.mecanico_id = mecanico_id
                
                # Si se asigna un mecánico, cambiar el estado a En Reparación si estaba en espera
                if self.estado == self.ESTADO_EN_ESPERA:
                    self.estado = self.ESTADO_EN_REPARACION
                
                actualizado = True
        
        if tiempo_estimado is not None and tiempo_estimado != self.tiempo_estimado:
            self.tiempo_estimado = tiempo_estimado
            actualizado = True
        
        if fecha_salida is not None and fecha_salida != self.fecha_salida:
            self.fecha_salida = fecha_salida
            actualizado = True
        
        if notas_adicionales is not None and notas_adicionales != self.notas_adicionales:
            self.notas_adicionales = notas_adicionales
            actualizado = True
            
        if costo is not None and costo != self.costo:
            self.costo = costo
            actualizado = True
        
        if actualizado:
            self.ultima_actualizacion = datetime.now()
            
        return actualizado
    
    def completar_reparacion(self, costo=None, notas=None):
        """
        Marca la reparación como completada.
        
        Args:
            costo (float, optional): Costo final de la reparación
            notas (str, optional): Notas sobre la reparación realizada
            
        Returns:
            bool: True si se completó la reparación, False si ya estaba completada
        """
        if self.estado == self.ESTADO_REPARADO:
            return False
        
        self.estado = self.ESTADO_REPARADO
        self.fecha_salida = datetime.now()
        
        if costo is not None:
            self.costo = costo
        
        if notas:
            if self.notas_adicionales:
                self.notas_adicionales += f"\n\nNotas de completado ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n{notas}"
            else:
                self.notas_adicionales = f"Notas de completado ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n{notas}"
        
        self.ultima_actualizacion = datetime.now()
        return True
    
    def cancelar_reparacion(self, motivo=None):
        """
        Cancela la reparación.
        
        Args:
            motivo (str, optional): Motivo de la cancelación
            
        Returns:
            bool: True si se canceló la reparación, False si ya estaba cancelada o reparada
        """
        if self.estado == self.ESTADO_CANCELADO or self.estado == self.ESTADO_REPARADO:
            return False
            
        self.estado = self.ESTADO_CANCELADO
        
        if motivo:
            if self.notas_adicionales:
                self.notas_adicionales += f"\n\nMotivo de cancelación ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n{motivo}"
            else:
                self.notas_adicionales = f"Motivo de cancelación ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n{motivo}"
        
        self.ultima_actualizacion = datetime.now()
        return True
    
    def reabrir_reparacion(self):
        """
        Reabre una reparación cancelada o completada.
        
        Returns:
            bool: True si se reabrió la reparación, False si no estaba cancelada ni completada
        """
        if not (self.estado == self.ESTADO_REPARADO or self.estado == self.ESTADO_CANCELADO):
            return False
            
        # Si tiene mecánico asignado, pasa a estado En Reparación, si no a En Espera
        self.estado = self.ESTADO_EN_REPARACION if self.mecanico_id else self.ESTADO_EN_ESPERA
        
        # Si estaba marcada como reparada, quitar fecha de salida
        if self.fecha_salida:
            self.fecha_salida = None
            
        # Añadir nota de reapertura
        if self.notas_adicionales:
            self.notas_adicionales += f"\n\nReparación reabierta ({datetime.now().strftime('%d/%m/%Y %H:%M')})"
        else:
            self.notas_adicionales = f"Reparación reabierta ({datetime.now().strftime('%d/%m/%Y %H:%M')})"
        
        self.ultima_actualizacion = datetime.now()
        return True
    
    def asignar_mecanico(self, mecanico_id):
        """
        Asigna un mecánico a la reparación.
        
        Args:
            mecanico_id (ObjectId or str): ID del mecánico a asignar
            
        Returns:
            bool: True si se asignó correctamente, False si la reparación está cancelada o reparada
        """
        if self.estado == self.ESTADO_CANCELADO or self.estado == self.ESTADO_REPARADO:
            return False
            
        # Convertir string a ObjectId si es necesario
        if isinstance(mecanico_id, str):
            mecanico_id = ObjectId(mecanico_id)
            
        self.mecanico_id = mecanico_id
        
        # Actualizar estado a En Reparación
        if self.estado == self.ESTADO_EN_ESPERA:
            self.estado = self.ESTADO_EN_REPARACION
            
        self.ultima_actualizacion = datetime.now()
        return True
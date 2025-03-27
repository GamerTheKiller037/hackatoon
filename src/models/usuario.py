#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modelo para representar un usuario en el sistema.
"""

import hashlib
from datetime import datetime
from bson import ObjectId

class Usuario:
    """Clase que representa un usuario en el sistema"""
    
    # Roles posibles para un usuario
    ROL_ADMIN = "Admin"
    ROL_MECANICO = "Mecánico"
    ROL_SUPERVISOR = "Supervisor"
    
    ROLES_VALIDOS = [
        ROL_ADMIN,
        ROL_MECANICO,
        ROL_SUPERVISOR
    ]
    
    def __init__(self, nombre, apellido, usuario, password=None, password_hash=None,
                 rol=ROL_MECANICO, activo=True, id=None):
        """
        Inicializa un nuevo usuario.
        
        Args:
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            usuario (str): Nombre de usuario para inicio de sesión
            password (str, optional): Contraseña en texto plano (se convierte a hash)
            password_hash (str, optional): Hash de la contraseña ya generado
            rol (str, optional): Rol del usuario. Por defecto: "Mecánico"
            activo (bool, optional): Indica si el usuario está activo. Por defecto: True
            id (ObjectId, optional): ID del documento en MongoDB
        """
        self.id = id if id else ObjectId()
        self.nombre = nombre
        self.apellido = apellido
        self.usuario = usuario
        
        # Manejar la contraseña
        if password:
            self.password_hash = self._hash_password(password)
        elif password_hash:
            self.password_hash = password_hash
        else:
            self.password_hash = None
            
        self.rol = rol if rol in self.ROLES_VALIDOS else self.ROL_MECANICO
        self.activo = activo
    
    @staticmethod
    def _hash_password(password):
        """
        Genera un hash para la contraseña.
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        # En una aplicación real, usar bcrypt o similar
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verificar_password(self, password):
        """
        Verifica si la contraseña es correcta.
        
        Args:
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        return self.password_hash == self._hash_password(password)
    
    def cambiar_password(self, password):
        """
        Cambia la contraseña del usuario.
        
        Args:
            password (str): Nueva contraseña
        """
        self.password_hash = self._hash_password(password)
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Usuario a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del usuario
            
        Returns:
            Usuario: Instancia de Usuario
        """
        return cls(
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            usuario=data.get('usuario'),
            password_hash=data.get('password'),
            rol=data.get('rol'),
            activo=data.get('activo', True),
            id=data.get('_id')
        )
    
    def to_dict(self):
        """
        Convierte la instancia a un diccionario para almacenar en MongoDB.
        
        Returns:
            dict: Diccionario con los datos del usuario
        """
        return {
            '_id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'usuario': self.usuario,
            'password': self.password_hash,
            'rol': self.rol,
            'activo': self.activo
        }
    
    def __str__(self):
        """
        Representación en string del usuario.
        
        Returns:
            str: String con los datos principales del usuario
        """
        return f"{self.nombre} {self.apellido} ({self.usuario}) - {self.rol}"
    
    def actualizar(self, nombre=None, apellido=None, usuario=None,
                  rol=None, activo=None):
        """
        Actualiza los datos del usuario.
        
        Args:
            nombre (str, optional): Nuevo nombre
            apellido (str, optional): Nuevo apellido
            usuario (str, optional): Nuevo nombre de usuario
            rol (str, optional): Nuevo rol
            activo (bool, optional): Nuevo estado de activación
            
        Returns:
            bool: True si se actualizó algún dato, False en caso contrario
        """
        actualizado = False
        
        if nombre is not None and nombre != self.nombre:
            self.nombre = nombre
            actualizado = True
        
        if apellido is not None and apellido != self.apellido:
            self.apellido = apellido
            actualizado = True
        
        if usuario is not None and usuario != self.usuario:
            self.usuario = usuario
            actualizado = True
        
        if rol is not None and rol in self.ROLES_VALIDOS and rol != self.rol:
            self.rol = rol
            actualizado = True
        
        if activo is not None and activo != self.activo:
            self.activo = activo
            actualizado = True
        
        return actualizado
    
    def nombre_completo(self):
        """
        Obtiene el nombre completo del usuario.
        
        Returns:
            str: Nombre completo (nombre + apellido)
        """
        return f"{self.nombre} {self.apellido}"
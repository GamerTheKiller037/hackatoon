#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Controlador para la autenticación de usuarios.
"""

import logging
from database.usuarios_dao import UsuariosDAO
from models.usuario import Usuario

class AuthController:
    """Controlador para la autenticación de usuarios"""
    
    def __init__(self):
        """Inicializa el controlador de autenticación"""
        self.usuarios_dao = UsuariosDAO()
        self._current_user = None
    
    def login(self, username, password):
        """
        Autentica a un usuario.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
        
        Returns:
            Usuario: Usuario autenticado, None si la autenticación falló
        """
        try:
            user = self.usuarios_dao.autenticar(username, password)
            if user:
                self._current_user = user
                logging.info(f"Usuario autenticado: {user.nombre} {user.apellido} ({user.rol})")
                return user
            else:
                logging.warning(f"Intento de autenticación fallido para el usuario: {username}")
                return None
        except Exception as e:
            logging.error(f"Error en la autenticación: {str(e)}")
            return None
    
    def logout(self):
        """Cierra la sesión del usuario actual"""
        if self._current_user:
            logging.info(f"Cierre de sesión: {self._current_user.nombre} {self._current_user.apellido}")
            self._current_user = None
    
    @property
    def current_user(self):
        """
        Obtiene el usuario actual.
        
        Returns:
            Usuario: Usuario autenticado, None si no hay usuario autenticado
        """
        return self._current_user
    
    def change_password(self, user_id, old_password, new_password):
        """
        Cambia la contraseña de un usuario.
        
        Args:
            user_id (str): ID del usuario
            old_password (str): Contraseña actual
            new_password (str): Nueva contraseña
        
        Returns:
            bool: True si se cambió la contraseña, False en caso contrario
        """
        try:
            # Obtener el usuario
            user = self.usuarios_dao.obtener_por_id(user_id)
            if not user:
                logging.warning(f"Usuario no encontrado: {user_id}")
                return False
            
            # Verificar la contraseña actual
            if not user.verificar_password(old_password):
                logging.warning(f"Contraseña incorrecta para el usuario: {user.usuario}")
                return False
            
            # Cambiar la contraseña
            return self.usuarios_dao.cambiar_password(user_id, new_password)
        except Exception as e:
            logging.error(f"Error al cambiar la contraseña: {str(e)}")
            return False
    
    def is_admin(self, user=None):
        """
        Verifica si el usuario es administrador.
        
        Args:
            user (Usuario, optional): Usuario a verificar. Si es None, se verifica el usuario actual.
        
        Returns:
            bool: True si el usuario es administrador, False en caso contrario
        """
        if user is None:
            user = self._current_user
        
        return user is not None and user.rol == Usuario.ROL_ADMIN
    
    def create_user(self, nombre, apellido, usuario, password, rol=Usuario.ROL_MECANICO):
        """
        Crea un nuevo usuario.
        
        Args:
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            usuario (str): Nombre de usuario
            password (str): Contraseña
            rol (str, optional): Rol del usuario. Por defecto: ROL_MECANICO
        
        Returns:
            Usuario: Usuario creado, None si no se pudo crear
        """
        try:
            # Verificar si ya existe un usuario con el mismo nombre de usuario
            if self.usuarios_dao.obtener_por_usuario(usuario):
                logging.warning(f"Ya existe un usuario con el nombre de usuario: {usuario}")
                return None
            
            # Crear el usuario
            new_user = Usuario(
                nombre=nombre,
                apellido=apellido,
                usuario=usuario,
                password=password,
                rol=rol
            )
            
            if self.usuarios_dao.insertar(new_user):
                logging.info(f"Usuario creado: {nombre} {apellido} ({rol})")
                return new_user
            else:
                logging.warning(f"No se pudo crear el usuario: {nombre} {apellido}")
                return None
        except Exception as e:
            logging.error(f"Error al crear el usuario: {str(e)}")
            return None
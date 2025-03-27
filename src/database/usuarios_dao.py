#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Access Object (DAO) para operaciones CRUD con usuarios.
"""

import logging
from bson import ObjectId
from pymongo.errors import PyMongoError
from database.connection import DatabaseConnection
from models.usuario import Usuario

class UsuariosDAO:
    """Clase para operaciones CRUD con usuarios en MongoDB"""
    
    def __init__(self):
        """Inicializa el DAO conectándose a la base de datos"""
        self.db_connection = DatabaseConnection()
        self.collection = self.db_connection.get_usuarios_collection()
    
    def obtener_todos(self):
        """
        Obtiene todos los usuarios de la base de datos.
        
        Returns:
            list: Lista de objetos Usuario
        """
        try:
            usuarios = self.collection.find()
            return [Usuario.from_dict(u) for u in usuarios]
        except PyMongoError as e:
            logging.error(f"Error al obtener los usuarios: {str(e)}")
            return []
    
    def obtener_por_id(self, usuario_id):
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id (str or ObjectId): ID del usuario
            
        Returns:
            Usuario: Objeto Usuario si existe, None en caso contrario
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
                
            usuario = self.collection.find_one({'_id': usuario_id})
            if usuario:
                return Usuario.from_dict(usuario)
            return None
        except PyMongoError as e:
            logging.error(f"Error al obtener el usuario {usuario_id}: {str(e)}")
            return None
    
    def obtener_por_usuario(self, nombre_usuario):
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            nombre_usuario (str): Nombre de usuario
            
        Returns:
            Usuario: Objeto Usuario si existe, None en caso contrario
        """
        try:
            usuario = self.collection.find_one({'usuario': nombre_usuario})
            if usuario:
                return Usuario.from_dict(usuario)
            return None
        except PyMongoError as e:
            logging.error(f"Error al obtener el usuario {nombre_usuario}: {str(e)}")
            return None
    
    def autenticar(self, nombre_usuario, password):
        """
        Autentica a un usuario por su nombre de usuario y contraseña.
        
        Args:
            nombre_usuario (str): Nombre de usuario
            password (str): Contraseña
            
        Returns:
            Usuario: Objeto Usuario si la autenticación es exitosa, None en caso contrario
        """
        try:
            usuario = self.obtener_por_usuario(nombre_usuario)
            if usuario and usuario.verificar_password(password) and usuario.activo:
                return usuario
            return None
        except Exception as e:
            logging.error(f"Error al autenticar el usuario {nombre_usuario}: {str(e)}")
            return None
    
    def insertar(self, usuario):
        """
        Inserta un nuevo usuario en la base de datos.
        
        Args:
            usuario (Usuario): Objeto Usuario a insertar
            
        Returns:
            bool: True si se insertó correctamente, False en caso contrario
        """
        try:
            # Verificar si ya existe un usuario con el mismo nombre de usuario
            if self.obtener_por_usuario(usuario.usuario):
                logging.warning(f"Ya existe un usuario con nombre de usuario {usuario.usuario}")
                return False
            
            # Insertar el usuario
            result = self.collection.insert_one(usuario.to_dict())
            return result.acknowledged
        except PyMongoError as e:
            logging.error(f"Error al insertar el usuario: {str(e)}")
            return False
    
    def actualizar(self, usuario):
        """
        Actualiza un usuario existente en la base de datos.
        
        Args:
            usuario (Usuario): Objeto Usuario con los datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            result = self.collection.update_one(
                {'_id': usuario.id},
                {'$set': usuario.to_dict()}
            )
            return result.matched_count > 0
        except PyMongoError as e:
            logging.error(f"Error al actualizar el usuario {usuario.id}: {str(e)}")
            return False
    
    def eliminar(self, usuario_id):
        """
        Elimina un usuario de la base de datos.
        
        Args:
            usuario_id (str or ObjectId): ID del usuario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
                
            result = self.collection.delete_one({'_id': usuario_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logging.error(f"Error al eliminar el usuario {usuario_id}: {str(e)}")
            return False
    
    def cambiar_password(self, usuario_id, nueva_password):
        """
        Cambia la contraseña de un usuario.
        
        Args:
            usuario_id (str or ObjectId): ID del usuario
            nueva_password (str): Nueva contraseña
            
        Returns:
            bool: True si se cambió correctamente, False en caso contrario
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
                
            # Obtener el usuario para generar el hash de la nueva contraseña
            usuario = self.obtener_por_id(usuario_id)
            if not usuario:
                return False
                
            usuario.cambiar_password(nueva_password)
            
            result = self.collection.update_one(
                {'_id': usuario_id},
                {'$set': {'password': usuario.password_hash}}
            )
            return result.matched_count > 0
        except PyMongoError as e:
            logging.error(f"Error al cambiar la contraseña del usuario {usuario_id}: {str(e)}")
            return False
    
    def obtener_por_rol(self, rol):
        """
        Obtiene los usuarios que tienen un rol específico.
        
        Args:
            rol (str): Rol de los usuarios
            
        Returns:
            list: Lista de objetos Usuario
        """
        try:
            usuarios = self.collection.find({'rol': rol})
            return [Usuario.from_dict(u) for u in usuarios]
        except PyMongoError as e:
            logging.error(f"Error al obtener los usuarios por rol {rol}: {str(e)}")
            return []
    
    def cambiar_estado(self, usuario_id, activo):
        """
        Cambia el estado de activación de un usuario.
        
        Args:
            usuario_id (str or ObjectId): ID del usuario
            activo (bool): Nuevo estado de activación
            
        Returns:
            bool: True si se cambió correctamente, False en caso contrario
        """
        try:
            if isinstance(usuario_id, str):
                usuario_id = ObjectId(usuario_id)
                
            result = self.collection.update_one(
                {'_id': usuario_id},
                {'$set': {'activo': activo}}
            )
            return result.matched_count > 0
        except PyMongoError as e:
            logging.error(f"Error al cambiar el estado del usuario {usuario_id}: {str(e)}")
            return False
    
    def tiene_admin(self):
        """
        Verifica si existe al menos un usuario administrador.
        
        Returns:
            bool: True si existe al menos un admin, False en caso contrario
        """
        try:
            count = self.collection.count_documents({'rol': Usuario.ROL_ADMIN})
            return count > 0
        except PyMongoError as e:
            logging.error(f"Error al verificar si existen administradores: {str(e)}")
            return False
    
    def crear_admin_default(self):
        """
        Crea un usuario administrador por defecto si no existe ninguno.
        
        Returns:
            bool: True si se creó el admin, False en caso contrario
        """
        try:
            if self.tiene_admin():
                return False
                
            admin = Usuario(
                nombre="Administrador",
                apellido="Sistema",
                usuario="admin",
                password="admin",  # En un entorno real, usar una contraseña más segura
                rol=Usuario.ROL_ADMIN
            )
            
            return self.insertar(admin)
        except Exception as e:
            logging.error(f"Error al crear el administrador por defecto: {str(e)}")
            return False
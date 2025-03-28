#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo de inicio de sesión para la aplicación.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
from database.usuarios_dao import UsuariosDAO

class LoginDialog(QDialog):
    """Diálogo de inicio de sesión"""
    
    def __init__(self, parent=None):
        """Inicializa el diálogo de inicio de sesión"""
        super().__init__(parent)
        
        self.usuarios_dao = UsuariosDAO()
        self.current_user = None
        
        # Crear el admin por defecto si no existe ninguno
        self.usuarios_dao.crear_admin_default()
        
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Inicio de Sesión")
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)  # Altura mínima aumentada para evitar problemas
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Establecer fuente más grande
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Barra superior morada
        header = QFrame()
        header.setFixedHeight(60)  # Altura fija
        header.setStyleSheet("background-color: #6a1b9a;")
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Título
        title_label = QLabel("Sistema de Gestión de Reparaciones de Camiones")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header)
        
        # Agregar espacio
        main_layout.addSpacing(20)
        
        # Instrucción
        instruction_label = QLabel("Ingrese sus credenciales para acceder al sistema")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("color: #555; font-size: 14px;")
        main_layout.addWidget(instruction_label)
        
        # Agregar espacio
        main_layout.addSpacing(20)
        
        # Sección de usuario
        user_section = QVBoxLayout()
        user_section.setSpacing(8)
        
        user_label = QLabel("Usuario:")
        user_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        user_section.addWidget(user_label)
        
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.usuario_input.setMaxLength(50)
        self.usuario_input.setMinimumHeight(35)
        self.usuario_input.setStyleSheet("padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 18px;")
        user_section.addWidget(self.usuario_input)
        
        main_layout.addLayout(user_section)
        
        # Agregar espacio
        main_layout.addSpacing(15)
        
        # Sección de contraseña
        password_section = QVBoxLayout()
        password_section.setSpacing(8)
        
        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        password_section.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaxLength(50)
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet("padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 18px;")
        password_section.addWidget(self.password_input)
        
        main_layout.addLayout(password_section)
        
        # Agregar espacio flexible
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setDefault(True)
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("background-color: #6a1b9a; color: white; font-weight: bold; font-size: 14px; border-radius: 4px;")
        self.login_button.clicked.connect(self.handle_login)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; font-size: 14px; border-radius: 4px;")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Información
        info_label = QLabel("Aplicación desarrollada para el sistema de Gestión de Reparaciones de Camiones")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; font-size: 12px; margin-top: 15px;")
        main_layout.addWidget(info_label)
        
        # Establecer el focus en el campo de usuario
        self.usuario_input.setFocus()

    def handle_login(self):
        """Maneja el proceso de inicio de sesión"""
        usuario = self.usuario_input.text().strip()
        password = self.password_input.text()
        
        if not usuario or not password:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Por favor, ingrese usuario y contraseña."
            )
            return
        
        # Autenticar usuario
        user = self.usuarios_dao.autenticar(usuario, password)
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Error de autenticación",
                "Usuario o contraseña incorrectos, o la cuenta está desactivada."
            )
            self.password_input.clear()
            self.password_input.setFocus()

    def get_current_user(self):
        """
        Obtiene el usuario autenticado.
        
        Returns:
            Usuario: Objeto Usuario autenticado
        """
        return self.current_user
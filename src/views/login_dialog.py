#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo de inicio de sesión para la aplicación.
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
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
        self.setMinimumWidth(400)
        self.setFixedHeight(300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo o título
        title_label = QLabel("Sistema de Gestión de Reparaciones de Camiones")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Campos de inicio de sesión
        form_layout = QVBoxLayout()
        
        # Usuario
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.usuario_input.setMaxLength(50)
        form_layout.addWidget(QLabel("Usuario:"))
        form_layout.addWidget(self.usuario_input)
        
        # Contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaxLength(50)
        form_layout.addWidget(QLabel("Contraseña:"))
        form_layout.addWidget(self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.handle_login)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Información
        info_label = QLabel("Ingrese sus credenciales para acceder al sistema")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; font-size: 12px;")
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

if __name__ == "__main__":
    # Prueba del diálogo
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = LoginDialog()
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        print(f"Usuario autenticado: {dialog.get_current_user()}")
    else:
        print("Inicio de sesión cancelado")
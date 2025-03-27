# Guarda esto como check_files.py
import os

file_path = "src/views/reparaciones/lista_reparaciones.py"
if os.path.exists(file_path):
    print(f"El archivo {file_path} existe")
    with open(file_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        print(f"Primera línea: {first_line}")
else:
    print(f"El archivo {file_path} no existe")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    print(f"Directorio creado: {os.path.dirname(file_path)}")
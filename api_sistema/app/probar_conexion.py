
from database import obtener_conexion

conexion = obtener_conexion()

if conexion:
    print("Conexión exitosa.")

    conexion.close()
else:
    print("No se pudo conectar con la base de datos.")

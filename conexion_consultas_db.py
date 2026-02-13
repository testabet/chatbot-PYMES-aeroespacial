import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def conectarse():  
    conexion=None
    try: 
        # Establece la conexion a la DB / mi_conexion es un obj
        conexion= mysql.connector.connect(
            host="localhost",
            user=os.getenv("DB_user"),
            passwd=os.getenv("DB_pass"), 
            database= "importaciones_aeroesp_2023", # PARA CONECTARSE DIRECTAMENTE A LA DB  
        )
        return conexion

    except Error as e:
        print(f"Ocurrio un error al conectarse a la base de datos: {e}")

        return None

def desconectarse(conexion):
    if conexion:
        conexion.close()
        print("Conexion finalizada")
    return 


def ejecutar_consulta_prueba():
    """
    Función de prueba para verificar que leemos datos.
    Usa 'with' para asegurar que la conexión se cierre sola.
    """
    conexion = conectarse()
    
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            #ursor.execute("SELECT * FROM productos LIMIT 3;")
            cursor.execute("SELECT * FROM paises LIMIT 3;")  
            #cursor.execute("SELECT * FROM importaciones LIMIT 3;") 
            
            registros = cursor.fetchall()
            
            print(f"--- Conexión Exitosa. Mostrando {len(registros)} productos ---")
            for fila in registros:
                print(fila)
                
        except Error as e:
            print(f"Error en la consulta: {e}")
        finally:
            # El bloque 'finally' se ejecuta SIEMPRE, haya error o no.
            if conexion.is_connected():
                cursor.close()
                conexion.close()
                print("--- Conexión cerrada correctamente ---")
    else:
        print("No se pudo establecer la conexión para realizar la consulta.")

# ---------------------------------------------------------
# BLOQUE PRINCIPAL (Main)
# ---------------------------------------------------------
if __name__ == "__main__":
    # Este 'if' asegura que el código de prueba solo corra si ejecutas este archivo directamente,
    # y no si lo importas desde el chatbot.
    ejecutar_consulta_prueba()
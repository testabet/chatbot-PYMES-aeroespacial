import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(host="localhost", 
                                    user=os.getenv("DB_user"),
                                    password=os.getenv("DB_pass"), 
                                    database="importaciones_aeroesp_2023",
                                    allow_local_infile=True)
    cursor = conn.cursor() 
   
     # Cargar desde archivo (si está habilitado en el servidor)
    ruta_pais=r"C:/Users/Betina/Documents/Diplo soluciones de IA/database_sql/PAISES_SQL.csv"
    ruta_prod=r"C:/Users/Betina/Documents/Diplo soluciones de IA/database_sql/PRODUCTOS_SQL.csv"
    ruta_imp= r"C:/Users/Betina/Documents/Diplo soluciones de IA/database_sql/IMPORTACIONES_SQL.csv"

    archivos= [ruta_pais,ruta_prod,ruta_imp]
    tablas=['paises','productos','importaciones']
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    conn.commit()

    for ruta,tabla in zip(archivos,tablas):
        print(ruta, tabla)
        query= f"""
                LOAD DATA LOCAL INFILE '{ruta}' 
                INTO TABLE {tabla}
                CHARACTER SET utf8mb4
                FIELDS TERMINATED BY ',' 
                ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
                IGNORE 1 LINES 
                """
        cursor.execute(query)
        conn.commit()

        print(f"Datos cargados exitosamente desde {ruta}")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM importaciones")
    total = cursor.fetchone()[0]
    print(f"✅ Filas totales cargadas en SQL: {total}")
    
    
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
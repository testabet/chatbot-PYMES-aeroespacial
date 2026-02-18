import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(host="localhost", 
                                    user=os.getenv("DB_user"),
                                    password=os.getenv("DB_pass"), 
                                    database="importaciones_aeroesp_2024",
                                    allow_local_infile=True)
    cursor = conn.cursor() 
   
     # Cargar desde archivo (si está habilitado en el servidor)
    ruta_pais=r"C:/Users/Betina/Documents/Diplo soluciones de IA/chatbot-sector-aeroespacial/dataset2024/PAISES_SQL_2024_252.csv"
    ruta_prod=r"C:/Users/Betina/Documents/Diplo soluciones de IA/chatbot-sector-aeroespacial/dataset2024/PRODUCTOS_SQL_2024_sintotal.csv"
    ruta_imp= r"C:/Users/Betina/Documents/Diplo soluciones de IA/chatbot-sector-aeroespacial/dataset2024/IMPORTACIONES_SQL_2024.csv"

    archivos= [ruta_pais,ruta_prod,ruta_imp]
    tablas=['paises','productos','importaciones']

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

    
    cursor.execute("SELECT COUNT(*) FROM importaciones")
    total = cursor.fetchone()[0]
    print(f"✅ Filas totales cargadas en importaciones SQL: {total}")
    
    
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
import pandas as pd
import os
from dotenv import load_dotenv
from busqueda_semantica_productos_paises import BuscadorDeProductos
from sql_llama3_pais_prod import generar_sql_llama3,generar_respuesta_final
from conexion_consultas_db import conectarse
from collections import deque

load_dotenv()

# --- CONFIGURACIÓN ---
UMBRAL_CONFIANZA = 0.55  # Si el score es menor a esto, es pregunta general
MAX_HISTORIAL = 3        # Guardamos 3 pares de preguntas/respuestas

def main():
    # 1. Inicializamos el buscador semantico
    buscador = BuscadorDeProductos()
    
    # 2. Inicializamos el historial
    historial = deque(maxlen=MAX_HISTORIAL * 2)

    print("\n🚀 Chatbot Aeroespacial Listo. Pregunta algo (o escribe 'salir').")

    while True:
        pregunta = input("\nUsuario: ")
        if pregunta.lower() in ['salir', 'chau']:
            break
            
        
        #3. Clasificamos con el puntaje obtenido en la busqueda semantica segun el umbral.
        #    Si supera el umbral, selecciona la info de producto o pais segun cual sea mayor    
        #   Si no lo supera hace una busqueda general. 
        match_prod,match_pais = buscador.buscar_producto_pais(pregunta)
        info = None

        if max(match_prod['score_prod'],match_pais['score_pais']) >= UMBRAL_CONFIANZA:

            if match_prod['score_prod'] >= match_pais['score_pais']:
                print(f"   🔍 Producto detectado: {match_prod['nombre_prod']} (Confianza: {match_prod['score_prod']:.2f})")
                info = match_prod
                info['tipo']="producto"
            
            else:
                print(f"   🔍 Pais detectado: {match_pais['nombre_pais']} (Confianza: {match_pais['score_pais']:.2f})")
                info= match_pais
                info['tipo']="pais"
                
        
        else:
            print(f"   🌐 Pregunta General detectada (Score bajo: {match_pais['score_pais']:.2f} para paises, y {match_prod['score_prod']:.2f} para productos). Buscando en toda la base.")
            info = None 

        # VERIFICAICON DE LA INFO Q LE ENTRA AL MODELO
        #print("Informacion que entra al modelo para generar la consulta:")
        #print(info)
        
        # 4. Generación SQL (Le pasamos la data masticada a Llama)
        print("   🧠 Generando consulta SQL...")
        sql = generar_sql_llama3(pregunta, list(historial),info)
        print(f"   💻 SQL: {sql}")

        # 5. Ejecución
        datos_para_ia = "No se encontraron datos."
        df_mostrar = None
        
        conn = conectarse()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                filas = cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                
                if filas:
                    df = pd.DataFrame(filas, columns=cols)
                    df_mostrar = df # Guardamos para mostrar la tabla al final
                    # Convertimos el DF a string para que la IA lo lea
                    datos_para_ia = df.to_string(index=False)
                    
                else:
                    print("\n🤷‍♂️ La consulta es válida, pero no arrojó datos (0 resultados).")
            
            except Exception as e:
                print(f"\n❌ Error SQL: {e}")
                datos_para_ia = f"Error al ejecutar SQL: {e}"
            finally:
                conn.close()


        #6. Generacion de respuesta final
        respuesta_final = generar_respuesta_final(pregunta, datos_para_ia)
        
        print("\n" + "="*40)
        print("RESPUESTA:")
        print(respuesta_final)
        print("="*40)
        
        # Mostrar tabla de datos crudos 
        if df_mostrar is not None:
            print("\nDetalle de Datos - Tabla Fuente")
            print(df_mostrar.to_string(index=False))
            print("="*40)
        
        # 7.: Guardar en Memoria 
        historial.append(f"Usuario: {pregunta}")
        historial.append(f"Asistente (Datos encontrados): {datos_para_ia}")

if __name__ == "__main__":
    main()

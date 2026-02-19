import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generar_sql_llama3(pregunta_usuario, historial,info=None):
    global esquema 
    """
    info_producto: Diccionario con {id, nombre, score} que viene del buscador semántico
    """
    
    esquema = """
    TABLAS DISPONIBLES :
    1. paises(
        - id_pais (PK)
        - codigo_ISO (ejemplo: "ARG","BRA")
        - nombre (ejemplo: "Argentina", "Brasil")
        - proyeccion de crecimiento (valor numerico)
        - eci_sitc (indice de complejidad economica, valor numerico)
        - eci_rank_sitc (ranking del pais segun el indice de complejidad economica)
        )
    2. productos(
        - id_producto (PK)
        - codigo_sitc (ejemplo: 7921)
        - nombre_producto (ejemplo: "Llantas, gomas, neumaticos nuevos para aeronaves")
        - valor_total_exportacion_usd (numero, valor monetario en USD)
        )
    3. importaciones(
        - id_importacion (PK)
        - id_pais_exportador (FK -> paises.id_pais)
        - id_pais_importador (FK -> paises.id_pais)
        - id_producto (FK -> productos.id_producto)
        - anio (ejemplo: 2023)
        - valor_importacion_usd (numero, valor monetario en USD)
        )
    """
    
    system_promt=f"""
                    Eres un experto Ingeniero de Datos SQL especializado en MySQL.
                    Tu tarea es generar consultas SQL exactas basadas en la pregunta del usuario.
                    Tu contexto (esquema de base de datos):
                    {esquema}    
                    
                    REGLAS:
                    1. Responde SOLAMENTE con el código SQL. Sin saludos, sin markdown, sin explicaciones.
                    2. Usa JOINs explícitos:
                    - Si preguntan por "país importador", une importaciones.id_pais_importador = paises.id_pais.
                    - Si preguntan por "país exportador", une importaciones.id_pais_exportador = paises.id_pais.
                    - Si preguntan por nombre de producto, une con la tabla productos.
                    3. Para preguntas de "Top X", usa ORDER BY valor_importacion_usd DESC LIMIT X.
                    4. Devuelve siempre columnas legibles (nombres de países/productos/valores en USD), no solo IDs.
                """
    
    # Aquí inyectamos el ID encontrado en el prompt
    
    contexto=""
    if info:
        if info["tipo"]== "producto":
            contexto = f"""
                            CONTEXTO:
                            El usuario está preguntando por el producto: "{info['nombre_prod']}"
                            cuyo ID interno en la base de datos es: {info['id_prod']} y el codigo SITC es: {info['codigo_SITC_prod']}
                            
                            INSTRUCCIÓN OBLIGATORIA:
                            NO CONFUNDIR EL CODIGO SITC CON EL CODIGO INTERNO, SI EL USUARIO PREGUNTA POR UN CODIGO SITC PARTICULAR, DEBER USAR:
                            WHERE cosigo_sitc = {info['codigo_SITC_prod']}
                            Si la pregunta requiere filtrar por producto, DEBES usar:
                            WHERE id_producto = {info['id_prod']}
                            (No uses LIKE ni busques por nombre, usa el ID interno exacto).
                        """
        elif info["tipo"]=="pais":
            contexto = f"""
                            CONTEXTO: El usuario pregunta por el PAÍS: "{info['nombre_pais']}" cuyo ID: {info['id_pais']}).
                            INSTRUCCIÓN OBLIGATORIA: 
                            - Si preguntan sobre IMPORTACIONES de este país -> 'WHERE id_pais_importador = {info['id_pais']}'
                            - Si preguntan sobre EXPORTACIONES de este país -> 'WHERE id_pais_exportador = {info['id_pais']}'
                            - Usa la lógica de la pregunta para decidir cuál columna usar.
                            """
    else:
        contexto = """
                        CONTEXTO :
                        No se detectó un producto o pais específico con suficiente confianza. 
                        Asume que es una pregunta general (Top rankings, sumas totales, comparaciones globales).
                        NO filtres por id_producto o id_pais a menos que el SQL lo requiera explícitamente por lógica.
                    """

    # Armamos el historial como texto
    bloque_historial = "HISTORIAL DE CONVERSACIÓN RECIENTE:\n" + "\n".join(historial)

    user_prompt = f"""
                    {bloque_historial}
                    
                    PREGUNTA ACTUAL: "{pregunta_usuario}"
                    
                    {contexto}
                    
                    Genera solo la consulta SQL.
                """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_promt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
        )
        
        return chat_completion.choices[0].message.content.strip().replace("```sql", "").replace("```", "")
    except Exception as e:
        print(f"Error en Groq (SQL): {e}")
        return None

def generar_respuesta_final(pregunta_usuario,df_sql,info=None):
    """
    Toma la pregunta y los datos crudos (CSV/String) y genera una respuesta amable.
    """
    productos="""- Llantas, gomas, neumaticos nuevos para aeronaves
            -  Motores de piston de combustion interna y sus partes, para aeronaves
             - Helicopteros
             - Aeronaves con un peso sin carga menor a 2000 kg 
             - Aeronaves con un peso sin carga entre 2000 kg a 15000 kg
             - Aeronaves con un peso sin carga mayor a 15000 kg
             - Aeronaves no especificadas en otra parte y equipos asociados
             - Partes,  no especificadas en otra parte, de las aeronaves de la partida 792
            """
    
    system_prompt=f""" 
    
                Actúa como un analista de datos experto en comercio aeroespacial para PyMEs del sector aeroespacial.
                Si hay datos de la busqueda semantica, evaluar si estos tienen relación con la pregunta del usuario, si tienen relación 
                armá la respuesta con estos datos y menciona el nombre del producto o pais según sea el caso. 
                En caso de que no tenga relación, debes mencionar que la información obtenida no concuerda con la pregunta.                
                Pedirle al usuario que vuelva a preguntar utilizando alguno de los productos que hay en la base de datos 
                
                PRODUCTOS DISPONIBLES EN LA BASE DE DATOS: 
                {productos}

                 INSTRUCCIONES:
                1. Responde la pregunta basándote EXCLUSIVAMENTE en los datos de forma profesional.
                2. Sé amable y profesional.
                3. Los valores dados corresponden a USD.
                4. Menciona "Fuente: Atlas de Complejidad Económica (Harvard)".
                5. Si los datos están vacíos, di que no hay registros para esa consulta.
                6. Sé conciso.
                """
    
    
    user_prompt = f"""
        
    PREGUNTA DEL USUARIO: "{pregunta_usuario}"
    
    DATOS OBTENIDOS DE LA BASE DE DATOS:
    {df_sql}
    
    DATOS OBTENIDOS DE LA BUSQUEDA SEMANTICA:
    {info}

    """
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.4,
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error generando respuesta textual: {e}"


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import uvicorn
from busqueda_semantica_productos_paises import BuscadorDeProductos
from sql_llama3_pais_prod import generar_sql_llama3, generar_respuesta_final
from conexion_consultas_db import conectarse

UMBRAL_CONFIANZA = 0.55

app = FastAPI(title="Chatbot PYMES Aeroespacial")

# CORS para que el index.html pueda llamar al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # después lo restringimos si querés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos una sola vez (mejor performance)
buscador = BuscadorDeProductos()

class ChatRequest(BaseModel):
    message: str
    history: list = []  # [{role, content}] desde el front

@app.post("/api/chat")
def chat(req: ChatRequest):
    pregunta = req.message

    # 1) Buscar producto / país
    match_prod, match_pais = buscador.buscar_producto_pais(pregunta)
    info = None

    if max(match_prod["score_prod"], match_pais["score_pais"]) > UMBRAL_CONFIANZA:
        if match_prod["score_prod"] > match_pais["score_pais"]:
            info = match_prod
            info["tipo"] = "producto"
        else:
            info = match_pais
            info["tipo"] = "pais"

    # 2) Transformar history del front al formato que espera tu modelo
    historial_txt = []
    for h in req.history[-12:]:
        role = h.get("role", "")
        content = h.get("content", "")
        if role == "user":
            historial_txt.append(f"Usuario: {content}")
        elif role == "assistant":
            historial_txt.append(f"Asistente: {content}")

    # 3) Generar SQL con Llama
    sql = generar_sql_llama3(pregunta, historial_txt, info)

    # 4) Ejecutar SQL
    datos_sql = "No se encontraron datos."
    preview = []

    conn = conectarse()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            filas = cursor.fetchall()
            cols = [d[0] for d in cursor.description]

            if filas:
                df = pd.DataFrame(filas, columns=cols)
                datos_sql = df.to_string(index=False)
                preview = df.head(10).to_dict(orient="records")
        finally:
            conn.close()
   
    # 5) Respuesta final
    respuesta = generar_respuesta_final(pregunta, datos_sql, info)
    print(sql)
    return {
        "answer": respuesta,
        "sql": sql,
        "preview": preview,
        "sources": ["Fuente: Atlas de Complejidad Económica (Harvard)"],
        "info_semantica": info
    }


if __name__ == "__main__":
    print("Iniciando servidor API...")
    # host "0.0.0.0" permite conexiones externas
    # port 8000 es el estándar de FastAPI
    uvicorn.run(app, host="127.0.0.1", port=8000)
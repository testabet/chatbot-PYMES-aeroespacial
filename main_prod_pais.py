import uvicorn

import pandas as pd
from dotenv import load_dotenv
from collections import deque
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from busqueda_semantica_productos_paises import BuscadorDeProductos
from sql_llama3_pais_prod import generar_sql_llama3, generar_respuesta_final
from conexion_consultas_db import conectarse

load_dotenv()

# ==============================
# CONFIGURACIÓN
# ==============================
UMBRAL_CONFIANZA = 0.55
MAX_HISTORIAL = 3  # turnos
# Guardás 3 entradas por turno (usuario / datos / respuesta)
HIST_MAXLEN = MAX_HISTORIAL * 3

FAKE_USER = "demo@aero"
FAKE_PASS = "Aero123!"
FAKE_TOKEN = "demo-token-123"

# ==============================
# FASTAPI
# ==============================
app = FastAPI(title="Chatbot PYMES Aeroespacial")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, poné tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos una sola vez (mejor performance)
buscador = BuscadorDeProductos()
historial = deque(maxlen=HIST_MAXLEN)

# ==============================
# MODELOS
# ==============================
class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    history: list = []  # lo podés usar en el futuro si querés


# ==============================
# SERVIR FRONT (opcional)
# ==============================
@app.get("/")
def home():
    """
    Si index.html está en la misma carpeta que main.py, esto lo sirve desde FastAPI.
    Útil para Railway/Render (1 sola URL).
    """
    try:
        return FileResponse("index.html")
    except Exception:
        return {"ok": True, "msg": "API running. Abre /docs para ver endpoints."}


# ==============================
# LOGIN FAKE
# ==============================
@app.post("/api/login")
def login(req: LoginRequest):
    if req.username == FAKE_USER and req.password == FAKE_PASS:
        return {
            "token": FAKE_TOKEN,
            "user": {"name": "Usuario Demo", "role": "viewer"},
        }
    raise HTTPException(status_code=401, detail="Credenciales inválidas")


def require_auth(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token faltante")

    token = authorization.split(" ", 1)[1].strip()
    if token != FAKE_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")


# ==============================
# CHATBOT
# ==============================
@app.post("/api/chat")
def chat(req: ChatRequest, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)

    pregunta = (req.message or "").strip()
    if not pregunta:
        raise HTTPException(status_code=400, detail="Message vacío")

    # ==============================
    # BUSQUEDA SEMANTICA
    # ==============================
    match_prod, match_pais = buscador.buscar_producto_pais(pregunta)
    info = None

    try:
        score_prod = float(match_prod.get("score_prod", 0))
        score_pais = float(match_pais.get("score_pais", 0))
    except Exception:
        score_prod, score_pais = 0.0, 0.0

    if max(score_prod, score_pais) > UMBRAL_CONFIANZA:
        if score_prod > score_pais:
            info = match_prod
            info["tipo"] = "producto"
        else:
            info = match_pais
            info["tipo"] = "pais"
    else:
        info = None

    # ==============================
    # GENERAR SQL CON LLM
    # ==============================
    sql = generar_sql_llama3(pregunta, list(historial), info)

    # ==============================
    # EJECUCIÓN SQL
    # ==============================
    datos_sql = "No se encontraron datos."
    conn = conectarse()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            filas = cursor.fetchall()
            cols = [d[0] for d in cursor.description] if cursor.description else []

            if filas and cols:
                df = pd.DataFrame(filas, columns=cols)
                datos_sql = df.to_string(index=False)
            elif filas and not cols:
                # por si la DB no trae description
                datos_sql = str(filas)

        except Exception as e:
            datos_sql = f"Error al ejecutar SQL: {e}"

        finally:
            try:
                conn.close()
            except Exception:
                pass

    # ==============================
    # RESPUESTA FINAL IA
    # ==============================
    respuesta_final = generar_respuesta_final(pregunta, datos_sql, info)

    # ==============================
    # MEMORIA
    # ==============================
    historial.append(f"Usuario: {pregunta}")
    historial.append(f"Asistente (Datos encontrados): {datos_sql}")
    historial.append(f"Respuesta generada: {respuesta_final}")

    # ==============================
    # RESPUESTA API
    # ==============================
    return {
        "answer": respuesta_final,
        "sql": sql,
        "data_preview": datos_sql,
    }

if __name__ == "__main__":
    print("Iniciando servidor API...")
    # host "0.0.0.0" permite conexiones externas
    # port 8000 es el estándar de FastAPI
    uvicorn.run(app, host="127.0.0.1", port=8000)
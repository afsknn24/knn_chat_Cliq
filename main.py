from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, RedirectResponse
from setup import CLAUDE_MODEL, ANTHROPIC_API_KEY
from model_class import Chatbot
from dotenv import set_key
import requests
import os

"""
Inicializamos nuestra API por medio de la creación de una instancia de la clase FastAPI.
También creamos una instancia de la clase Chatbot para utilizar en nuestra API, la cual recibe de parametros el modelo 
de Claude a utilizar y la clave de API de Anthropic.
"""
app = FastAPI()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
refresh_token = os.getenv("REFRESH_TOKEN")
REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"
chat = Chatbot(CLAUDE_MODEL, ANTHROPIC_API_KEY)


# Modelo de respuesta.
class WebHookPayload(BaseModel):
    text:str

# Inicialización para solicitar el token de acceso a Zoho WorkDrive.
@app.get("/auth/start")
async def start_auth():
    auth_url=f"https://accounts.zoho.com/oauth/v2/auth?scope=WorkDrive.files.ALL,ZohoFiles.files.READ&client_id={CLIENT_ID}&response_type=code&access_type=offline&redirect_uri={REDIRECT_URI}&state=register"
    return RedirectResponse(auth_url)


# Redirección general, donde se obtienen los tokens de acceso y refreshtoken.
@app.get("/auth/callback")
async def callback(request: Request):
    global access_token
    code = request.query_params.get("code")
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    payload = {
        "code":code,
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=payload)
    tokens = response.json()
    access_token = tokens["access_token"]
    set_key(".env", "ACCESS_TOKEN", access_token)
    if "refresh_token" in tokens:
        refresh_wd_token = tokens["refresh_token"]
        set_key(".env", "REFRESH_TOKEN", refresh_wd_token)
    return {"tokens": tokens}


# Endpoint para obtener un nuevo token de acceso.
@app.get("/auth/refresh")
async def refresh_token():
    token_url="https://accounts.zoho.com/oauth/v2/token"
    payload = {
        "refresh_token":refresh_token,
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET,
        "grant_type":"refresh_token"
    }
    response = requests.post(token_url, data=payload)
    new_token = response.json()
    return {"new_token": new_token}


# Ruta para obtener la respuesta a una pregunta del Anthropic.
@app.post("/answer")
async def answer(payload:WebHookPayload):
    # Obtenemos la pregunta del payload.
    question=payload.text
    # Obtenemos los documentos de contexto a utilizar en la respuesta.
    context = chat.retrieved_documents(question)
    # Obtenemos la respuesta a la pregunta.
    response = chat.get_response(question, context)
    return JSONResponse(content={"response":response})


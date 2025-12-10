from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.rag import RAG

# Inicializar FastAPI y RAG
app = FastAPI()
rag = RAG()

# Permitir que el frontend (o ngrok) acceda a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Para pruebas locales puedes dejar "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para recibir queries en JSON
class ChatRequest(BaseModel):
    query: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint para subir documentos.
    Convierte el contenido a texto y lo agrega a RAG.
    """
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    result = rag.add_document(text, file.filename)
    return {"status": "ok", "added_document": result}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint de chat.
    Busca en los documentos cargados en RAG y devuelve resultados.
    """
    results = rag.search(request.query)
    return {"query": request.query, "results": results}

@app.get("/health")
async def health():
    """
    Endpoint de salud de la API.
    Devuelve OK si RAG está funcionando.
    """
    try:
        test = rag.search("test", k=1)
        return {"status": "ok", "collections_exist": True}
    except Exception as e:
        return {"status": "error", "message": str(e)}

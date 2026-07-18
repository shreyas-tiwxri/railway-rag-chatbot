from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.db.models import init_db

app = FastAPI(
    title="Railway Documents RAG Chatbot",
    description="Hybrid RAG API over Indian Railways tariff/policy PDFs — "
                 "structured SQL lookups for rate tables + vector search for policy text.",
    version="0.1.0",
)

app.include_router(router)
app.mount("/chat", StaticFiles(directory="static", html=True), name="chat-ui")


@app.on_event("startup")
def on_startup():
    init_db()

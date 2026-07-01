from fastapi import FastAPI

from app.models import ChatRequest, ChatResponse
from app.parser import CatalogParser
from app.retriever import Retriever
from app.chat import ChatController

app = FastAPI(title="SHL Assessment Recommendation Agent")

# ---------- Load everything once at startup ----------

parser = CatalogParser("data/shl_catalog.json")
catalog = parser.load_catalog()

retriever = Retriever(catalog)

chat_controller = ChatController(retriever)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = chat_controller.handle_chat(request.messages)

    return ChatResponse(**result)
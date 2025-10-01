from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio

from src.utils.rag import get_answer_and_docs, async_get_answer_and_docs
from src.utils.pinecone_utils import upload_website_to_pinecone

app = FastAPI(
    title="Fullstack RAG",
    description="A simple RAG API",
    version="0.1.0"
)

# Allow frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://fullstack-rag.netlify.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------
# Request schemas
# -------------------------
class Message(BaseModel):
    message: str

# -------------------------
# Endpoints
# -------------------------

@app.get("/")
def root():
    return {"message": "RAG API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.websocket("/async_chat")
async def async_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            question = await websocket.receive_text()
            async for event in async_get_answer_and_docs(question):
                if event["event_type"] == "done":
                    await websocket.close()
                    return
                else:
                    await websocket.send_text(json.dumps(event))
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()


@app.post("/chat", description="Chat with the RAG API through this endpoint")
async def chat(message: Message):
    try:
        # Add timeout to prevent infinite loading
        response = await asyncio.wait_for(
            asyncio.to_thread(get_answer_and_docs, message.message),
            timeout=120.0  # 2 minutes max
        )
        response_content = {
            "question": message.message,
            "answer": response["answer"],
            "documents": response["context"]
        }
        return JSONResponse(content=response_content, status_code=200)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout - please try a simpler question")
    except Exception as e:
        print(f"Error in /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/indexing", description="Index a website into Pinecone through this endpoint")
async def indexing(url: Message):
    try:
        response = await asyncio.to_thread(upload_website_to_pinecone, url.message)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        print(f"Error in /indexing: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=400)
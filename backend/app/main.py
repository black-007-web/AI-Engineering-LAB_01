from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import users
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.v1 import rag
from app.api.v1 import summarization






app = FastAPI(
    title="AI Engineering Lab",
    description="AI Engineering practice platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)


app.include_router(users.router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(rag.router)
app.include_router(summarization.router)

@app.get("/")
async def root():
    return {
        "project": "AI Engineering Lab",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

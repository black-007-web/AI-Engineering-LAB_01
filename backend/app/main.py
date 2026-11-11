
from fastapi import FastAPI

app = FastAPI(
    title="AI Engineering Lab",
    description="A modular AI Engineering practice platform",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "project": "AI Engineering Lab",
        "status": "running",
        "message": "Welcome to the AI Engineering Lab API"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

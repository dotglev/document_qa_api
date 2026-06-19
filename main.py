from fastapi import FastAPI
from routers import upload, query

app = FastAPI(title="RAG Document Q&A API")

app.include_router(upload.router)
app.include_router(query.router)

@app.get("/")
def home():
    return {"status": "RAG Document Q&A API is running"}
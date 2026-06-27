from fastapi import FastAPI
from routers import upload, query, users
from models.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise RAG Knowledge Intelligence Platform")

app.include_router(upload.router)
app.include_router(query.router)
app.include_router(users.router)

@app.get("/")
def home():
    return {"status": "Enterprise RAG API is running"}
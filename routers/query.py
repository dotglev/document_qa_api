from fastapi import APIRouter, Depends
from pydantic import BaseModel
from routers.auth import verify_api_key
from services.embedder import create_embeddings
from services.vector_store import search_similar_chunks
from services.llm import get_answer

router = APIRouter()

class QueryRequest(BaseModel):
    document_id: str
    question: str

@router.post("/query")
async def query_document(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    question_embedding = create_embeddings([request.question])[0]
    chunks = search_similar_chunks(request.document_id, question_embedding)
    answer = get_answer(request.question, chunks)
    return {
        "question": request.question,
        "answer": answer,
        "source_chunks": chunks
    }
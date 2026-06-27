from fastapi import APIRouter, Depends
from pydantic import BaseModel
from routers.users import get_current_user
from services.embedder import create_embeddings
from services.vector_store import search_with_citations
from services.llm import get_answer_with_citations

router = APIRouter()

class QueryRequest(BaseModel):
    document_id: str
    question: str

@router.post("/query")
async def query_document(
    request: QueryRequest,
    current_user=Depends(get_current_user)
):
    question_embedding = create_embeddings([request.question])[0]
    chunks = search_with_citations(request.document_id, question_embedding)
    result = get_answer_with_citations(request.question, chunks)
    return {
        "question": request.question,
        "answer": result["answer"],
        "citations": result["citations"]
    }
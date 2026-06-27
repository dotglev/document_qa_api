from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from routers.users import get_current_user
from services.vector_store import get_all_chunks
from services.hybrid_search import hybrid_search
from services.llm import get_answer_with_citations

router = APIRouter()

class QueryRequest(BaseModel):
    document_id: str
    question: str
    search_type: str = "hybrid"

@router.post("/query")
async def query_document(
    request: QueryRequest,
    current_user=Depends(get_current_user)
):
    all_chunks = get_all_chunks(request.document_id)
    chunks = hybrid_search(request.document_id, request.question, all_chunks)
    result = get_answer_with_citations(request.question, chunks)
    return {
        "question": request.question,
        "answer": result["answer"],
        "citations": result["citations"],
        "search_type": request.search_type
    }
    
    from fastapi.responses import StreamingResponse

@router.post("/query/stream")
async def query_document_stream(
    request: QueryRequest,
    current_user=Depends(get_current_user)
):
    all_chunks = get_all_chunks(request.document_id)
    chunks = hybrid_search(request.document_id, request.question, all_chunks)
    
    from services.llm import stream_answer
    
    def generate():
        for token in stream_answer(request.question, chunks):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")

@router.post("/query/agent")
async def query_document_agent(
    request: QueryRequest,
    current_user=Depends(get_current_user)
):
    from services.query_agent import agentic_retrieve
    from services.llm import get_answer_with_citations

    result = agentic_retrieve(request.document_id, request.question)
    chunks = result["chunks"]
    answer = get_answer_with_citations(request.question, chunks)

    return {
        "question": request.question,
        "answer": answer["answer"],
        "citations": answer["citations"],
        "agent_plan": result["plan"],
        "sufficient_context": result["sufficient"],
        "total_chunks_searched": result["total_chunks_found"]
    }
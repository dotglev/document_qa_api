import uuid
from fastapi import APIRouter, UploadFile, File, Depends
from routers.auth import verify_api_key
from services.pdf_processor import extract_text_from_pdf
from services.chunker import split_into_chunks
from services.embedder import create_embeddings
from services.vector_store import store_embeddings

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    document_id = str(uuid.uuid4())
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    chunks = split_into_chunks(text)
    embeddings = create_embeddings(chunks)
    store_embeddings(document_id, chunks, embeddings)
    return {
        "document_id": document_id,
        "chunks_processed": len(chunks),
        "status": "success"
    }
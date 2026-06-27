import uuid
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from typing import Optional
from sqlalchemy.orm import Session
from routers.users import get_current_user
from models.database import get_db
from models.user import Document
from services.pdf_processor import extract_text_with_citations
from services.chunker import split_pages_into_chunks
from services.embedder import create_embeddings
from services.vector_store import store_embeddings_with_citations
from services.webhook import send_webhook

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    webhook_url: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document_id = str(uuid.uuid4())
    file_bytes = await file.read()
    pages = extract_text_with_citations(file_bytes)
    chunks = split_pages_into_chunks(pages)
    texts = [c["text"] for c in chunks]
    embeddings = create_embeddings(texts)
    store_embeddings_with_citations(document_id, chunks, embeddings)

    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        document_id=document_id,
        chunk_count=str(len(chunks)),
        status="completed"
    )
    db.add(doc)
    db.commit()

    if webhook_url:
        background_tasks.add_task(send_webhook, webhook_url, document_id, "success")

    return {
        "document_id": document_id,
        "filename": file.filename,
        "chunks_processed": len(chunks),
        "status": "success"
    }

@router.get("/documents")
def get_my_documents(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return {
        "documents": [
            {
                "document_id": d.document_id,
                "filename": d.filename,
                "chunks": d.chunk_count,
                "status": d.status,
                "created_at": d.created_at
            }
            for d in docs
        ]
    }
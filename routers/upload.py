from fastapi import APIRouter, UploadFile, File, Depends
from routers.auth import verify_api_key

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    return {"filename": file.filename, "status": "received"}
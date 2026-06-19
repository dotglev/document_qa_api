from fastapi import APIRouter, Depends
from routers.auth import verify_api_key

router = APIRouter()

@router.post("/query")
async def query_document(
    api_key: str = Depends(verify_api_key)
):
    return {"status": "query endpoint ready"}
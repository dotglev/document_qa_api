from fastapi import Header, HTTPException
from config import OUR_API_KEY

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != OUR_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
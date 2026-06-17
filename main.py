# 1. Import the tools we need from FastAPI
from fastapi import FastAPI, Header, HTTPException

# 2. Import our secret key from the config file we just built
from config import OUR_API_KEY

# 3. Create the actual FastAPI application object
app = FastAPI()

# 4. Create a public route that anyone can visit
@app.get("/")
def home():
    return {"message": "Welcome to the RAG Document QA API!"}

# 5. Create a protected route that requires the API key
@app.get("/protected-data")
def get_protected_data(x_api_key: str = Header(...)):
    
    # The Security Guard Logic:
    if x_api_key != OUR_API_KEY:
        # If the key is wrong, throw a 403 Forbidden error
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # If the key is correct, return the secret data
    return {"data": "This is secret company data. You are authorized!"}
import os
from dotenv import load_dotenv

load_dotenv()

OUR_API_KEY = os.getenv("OUR_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# =============================================================================
# RAG Document Q&A API — Pseudocode Blueprint
# This file is for ME (the developer). It's my personal map.
# Every line is a comment so it runs without errors.
# Run it anytime with: python pseudocode.py
# =============================================================================


# =============================================================================
# DAY 1 — THE FOUNDATION
# Goal: A real FastAPI server running on my machine
# =============================================================================

# --- STEP 1: Project Folder Structure ---
# Create these folders inside RAG-document-qa-api/:
#   routers/      → one file per API endpoint (upload, query, auth)
#   services/     → one file per feature (pdf, chunking, embeddings, etc.)
#   models/       → defines what request/response data looks like
#   ui/           → Streamlit browser interface lives here

# --- STEP 2: Install All Packages ---
# Run this once in the terminal with venv active:
#   pip install fastapi uvicorn python-multipart pymupdf
#               sentence-transformers chromadb
#               requests python-dotenv streamlit httpx
# Then save them to requirements.txt with:
#   pip freeze > requirements.txt

# --- STEP 3: .env File (Secret Keys — never pushed to GitHub) ---
# Create a file called .env in the root folder
# It holds secrets like this (no quotes, no spaces):
#   QWEN_API_KEY=paste-your-qwen-key-here
#   OUR_API_KEY=make-up-a-strong-secret-key-for-clients
#   CHROMA_DB_PATH=./chroma_storage

# --- STEP 4: config.py ---
# This file loads everything from .env so the rest of the app can use it
# Use the python-dotenv library to read the .env file
# Expose the values as variables: QWEN_API_KEY, OUR_API_KEY, CHROMA_DB_PATH

# --- STEP 5: API Key Auth (routers/auth.py) ---
# This protects our API so only people with the right key can use it
# Every request must include a header called X-API-Key
# If the key is missing → return error 401 (Unauthorized)
# If the key is wrong   → return error 403 (Forbidden)
# If the key is correct → let the request through
# It's only ~10 lines of code and impresses every technical client

# --- STEP 6: FastAPI Skeleton (main.py) ---
# Create the FastAPI app object
# Register the routers (upload, query)
# Add a root endpoint GET / that returns {"status": "API is running"}
# Run the server with: uvicorn main:app --reload
# Open browser at localhost:8000 → should see the status message
# Open localhost:8000/docs → FREE interactive API docs (auto-generated!)

# DAY 1 DONE WHEN:
# localhost:8000 is live in the browser
# localhost:8000/docs shows interactive docs


# =============================================================================
# DAY 2 — THE PDF PIPELINE
# Goal: Upload a PDF and have it fully stored in ChromaDB
# =============================================================================

# --- STEP 1: PDF Upload Endpoint (routers/upload.py) ---
# Create endpoint: POST /upload
# It receives a PDF file + an optional webhook_url from the user
# Validate the API key first (using auth.py from Day 1)
# Validate the file is actually a PDF and not too large
# Generate a unique document_id for this PDF (use Python's uuid library)
# Pass the file to the pdf_processor service
# Return the document_id to the user so they can query it later

# --- STEP 2: Extract Text from PDF (services/pdf_processor.py) ---
# Use the PyMuPDF library (imported as fitz)
# Open the PDF file
# Loop through every page
# Extract the raw text from each page
# Join all pages into one big string
# Return the full text

# --- STEP 3: Chunking (services/chunker.py) ---
# We can't send the whole PDF to the AI — it's too long
# Break the full text into overlapping chunks
# chunk_size = 500 characters per chunk
# chunk_overlap = 50 characters shared between neighboring chunks
# Why overlap? So we don't lose context at the edges of chunks
# Return a list of all chunks

# --- STEP 4: Create Embeddings (services/embedder.py) ---
# Load the sentence-transformer model once when the app starts
# Model name: "all-MiniLM-L6-v2" (small, fast, free, no GPU needed)
# For each chunk → run it through the model → get back ~384 numbers
# Those numbers represent the MEANING of that chunk
# Return a list of embeddings (one per chunk)

# --- STEP 5: Store in ChromaDB (services/vector_store.py) ---
# ChromaDB is our local vector database — runs on our machine, completely free
# Connect to ChromaDB on startup
# Create a collection (like a database table) if it doesn't exist
# For each chunk + its embedding:
#   Save to ChromaDB with: unique ID, embedding, original text, document_id
# Also write a search function:
#   Given a question embedding → find the top 5 most similar chunks
#   Return those chunks as text

# DAY 2 DONE WHEN:
# Upload a real PDF via POST /upload
# Check ChromaDB and see the chunks stored inside it


# =============================================================================
# DAY 3 — THE AI BRAIN + WEBHOOKS
# Goal: Ask a question, get a real AI answer using the PDF content
# =============================================================================

# --- STEP 1: Get Qwen API Key ---
# Go to the Qwen API website and sign up for a free account
# Copy the API key and paste it into the .env file as QWEN_API_KEY
# Qwen is the LLM (Large Language Model) that will generate our answers

# --- STEP 2: RAG Query Logic (services/llm.py) ---
# This is the core of the whole project — RAG in action
#
# FUNCTION answer_question(document_id, question):
#
#   Step A — Embed the question
#     Convert the user's question into an embedding
#     Use the same sentence-transformer model from Day 2
#
#   Step B — Search ChromaDB
#     Use the question embedding to search ChromaDB
#     Get back the top 5 most relevant chunks from that document
#
#   Step C — Build the prompt
#     Combine the 5 chunks into a context block
#     Build a prompt that tells Qwen:
#       "Answer ONLY using the context below.
#        If the answer isn't there, say you don't know."
#       Then add the context chunks
#       Then add the user's question
#
#   Step D — Call Qwen API
#     Send the prompt to Qwen via an HTTP POST request
#     Include QWEN_API_KEY in the request header
#     Receive the generated answer back
#
#   Step E — Return the answer
#     Return: the question, the answer, and the source chunks used

# --- STEP 3: Query Endpoint (routers/query.py) ---
# Create endpoint: POST /query
# Validate API key first
# Receive: document_id + question from the user
# Call answer_question() from llm.py
# Return the answer + source chunks to the user

# --- STEP 4: Webhooks (services/webhook.py) ---
# After a PDF finishes processing, notify the user automatically
# If the user included a webhook_url in their upload request:
#   Send an HTTP POST to that URL with this payload:
#     { event: "document.processed", document_id: "...", status: "success" }
#   If it fails → retry up to 3 times
#   If all retries fail → log the failure, don't crash the app
# This is how professional production APIs behave

# DAY 3 DONE WHEN:
# POST /query with a real question returns a real AI answer
# The answer is based on the uploaded PDF content
# Webhook fires and delivers a notification when processing completes


# =============================================================================
# DAY 4 — STREAMLIT UI + POLISH + GITHUB
# Goal: Clean browser UI + professional GitHub presence
# =============================================================================

# --- STEP 1: Streamlit UI (ui/streamlit_app.py) ---
# Streamlit lets us build a browser interface in pure Python
# No HTML, no CSS, no JavaScript needed
#
# PAGE LAYOUT:
#   Title: "RAG Document Q&A"
#   Sidebar: API key input field (stored in session only, never saved)
#
#   Section A — Upload PDF:
#     File uploader widget (PDF only)
#     When user uploads → call POST /upload endpoint
#     Show spinner: "Processing your document..."
#     When done → show success message + document_id
#
#   Section B — Ask a Question:
#     Text input: "Ask a question about your document"
#     Button: "Get Answer"
#     When clicked → call POST /query endpoint
#     Show spinner: "Thinking..."
#     When answer arrives → display it cleanly
#     Also show the source chunks (so client can see where the answer came from)
#
# Run the UI with: streamlit run ui/streamlit_app.py

# --- STEP 2: End to End Testing ---
# Upload a real PDF through the Streamlit UI
# Ask 5 different questions about it
# Confirm the answers are accurate and based on the document
# Test with a wrong API key → confirm it gets rejected
# Test the webhook with a free service like webhook.site

# --- STEP 3: README.md for GitHub ---
# Write a professional README that explains:
#   What the project does (1 paragraph)
#   The tech stack (FastAPI, RAG, ChromaDB, Qwen, Streamlit)
#   How to install and run it locally (step by step)
#   How to use the API (example requests with curl or Python)
#   A screenshot of the Streamlit UI
# This README is what Upwork clients will read

# --- STEP 4: Push Everything to GitHub ---
# Make sure .env is in .gitignore (NEVER push secrets)
# Add all files: git add .
# Commit: git commit -m "Complete RAG Document Q&A API"
# Push: git push origin main

# DAY 4 DONE WHEN:
# Streamlit UI works end to end in the browser
# GitHub repo looks clean and professional
# README explains the project clearly to any client


# =============================================================================
# WHAT THIS PROJECT DEMONSTRATES TO UPWORK CLIENTS
# =============================================================================

print("""
╔══════════════════════════════════════════════════════════════════╗
║           RAG Document Q&A API — Project Overview               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  WHAT IT DOES:                                                   ║
║  A user uploads any PDF document. The system reads it,          ║
║  breaks it into chunks, converts those chunks into              ║
║  embeddings, and stores them in a vector database.              ║
║  When a user asks a question, the system finds the most         ║
║  relevant chunks and sends them to an AI (Qwen) to              ║
║  generate a precise, document-grounded answer.                  ║
║                                                                 ║
║  THE TECH STACK:                                                ║
║  → FastAPI         (REST API framework)                         ║
║  → PyMuPDF         (PDF text extraction)                        ║
║  → sentence-transformers (local embeddings, no GPU)             ║
║  → ChromaDB        (local vector database)                      ║
║  → Qwen API        (LLM for answer generation)                  ║
║  → Webhooks        (async notifications)                        ║
║  → Streamlit       (browser UI for clients)                     ║
║  → API Key Auth    (secure access control)                      ║
║                                                                  ║
║  THE 4-DAY BUILD PLAN:                                          ║
║  Day 1 → FastAPI server running with auth                       ║
║  Day 2 → PDF upload, chunking, embeddings, ChromaDB            ║
║  Day 3 → Qwen RAG query + webhooks                             ║
║  Day 4 → Streamlit UI + testing + GitHub polish                ║
║                                                                  ║
║  SKILLS THIS PROVES TO CLIENTS:                                 ║
║  ✓ RAG (Retrieval-Augmented Generation)                         ║
║  ✓ REST API design with FastAPI                                 ║
║  ✓ Vector databases (ChromaDB)                                  ║
║  ✓ LLM integration (Qwen)                                       ║
║  ✓ Webhook implementation                                       ║
║  ✓ API security (key-based auth)                                ║
║  ✓ Full-stack AI engineering                                    ║
║                                                                  ║
║  STATUS: Blueprint ready. starts NOW.                     ║
╚══════════════════════════════════════════════════════════════════╝
""")
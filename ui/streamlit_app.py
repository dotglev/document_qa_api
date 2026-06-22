import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("RAG Document Q&A")
st.markdown("Upload a PDF and ask questions about it.")

api_key = st.sidebar.text_input("API Key", type="password")

st.header("Step 1 — Upload PDF")
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file and api_key:
    if st.button("Upload & Process"):
        with st.spinner("Processing document..."):
            response = requests.post(
                f"{API_URL}/upload",
                headers={"X-API-Key": api_key},
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state["document_id"] = data["document_id"]
                st.success(f"Done! Chunks processed: {data['chunks_processed']}")
                st.code(f"Document ID: {data['document_id']}")
            else:
                st.error(f"Upload failed: {response.text}")

st.header("Step 2 — Ask a Question")
question = st.text_input("Your question")

if question and api_key and "document_id" in st.session_state:
    if st.button("Get Answer"):
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_URL}/query",
                headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                json={"document_id": st.session_state["document_id"], "question": question}
            )
            if response.status_code == 200:
                data = response.json()
                st.subheader("Answer")
                st.write(data["answer"])
                st.subheader("Source Chunks")
                for chunk in data["source_chunks"]:
                    st.text_area("", chunk, height=100)
            else:
                st.error(f"Query failed: {response.text}")
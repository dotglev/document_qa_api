import requests
from config import GROQ_API_KEY
from services.hybrid_search import hybrid_search
from services.vector_store import get_all_chunks

def reason_across_documents(document_ids: list, question: str) -> dict:
    all_evidence = []

    for doc_id in document_ids:
        try:
            chunks = get_all_chunks(doc_id)
            results = hybrid_search(doc_id, question, chunks, top_n=3)
            for chunk in results:
                chunk["document_id"] = doc_id
                all_evidence.append(chunk)
        except Exception as e:
            continue

    if not all_evidence:
        return {
            "answer": "No relevant information found across the provided documents.",
            "evidence": [],
            "documents_searched": len(document_ids)
        }

    context = ""
    for i, chunk in enumerate(all_evidence):
        context += f"[Document: {chunk['document_id'][:8]}... | Page {chunk['page']}]\n{chunk['text']}\n\n"

    prompt = f"""You are an expert analyst. Answer the question below by reasoning across multiple documents.
Synthesize information from all provided sources.
Clearly indicate when information comes from different documents.
If documents contradict each other, mention it.

Context from multiple documents:
{context}

Question: {question}

Comprehensive Answer:"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
    )

    answer = response.json()["choices"][0]["message"]["content"]

    evidence = [
        {
            "document_id": chunk["document_id"],
            "page": chunk["page"],
            "excerpt": chunk["text"][:200] + "...",
            "relevance_score": chunk.get("relevance_score", 0)
        }
        for chunk in all_evidence
    ]

    return {
        "answer": answer,
        "evidence": evidence,
        "documents_searched": len(document_ids),
        "evidence_pieces": len(all_evidence)
    }
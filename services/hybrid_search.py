from rank_bm25 import BM25Okapi
from services.vector_store import search_with_citations
from services.embedder import create_embeddings

def bm25_search(chunks: list, question: str, top_n: int = 5) -> list:
    texts = [c["text"] for c in chunks]
    tokenized = [text.lower().split() for text in texts]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(question.lower().split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    return [
        {
            "text": chunks[i]["text"],
            "page": chunks[i]["page"],
            "relevance_score": round(float(scores[i]), 3),
            "search_type": "keyword"
        }
        for i in top_indices if scores[i] > 0
    ]

def hybrid_search(document_id: str, question: str, all_chunks: list, top_n: int = 5) -> list:
    question_embedding = create_embeddings([question])[0]
    vector_results = search_with_citations(document_id, question_embedding, top_n)
    for r in vector_results:
        r["search_type"] = "vector"

    bm25_results = bm25_search(all_chunks, question, top_n)

    seen_texts = set()
    combined = []
    for chunk in vector_results + bm25_results:
        if chunk["text"] not in seen_texts:
            seen_texts.add(chunk["text"])
            combined.append(chunk)

    return combined[:top_n]
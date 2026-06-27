import json
import requests
from config import GROQ_API_KEY
from services.hybrid_search import hybrid_search
from services.vector_store import get_all_chunks

def plan_query(question: str) -> dict:
    prompt = f"""You are a query planning agent. Analyze this question and return a JSON plan.

Question: {question}

Return JSON with:
- search_strategy: "broad" or "specific"  
- sub_questions: list of 1-3 sub-questions to search for
- keywords: list of important keywords

Return ONLY valid JSON, no other text."""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
    )
    try:
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except:
        return {
            "search_strategy": "broad",
            "sub_questions": [question],
            "keywords": question.split()[:5]
        }


def evaluate_results(question: str, chunks: list) -> bool:
    if not chunks:
        return False
    context = "\n".join([c["text"][:200] for c in chunks[:3]])
    prompt = f"""Question: {question}

Retrieved context:
{context}

Is this context sufficient to answer the question? Reply with only "YES" or "NO"."""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
    )
    answer = response.json()["choices"][0]["message"]["content"].strip().upper()
    return answer == "YES"


def agentic_retrieve(document_id: str, question: str) -> dict:
    plan = plan_query(question)
    all_chunks = get_all_chunks(document_id)
    all_results = []
    seen_texts = set()

    for sub_question in plan.get("sub_questions", [question]):
        results = hybrid_search(document_id, sub_question, all_chunks, top_n=3)
        for chunk in results:
            if chunk["text"] not in seen_texts:
                seen_texts.add(chunk["text"])
                all_results.append(chunk)

    sufficient = evaluate_results(question, all_results)

    if not sufficient and len(plan.get("keywords", [])) > 0:
        keyword_query = " ".join(plan["keywords"])
        extra_results = hybrid_search(document_id, keyword_query, all_chunks, top_n=3)
        for chunk in extra_results:
            if chunk["text"] not in seen_texts:
                seen_texts.add(chunk["text"])
                all_results.append(chunk)

    return {
        "chunks": all_results[:8],
        "plan": plan,
        "sufficient": sufficient,
        "total_chunks_found": len(all_results)
    }
import chromadb
import uuid

client = chromadb.PersistentClient(path="./chroma_storage")

def get_collection(document_id: str):
    return client.get_or_create_collection(name=document_id)

def store_embeddings(document_id: str, chunks: list, embeddings: list):
    collection = get_collection(document_id)
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks
    )

def store_embeddings_with_citations(document_id: str, chunks: list, embeddings: list):
    collection = get_collection(document_id)
    ids = [str(uuid.uuid4()) for _ in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [{"page": c["page"]} for c in chunks]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

def search_similar_chunks(document_id: str, question_embedding: list, top_n: int = 5) -> list:
    collection = get_collection(document_id)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_n
    )
    return results["documents"][0]

def search_with_citations(document_id: str, question_embedding: list, top_n: int = 5) -> list:
    collection = get_collection(document_id)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_n,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        chunks.append({
            "text": doc,
            "page": metadata.get("page", "unknown"),
            "relevance_score": round(1 - distance, 3)
        })
    return chunks
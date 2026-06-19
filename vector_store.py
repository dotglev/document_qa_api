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

def search_similar_chunks(document_id: str, question_embedding: list, top_n: int = 5) -> list:
    collection = get_collection(document_id)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_n
    )
    return results["documents"][0]
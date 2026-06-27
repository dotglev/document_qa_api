def split_into_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - chunk_overlap
    return chunks

def split_pages_into_chunks(pages: list, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    chunks = []
    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append({
                    "text": chunk,
                    "page": page_num
                })
            start = end - chunk_overlap
    return chunks
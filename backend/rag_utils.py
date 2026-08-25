from sentence_transformers import SentenceTransformer
import chromadb

## Chunking 
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

## Embedding 
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: list[str]):
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings

test_chunks = ["The cat sat on the mat.", "Stock prices rose sharply today."]
result = embed_chunks(test_chunks)
print(len(result), len(result[0]))

## VectorDB
client = chromadb.Client()
collection = client.get_or_create_collection("documents")

def store_chunks(chunks: list[str], embeddings, doc_id: str):
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    collection.add(
        ids=ids,
        embeddings=embeddings,   
        documents=chunks,    
    )

def retrieve_relevant_chunks(query: str, n_results: int = 2) -> list[str]:
    query_embedding = embed_chunks([query])
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    return results["documents"][0]
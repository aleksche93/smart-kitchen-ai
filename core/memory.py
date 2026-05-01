import chromadb

try:
    # Connect to the docker service 'chromadb' on port 8000
    chroma_client = chromadb.HttpClient(host="chromadb", port=8000)
except Exception as e:
    print(f"ChromaDB initialization failed: {e}")
    chroma_client = None

def get_chroma_client():
    return chroma_client

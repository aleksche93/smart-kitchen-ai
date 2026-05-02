import json
import uuid
import chromadb
from chromadb.utils import embedding_functions

try:
    # Connect to the docker service 'chromadb' on port 8000
    chroma_client = chromadb.HttpClient(host="chromadb", port=8000)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    user_traits_col = chroma_client.get_or_create_collection(name="user_traits", embedding_function=ef)
    culinary_sins_col = chroma_client.get_or_create_collection(name="culinary_sins", embedding_function=ef)
except Exception as e:
    print(f"ChromaDB initialization failed: {e}")
    chroma_client = None
    user_traits_col = None
    culinary_sins_col = None

def get_chroma_client():
    return chroma_client

async def extract_and_store_traits(user_message: str, session_id: str):
    """Background task to extract user traits or culinary sins and save to ChromaDB."""
    import os
    from google import genai
    from google.genai import types
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not chroma_client:
        return
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Analyze the following user message from a kitchen assistant chat.
    Does the user explicitly state a dietary preference, allergy, or habit (Trait)?
    Or do they admit to a culinary "sin" (e.g., cooking steak well-done, blending potatoes, eating expired food, etc.)?
    
    User Message: "{user_message}"
    
    Output JSON ONLY in this format:
    {{
        "has_trait": true/false,
        "trait_description": "short description of the trait if true, else null",
        "has_sin": true/false,
        "sin_description": "short description of the sin if true, else null"
    }}
    """
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
        )
        data = json.loads(response.text)
        
        doc_id = str(uuid.uuid4())
        metadata = {"session_id": session_id, "source": "chat"}
        
        if data.get("has_trait") and data.get("trait_description"):
            if user_traits_col:
                user_traits_col.add(documents=[data["trait_description"]], metadatas=[metadata], ids=[doc_id + "-trait"])
            
        if data.get("has_sin") and data.get("sin_description"):
            if culinary_sins_col:
                culinary_sins_col.add(documents=[data["sin_description"]], metadatas=[metadata], ids=[doc_id + "-sin"])
            
    except Exception as e:
        print(f"LTM Extraction failed: {e}")

class UserChefMemoryGraph:
    """Placeholder for future User-Chef Knowledge Graph."""
    def __init__(self):
        self.nodes = {}
        self.edges = []
        
    def add_user_node(self, user_id: str, metadata: dict):
        self.nodes[user_id] = {"type": "user", "metadata": metadata}
        
    def add_chef_interaction(self, user_id: str, interaction_type: str, details: dict):
        edge = {"source": user_id, "target": "Chef", "relation": interaction_type, "details": details}
        self.edges.append(edge)

# Global instance for future use
memory_graph = UserChefMemoryGraph()

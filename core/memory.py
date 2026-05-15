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
    flavor_bible_col = chroma_client.get_or_create_collection(name="flavor_bible", embedding_function=ef)
except Exception as e:
    print(f"ChromaDB initialization failed: {e}")
    chroma_client = None
    user_traits_col = None
    culinary_sins_col = None
    flavor_bible_col = None

def get_chroma_client():
    return chroma_client

async def extract_and_store_traits(session_id: str, chat_history: list):
    """Background task to extract user traits and store them in the Graph Memory (SQLite)."""
    import os
    import json
    from google import genai
    from google.genai import types
    from db.database import async_session
    from db.models import GraphMemoryModel
    from sqlalchemy import select
    from core.graph_manager import UserChefMemoryGraph
    import logging
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return
        
    client = genai.Client(api_key=api_key)
    
    # Analyze the chat history
    history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
    
    prompt = f"""
    Analyze the following chat history. Identify ANY user traits, preferences, or relationships between the user and ingredients/recipes.
    
    Chat History:
    {history_text}
    
    Output JSON ONLY in this format:
    {{
        "nodes": [
            {{"id": "User", "type": "UserPreference", "attributes": {{"name": "ChefUser"}}}},
            {{"id": "Garlic", "type": "Ingredient", "attributes": {{"category": "Vegetable"}}}}
        ],
        "edges": [
            {{"source": "User", "target": "Garlic", "relationship": "DISLIKES"}}
        ]
    }}
    Return empty lists if nothing is found.
    """
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
        )
        
        if not response or not response.text:
            logging.warning("Graph Trait Extraction: Empty response from LLM")
            return
            
        data = json.loads(response.text)
        
        # Defensive check for extraction result
        if not data or not isinstance(data, dict):
            logging.warning(f"Graph Trait Extraction: Invalid JSON structure: {data}")
            return
            
        async with async_session() as session:
            # 1. Load existing graph or init new
            q = await session.execute(
                select(GraphMemoryModel).where(GraphMemoryModel.session_id == session_id)
            )
            graph_model = q.scalars().first()
            
            graph_manager = UserChefMemoryGraph()
            if graph_model and graph_model.graph_data:
                graph_manager.deserialize(graph_model.graph_data)
            
            # 2. Add new nodes/edges
            for node in data.get("nodes", []):
                graph_manager.add_node(
                    node_type=node.get("type", "Unknown"), 
                    node_id=node.get("id"), 
                    attributes=node.get("attributes", {})
                )
            for edge in data.get("edges", []):
                graph_manager.add_edge(
                    node_id_1=edge.get("source"),
                    node_id_2=edge.get("target"),
                    relationship=edge.get("relationship", "RELATED_TO")
                )
                
            # 3. Serialize and save back
            if not graph_model:
                graph_model = GraphMemoryModel(session_id=session_id)
                session.add(graph_model)
                
            graph_model.graph_data = graph_manager.serialize()
            await session.commit()
            
    except Exception as e:
        logging.error(f"Graph Trait Extraction failed: {e}")

import chromadb
from chromadb.utils import embedding_functions
import numpy as np

try:
    # Use internal docker host
    chroma_client = chromadb.HttpClient(host="chromadb", port=8000)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    flavor_col = chroma_client.get_collection(name="flavor_bible", embedding_function=ef)
except Exception:
    chroma_client = None
    flavor_col = None

def get_harmony_score(ingredients: list[str]) -> float:
    """
    Calculates the Harmony Score for a list of ingredients.
    Score ranges from 1.0 (Chaos) to 4.0 (Divine).
    """
    if not flavor_col or not ingredients or len(ingredients) < 2:
        return 2.5 # Neutral fallback

    total_score = 0.0
    pairs_checked = 0

    try:
        # Batch search for pairings for all ingredients
        results = flavor_col.query(
            query_texts=ingredients,
            n_results=5
        )
        
        for i, ing in enumerate(ingredients):
            for j, other_ing in enumerate(ingredients[i+1:]):
                found_match = any(other_ing.lower() in doc.lower() for doc in results['documents'][i])
                if found_match:
                    total_score += 1.0
                else:
                    dist = results['distances'][i][0] if results['distances'] and results['distances'][i] else 1.0
                    total_score += max(0, 1.0 - dist)
                pairs_checked += 1
    except:
        pass

    if pairs_checked == 0:
        return 2.5
        
    avg_harmony = (total_score / pairs_checked) * 3.0 + 1.0 # Map to 1.0 - 4.0
    return round(min(4.0, max(1.0, avg_harmony)), 2)

def get_pairing_tips(ingredients: list[str]) -> list[str]:
    """Suggests 1-2 items that could enhance the dish."""
    if not flavor_col or not ingredients:
        return []
        
    tips = []
    try:
        # Search pairings for the main ingredient (usually the first one)
        results = flavor_col.query(
            query_texts=[ingredients[0]],
            n_results=3
        )
        for doc in results['documents'][0]:
            # Extract the partner name from "Item pairs well with Partner"
            if "pairs well with" in doc:
                partner = doc.split("pairs well with")[1].strip()
                if partner.lower() not in [ing.lower() for ing in ingredients]:
                    tips.append(partner)
                    if len(tips) >= 2: break
    except:
        pass
    return tips

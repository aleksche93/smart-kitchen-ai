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

    # Check pairs (simplified: check each ingredient against others)
    for i, ing in enumerate(ingredients):
        try:
            # Search for pairings for this ingredient
            results = flavor_col.query(
                query_texts=[ing],
                n_results=5
            )
            
            # Check if any of the other ingredients are in the results
            for other_ing in ingredients[i+1:]:
                # If the other ingredient appears in the matched "pairings" documents
                found_match = any(other_ing.lower() in doc.lower() for doc in results['documents'][0])
                if found_match:
                    total_score += 1.0 # High harmony
                else:
                    # Check distance as a fallback for harmony
                    # Closer distance = more harmonic context
                    dist = results['distances'][0][0] if results['distances'] else 1.0
                    total_score += max(0, 1.0 - dist)
                
                pairs_checked += 1
        except:
            continue

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

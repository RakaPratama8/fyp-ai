from sentence_transformers import SentenceTransformer  # type: ignore
import numpy as np

print("Loading model. This might take a moment on first run...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.")

def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given string."""
    vector = model.encode(text)
    return vector.tolist()

def extract_highlighted_sentence(query: str, abstract: str) -> str:
    """
    Splits the abstract into sentences, embeds each, and finds the one 
    most semantically similar to the query. Returns the abstract with the 
    best sentence wrapped in <mark> tags.
    """
    if not abstract:
        return ""
        
    query_emb = model.encode(query)
    
    sentences = [s.strip() + "." for s in abstract.split(".") if len(s.strip()) > 5]
    if not sentences:
        return abstract

    sentence_embs = model.encode(sentences)
    
    similarities = model.similarity(query_emb, sentence_embs)[0]
    best_idx = int(np.argmax(similarities))
    
    best_sentence = sentences[best_idx]
    
    highlighted_abstract = abstract.replace(
        best_sentence[:-1], 
        f"<mark>{best_sentence[:-1]}</mark>"
    )
    
    return highlighted_abstract

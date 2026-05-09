from sentence_transformers import SentenceTransformer  # type: ignore
import numpy as np
import re

print("Loading model. This might take a moment on first run...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.")

def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a given string."""
    vector = model.encode(text)
    return vector.tolist()

def extract_highlighted_sentence(query: str, abstract: str) -> str:
    """
    Splits the abstract into sentences and finds the one with the highest 
    keyword overlap to the query. Fast, CPU-friendly, and requires 0 ML inference.
    """
    if not abstract:
        return ""
        
    # Extract lowercase words from the query
    query_terms = set(re.findall(r'\w+', query.lower()))
    if not query_terms:
        return abstract

    raw_sentences = abstract.split('.')
    best_sentence = ""
    max_overlap = -1

    for raw_s in raw_sentences:
        s = raw_s.strip()
        if len(s) < 10:  # Skip empty or very short fragments
            continue

        # Extract words from the sentence
        sentence_terms = set(re.findall(r'\w+', s.lower()))
        overlap = len(query_terms.intersection(sentence_terms))

        if overlap > max_overlap:
            max_overlap = overlap
            best_sentence = s

    # If we found a matching sentence, highlight it
    if best_sentence and max_overlap > 0:
        highlighted_abstract = abstract.replace(best_sentence, f"<mark>{best_sentence}</mark>")
        return highlighted_abstract
    
    # Fallback if no direct keyword overlap is found
    return abstract

import requests
import re
from typing import List, Dict

POLITE_POOL_EMAIL = "admin@fypaper.com"
BASE_URL = "https://api.openalex.org/works"

def fetch_papers(query: str, min_year: int, max_results: int = 10) -> List[Dict]:
    """
    Queries the OpenAlex API for papers matching the text query.
    Filters by publication year and parses the inverted abstract back to plain text.
    """
    params = {
        "search": query,
        "filter": f"publication_year:>{min_year - 1},has_abstract:true",
        "per-page": max_results,
        "mailto": POLITE_POOL_EMAIL,
        "sort": "relevance_score:desc"
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    for work in data.get("results", []):
        openalex_id = work.get("id")
        title = work.get("title")
        doi = work.get("doi")
        publication_year = work.get("publication_year")
        
        authors = [a.get("author", {}).get("display_name") for a in work.get("authorships", [])]
        
        # OpenAlex returns an inverted index for abstracts instead of plain text. We must rebuild it.
        abstract_inverted = work.get("abstract_inverted_index", {})
        abstract_text = _rebuild_abstract(abstract_inverted)
        
        if abstract_text and title:
            results.append({
                "openalex_id": openalex_id,
                "title": title,
                "doi": doi,
                "abstract": abstract_text,
                "publication_year": publication_year,
                "authors": authors
            })
            
    return results

def _rebuild_abstract(inverted_index: Dict[str, List[int]]) -> str:
    if not inverted_index:
        return ""
        
    max_idx = max([idx for positions in inverted_index.values() for idx in positions])
    words = [""] * (max_idx + 1)
    
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
            
    return " ".join(words)

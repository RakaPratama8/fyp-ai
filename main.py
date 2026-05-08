from fastapi import FastAPI, HTTPException  # type: ignore
from pydantic import BaseModel
from typing import List, Optional

from database import get_connection, init_db
from embedding import get_embedding, extract_highlighted_sentence
from openalex import fetch_papers

app = FastAPI(title="FYP AI Service")

@app.on_event("startup")
def on_startup():
    init_db()

class SearchRequest(BaseModel):
    text: str
    min_year: int = 2021
    top_k: int = 10

class SearchResult(BaseModel):
    id: str
    title: str
    doi: Optional[str]
    authors: List[str]
    publication_year: int
    abstract: str
    highlighted_abstract: str
    similarity_score: float

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/internals/semantic-search", response_model=List[SearchResult])
def semantic_search(req: SearchRequest):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        papers = fetch_papers(req.text, req.min_year, req.top_k)
        
        for p in papers:
            cur.execute("SELECT openalex_id FROM papers WHERE openalex_id = %s", (p['openalex_id'],))
            if cur.fetchone() is None:
                emb = get_embedding(p['title'] + ". " + p['abstract'])
                authors_str = ", ".join(p['authors'] if p['authors'] else [])
                
                cur.execute("""
                    INSERT INTO papers (openalex_id, title, doi, abstract, publication_year, authors, author_names, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (p['openalex_id'], p['title'], p['doi'], p['abstract'], p['publication_year'], p['authors'], authors_str, emb))
        conn.commit()
        
        query_emb = get_embedding(req.text)
        
        cur.execute("""
            SELECT openalex_id, title, doi, abstract, publication_year, author_names, 1 - (embedding <=> %s::vector) AS similarity
            FROM papers
            WHERE publication_year >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_emb, req.min_year, query_emb, req.top_k))
        
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            oid, title, doi, abstract, year, author_names, sim = row
            
            # 4. Highlight the most matching sentence in the abstract
            highlighted = extract_highlighted_sentence(req.text, abstract)
            
            results.append(SearchResult(
                id=oid,
                title=title,
                doi=doi,
                authors=[a.strip() for a in author_names.split(",")] if author_names else [],
                publication_year=year,
                abstract=abstract,
                highlighted_abstract=highlighted,
                similarity_score=round(float(sim), 4)
            ))
            
        cur.close()
        return results

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

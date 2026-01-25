"""Returns a the result of the query being run against the database.
"""
from db_manager import DatabaseManager
from processors import embed_text

def search_query(query: str):
    vec = embed_text(query)
    db_manager = DatabaseManager()
    results = db_manager.query_embeddings(vec, top_k=500)
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")
    
    # Group the most occuring articles in the top results
    article_score: dict[str, float] = {}
    schedule_score: dict[str, float] = {}
    for res in results:
        if res.article is not None:
            article_score.setdefault(res.article, 0)
            article_score[res.article] += res.similarity_score if res.similarity_score else 0.0
        
        if res.schedule is not None:
            schedule_score.setdefault(res.schedule, 0)
            schedule_score[res.schedule] += res.similarity_score if res.similarity_score else 0.0
        
    print("Top Articles in Results:", sorted(article_score.items(), key=lambda x: x[1], reverse=True)[:5])
    print("Top Schedules in Results:", sorted(schedule_score.items(), key=lambda x: x[1], reverse=True)[:5])
    
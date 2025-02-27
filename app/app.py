from fastapi import FastAPI, Query
from query import list_articles, query_rag

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the RAG API"}

@app.get("/articles/")
def get_articles():
    """API endpoint to list available articles."""
    articles = list_articles()
    return {"articles": articles}

@app.get("/query/")
def query(
    query_text: str = Query(..., description="Query text for the RAG system"),
    article_title: str = Query(None, description="Title of the article to search within (optional)")
):
    """API endpoint to process queries using RAG."""
    response = query_rag(query_text, article_title)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

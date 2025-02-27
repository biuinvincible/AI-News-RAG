import os
import json
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
from together import Together
from dotenv import load_dotenv
from utils.get_embedding_function import get_embedding_function
from utils.get_ipv4_ip import get_windows_ip

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Lấy thư mục gốc của project
DATA_FILE = os.path.join(BASE_DIR, "news_crawler", "vnexpress_articles.json")
CHROMA_PATH = "chroma"
OLLAMA_URL = os.getenv("OLLAMA_HOST", f"http://{get_windows_ip()}:11434")

# API key
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

# Load Re-Ranking Model
RERANKER_MODEL = CrossEncoder("BAAI/bge-reranker-large")

# Load articles data
with open(DATA_FILE, "r", encoding="utf-8") as file:
    articles_data = json.load(file)

# Prompt template
PROMPT_TEMPLATE = """
You are an AI assistant with access to AI news articles.
Use ONLY the following context to answer the question, but it has to be adequate and relevant.
If the Question is not recognized as a question, it seems to be an article or something similar. In that case, try to summarize the article based on the context with as much information as possible.
Context:

{context}

If the answer is not in the context, reply: "I don't have enough information."

---

Question: {question}
Answer:
"""

def list_articles():
    """Returns a list of available articles."""
    articles = []
    for metadata in articles_data:
        if metadata:
            title = metadata.get("title_en", "Không có tiêu đề")
            date = metadata.get("date", "Không rõ ngày")
            content = metadata.get("content_en", "Không có nội dung")  
            articles.append({"title": title, "date": date, "content": content})
    return articles

def query_rag(query_text: str, article_title: str = None):
    """Processes the query using RAG and returns the response."""
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Perform vector search
    if article_title:
        vector_results = db.similarity_search_with_score(query_text, k=10, filter={"title": article_title})
    else:
        vector_results = db.similarity_search_with_score(query_text, k=10)

    # Perform BM25 Search
    all_documents = [doc.page_content for doc, _ in vector_results]
    tokenized_corpus = [doc.split() for doc in all_documents]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query_text.split())
    bm25_results = sorted(zip(vector_results, bm25_scores), key=lambda x: x[1], reverse=True)[:5]

    # Combine results
    combined_results = vector_results + [doc[0] for doc in bm25_results]
    if not combined_results:
        return "❌ Không tìm thấy nội dung phù hợp."

    # Re-Ranking
    rerank_input = [(query_text, doc.page_content) for doc, _ in combined_results]
    rerank_scores = RERANKER_MODEL.predict(rerank_input)
    ranked_results = sorted(zip(combined_results, rerank_scores), key=lambda x: x[1], reverse=True)

    # Keep Top-3 results
    final_results = [doc[0] for doc in ranked_results[:10]]

    # Generate response
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in final_results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    client = Together(api_key=together_api_key)
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = response.choices[0].message.content

    sources = [doc.metadata.get("id", "Unknown") for doc, _ in final_results]
    return {"response": response_text, "sources": sources}

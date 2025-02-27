from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
import os

def get_embedding_function():
    load_dotenv()
    ollama_host = os.getenv("OLLAMA_HOST")
    print("🛠️ Initializing embedding function...")
    return OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_host)

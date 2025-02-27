import argparse
import os
import shutil
import json
import requests
import chromadb
import unicodedata
import nltk
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from utils.get_embedding_function import get_embedding_function
from utils.get_ipv4_ip import get_windows_ip
from langchain_chroma import Chroma  
nltk.download('punkt')  # Dùng để chia theo câu nếu cần
CHROMA_PATH = "chroma"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Lấy thư mục gốc của project
DATA_FILE = os.path.join(BASE_DIR, "news_crawler", "vnexpress_articles.json")
OLLAMA_URL = f"http://{get_windows_ip()}:11434/api/tags"
print(f"🔗 Connecting to Ollama at: {OLLAMA_URL}")

def main():
    """Main function to load, process, and store AI news articles in ChromaDB."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database...")
        clear_database()

    if not check_ollama():
        print("❌ Ollama is not running! Start it with `ollama serve` and retry.")
        return

    if not os.path.exists(DATA_FILE):
        print("⚠️ No JSON data file found! Please provide `vnexpress_articles.json`.")
        return

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def check_ollama():
    """Check if Ollama is running before processing embeddings."""
    try:
        response = requests.get(OLLAMA_URL, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def clean_text(text):
    """Loại bỏ ký tự không hợp lệ, surrogate characters, khoảng trắng thừa."""
    if not isinstance(text, str):
        return ""

    cleaned_text = ''.join(c for c in text if unicodedata.category(c) != 'Cs')  # Loại bỏ ký tự lỗi
    cleaned_text = unicodedata.normalize("NFKC", cleaned_text)  # Chuẩn hóa Unicode
    cleaned_text = cleaned_text.encode("utf-8", "ignore").decode("utf-8")  # Mã hóa UTF-8
    cleaned_text = " ".join(cleaned_text.split())  # Xóa khoảng trắng thừa

    return cleaned_text


def load_documents():
    """Load AI-related news articles from JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    documents = []
    for article in articles:
        cleaned_content = clean_text(article.get("content_en", ""))
        cleaned_description = clean_text(article.get("description_en", ""))
        cleaned_title = clean_text(article.get("title_en", ""))
        cleaned_url = clean_text(article.get("url", ""))
        cleaned_date = clean_text(article.get("date", ""))

        if not cleaned_content:
            continue  # Bỏ qua bài viết rỗng

        # Nối description vào content
        combined_content = f"{cleaned_description}\n\n{cleaned_content}"

        metadata = {
            "title": cleaned_title,
            "url": cleaned_url,
            "date": cleaned_date,
        }

        documents.append(Document(page_content=combined_content, metadata=metadata))

    print(f"✅ Loaded {len(documents)} articles after cleaning.")
    return documents


def split_by_paragraphs(text):
    """Chia văn bản theo đoạn văn (paragraph)."""
    paragraphs = text.split("\n\n")  # Chia theo dấu xuống dòng kép
    return [p.strip() for p in paragraphs if len(p.strip()) > 100]  # Loại bỏ đoạn quá ngắn


def split_by_sentences(text, max_sentences=6):
    """Chia văn bản thành chunk theo từng câu."""
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = [" ".join(sentences[i:i + max_sentences]) for i in range(0, len(sentences), max_sentences)]
    return chunks


def split_documents(documents: list[Document], method="recursive"):
    """Split articles into smaller chunks using different strategies."""
    split_chunks = []

    for doc in documents:
        text = doc.page_content

        if method == "recursive":
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=150,
                length_function=len,
                is_separator_regex=False,
            )
            chunks = text_splitter.split_text(text)

        elif method == "paragraph":
            chunks = split_by_paragraphs(text)

        elif method == "sentence":
            chunks = split_by_sentences(text, max_sentences=6)

        else:
            raise ValueError("Invalid chunking method. Use 'recursive', 'paragraph', or 'sentence'.")

        for chunk in chunks:
            split_chunks.append(Document(page_content=chunk, metadata=doc.metadata))

    print(f"✅ {len(split_chunks)} chunks generated using {method} splitting.")
    return split_chunks


def add_to_chroma(chunks: list[Document]):
    """Add document chunks to ChromaDB with Ollama embeddings."""
    print("🔍 Initializing ChromaDB...")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())

    # Tạo ID cho từng chunk
    chunks_with_ids = calculate_chunk_ids(chunks)
    print(f"📌 Generated {len(chunks_with_ids)} chunks with unique IDs.")

    # Lấy danh sách ID hiện tại trong database
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"📊 Number of existing documents in DB: {len(existing_ids)}")

    # Chỉ thêm các chunk chưa có trong database
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        print(f"👉 Adding {len(new_chunks)} new documents...")
        
        # Debug nội dung chunks mới
        for chunk in new_chunks[:5]:  # In thử 5 chunk đầu
            print(f"📌 Chunk ID: {chunk.metadata['id']}, Content: {chunk.page_content[:100]}...")

        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

        # Thêm dữ liệu vào database
        db.add_documents(new_chunks, ids=new_chunk_ids)

        # Tạo lại kết nối với database để đảm bảo cập nhật thành công
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
        print("✅ Database updated successfully!")

        # Kiểm tra lại embeddings
        docs = db.get(include=['embeddings'])
        print(f"🔍 Retrieved {len(docs['ids'])} documents from ChromaDB.")

        # Debug 5 embeddings đầu tiên
        for i in range(min(5, len(docs['ids']))):
            emb = docs['embeddings'][i]
            if emb is None:
                print(f"❌ Embedding for doc {docs['ids'][i]} is None!")
            else:
                print(f"✅ Embedding for doc {docs['ids'][i]}: {emb[:5]}... (truncated)")

    else:
        print("✅ No new documents to add.")

def calculate_chunk_ids(chunks):
    """Generate unique IDs for document chunks based on URL and chunk index."""
    last_url_id = None
    current_chunk_index = 0

    for chunk in chunks:
        url = chunk.metadata.get("url", "unknown")
        current_url_id = url  

        if current_url_id == last_url_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk.metadata["id"] = f"{current_url_id}:{current_chunk_index}"
        last_url_id = current_url_id

    return chunks


def clear_database():
    """Delete the existing ChromaDB folder."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print("🗑️ Database cleared successfully!")


if __name__ == "__main__":
    main()

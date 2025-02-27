# VnExpress AI RAG Chatbot

## Giới thiệu
Dự án này thu thập các bài báo AI từ VnExpress, sau đó xây dựng hệ thống chatbot sử dụng phương pháp Retrieval-Augmented Generation (RAG). Chatbot có thể truy vấn dữ liệu từ các bài báo và trả lời câu hỏi dựa trên nội dung thu thập được.

---
## Hướng dẫn cài đặt và chạy dự án

### 1. Cài đặt và chạy Ollama
Dự án sử dụng Ollama để phục vụ mô hình embedding.

#### a) Cài đặt Ollama và tải mô hình
```sh
ollama pull nomic-embed-text
```

#### b) Chạy Ollama
Nếu Ollama đã chạy trước đó, dừng nó bằng lệnh:
```sh
taskkill /IM ollama.exe /F
```
Sau đó, thiết lập host và khởi chạy:
```sh
set OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

#### c) Kiểm tra địa chỉ host của Ollama
Chạy lệnh sau để xem địa chỉ IPv4 của máy:
```sh
powershell.exe "ipconfig | findstr IPv4"
```
Thường là dòng đầu tiên trong kết quả.

---
### 2. Thiết lập biến môi trường

#### a) Đăng ký API Key của Together AI tại [together.ai](https://www.together.ai/)

#### b) Tạo file `.env` trong thư mục `app/`
Nội dung file `.env`:
```sh
TOGETHER_API_KEY="your_api_key"
OLLAMA_HOST="ollama_host"
```
Thay `your_api_key` bằng API key đã đăng ký, `ollama_host` bằng địa chỉ host từ bước (1c).

---
### 3. Chạy API FastAPI
Di chuyển vào thư mục `app/` và khởi động API:
```sh
cd app
uvicorn app:app --host localhost --port 8000 --reload
```

---
### 4. Chạy giao diện với Streamlit
Di chuyển vào thư mục `streamlit/` và chạy ứng dụng:
```sh
cd streamlit
streamlit run streamlit_app.py
```

---
### 5. Cập nhật tin tức vào cơ sở dữ liệu

#### a) Thu thập danh sách URL bài báo
Di chuyển vào thư mục `news_crawler/` và chạy:
```sh
cd news_crawler
python url_crawler.py <số trang bắt đầu> <số trang kết thúc>
```
Ví dụ để thu thập từ trang 1 đến 10:
```sh
python url_crawler.py 1 10
```

#### b) Thu thập nội dung bài báo
```sh
python content_crawler.py
```

#### c) Đưa dữ liệu vào cơ sở dữ liệu
Di chuyển vào thư mục `app/` và chạy:
```sh
cd ..
cd app
python populate_database.py
```
Nếu muốn xóa dữ liệu cũ trước khi cập nhật mới, chạy:
```sh
python populate_database.py --reset
```

---
## Ghi chú
- Đảm bảo bạn đã cài đặt đầy đủ các thư viện cần thiết trước khi chạy dự án bằng cách chạy:
  ```sh
  pip install -r requirements.txt
  ```
- Nếu gặp lỗi, hãy kiểm tra lại `.env` và đảm bảo các service đang chạy đúng cách.

---
## Liên hệ
Nếu bạn có bất kỳ câu hỏi nào, hãy liên hệ qua email hoặc GitHub Issues của dự án.


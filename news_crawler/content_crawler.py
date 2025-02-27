from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import json
import re
from helper_functions import configure_driver
from deep_translator import GoogleTranslator

# Khởi tạo Google Translate API
translator = GoogleTranslator(source="auto", target="en")

# Danh sách từ viết tắt cần thay thế
abbreviation_dict = {
    "AI": "Trí tuệ nhân tạo",
    "IoT": "Internet vạn vật",
    "ML": "Học máy",
    "NLP": "Xử lí ngôn ngữ tự nhiên"
}

def replace_abbreviations(text):
    if not text:
        return ""
    for abbr, full_form in abbreviation_dict.items():
        text = re.sub(rf'\b{abbr}\b', full_form, text, flags=re.IGNORECASE)
    return text

# File lưu dữ liệu JSON
output_file = "vnexpress_articles.json"

# Đọc dữ liệu cũ để tránh crawl trùng
try:
    with open(output_file, "r", encoding="utf-8") as file:
        articles = json.load(file)
        crawled_urls = {article["url"] for article in articles}  # Tạo set để kiểm tra nhanh
except (FileNotFoundError, json.JSONDecodeError):
    articles = []
    crawled_urls = set()

# Đọc danh sách URL từ file CSV
input_file = "vnexpress_links.csv"
urls = []
with open(input_file, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Bỏ qua header
    urls = [row[0] for row in reader if row[0] not in crawled_urls]  # Lọc bỏ URL đã crawl

if not urls:
    print("✅ Tất cả các URL đã được crawl. Không có gì mới để thu thập.")
    exit()

# Khởi tạo Selenium WebDriver
driver = configure_driver()

def wait_for_page_load(driver, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        state = driver.execute_script("return document.readyState")
        if state == "complete":
            return True
        time.sleep(1)
    print("⚠️ Cảnh báo: Trang chưa tải hoàn toàn sau thời gian chờ!")
    return False

def translate_content(content):
    if not content:
        return ""
    content = replace_abbreviations(content)
    paragraphs = content.split('\n')
    translated_paragraphs = [translator.translate(p.strip()) for p in paragraphs if p.strip()]
    return '\n'.join(translated_paragraphs)

# Bắt đầu crawl từng URL
for url in urls:
    try: 
        driver.get(url)
        if not wait_for_page_load(driver):
            print(f"⏳ Trang {url} có thể chưa tải hoàn toàn!")
            continue
    except Exception as e:
        print(f"Time out khi tải {url}, lỗi: {e}")
        continue
    
    try:
        title = driver.find_element(By.CLASS_NAME, "title-detail").text.strip()
        description = driver.find_element(By.CLASS_NAME, "description").text.strip()
        content = driver.find_element(By.CLASS_NAME, "fck_detail").text.strip()
        date = driver.find_element(By.CLASS_NAME, "date").text.strip()
        
        # Thay thế từ viết tắt và dịch
        title, description, content = map(replace_abbreviations, [title, description, content])
        title_en, description_en, content_en = map(translator.translate, [title, description, translate_content(content)])
        
        article = {
            "url": url,
            "title": title,
            "title_en": title_en,
            "description": description,
            "description_en": description_en,
            "content": content,
            "content_en": content_en,
            "date": date
        }
        
        articles.append(article)
        
        # Ghi dữ liệu vào file JSON sau mỗi bài viết
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(articles, file, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã thu thập và lưu: {url}")
    
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu từ {url}: {e}")

# Đóng trình duyệt
driver.quit()
print(f"🎯 Đã hoàn thành crawl và lưu vào {output_file}")
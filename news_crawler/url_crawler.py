import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import os
from helper_functions import configure_driver

# Lấy phạm vi trang từ tham số dòng lệnh
start_page = int(sys.argv[1])
end_page = int(sys.argv[2])

# Khởi tạo trình duyệt
driver = configure_driver()

# Tập hợp các link đã lấy
hrefs = set()

# Lặp qua các trang
temp = len(hrefs)
for i in range(start_page, end_page + 1):
    url = f"https://vnexpress.net/cong-nghe/ai-p{i}" if i > 1 else "https://vnexpress.net/cong-nghe/ai"
    driver.get(url)
    time.sleep(3)  # Đợi 2 giây trước khi dừng tải
    driver.execute_script("window.stop();")  # Dừng tải trang

    # Tìm tất cả các thẻ <a> có thuộc tính data-medium và href
    links = driver.find_elements(By.XPATH, "//a[@data-medium and @href]")
    
    # Lưu danh sách các đường dẫn (chỉ lấy link kết thúc bằng ".html")
    hrefs.update(link.get_attribute("href") for link in links if link.get_attribute("href").endswith(".html"))
    
    if temp == len(hrefs):
        print("✅ Đã thu thập đủ link. Kết thúc...")
        break
    temp = len(hrefs)
    print(hrefs)

# Đóng trình duyệt
driver.quit()

# In ra màn hình
for href in sorted(hrefs):
    print(href)

# Lưu vào file CSV
output_file = "vnexpress_links.csv"
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["URL"])
    for href in sorted(hrefs):
        writer.writerow([href])

print(f"📌 Đã lưu {len(hrefs)} link hợp lệ vào {output_file}")

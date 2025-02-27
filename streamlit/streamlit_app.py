import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("VNExpress AI RAG")

query_text = st.text_input("Nhập truy vấn:")
if st.button("Gửi"):
    query_params = {"query_text": query_text}
    response = requests.get(f"{API_BASE_URL}/query/", params=query_params)
    
    if response.status_code == 200:
        answer = response.json()
        st.subheader("Trả lời:")
        st.write(answer)
    else:
        st.error("Không thể lấy câu trả lời từ API!")

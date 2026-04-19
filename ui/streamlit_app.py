import streamlit as st
import requests
import os


# This looks for the 'BACKEND_URL' Render just created
# It falls back to 'backend' so it STILL works on your local laptop!
raw_host = os.getenv("BACKEND_URL", "backend:8000")

# Make sure it's a full URL
backend_url = f"http://{raw_host}" if not raw_host.startswith("http") else raw_host

st.title("📄 Chat with Your Documents")

query = st.text_input("Ask a question:")

if st.button("Ask") and query:
    response = requests.get(
        f"{backend_url}/ask_llm_agent?query=" + query
    )

    data = response.json()

    st.write("### 🤖 Answer")
    st.write(data["answer"])
    
    if "sources" in data:
        st.write("### 📚 Sources")
        for s in data["sources"]:
            st.write("-", s)

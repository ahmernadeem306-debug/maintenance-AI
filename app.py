import streamlit as st
import os
import tempfile
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="PDF Chat with Gemini")
st.title("PDF Chat - Maintenance AI")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
for m in genai.list_models:
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)


        



if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

with st.sidebar:
    st.header("Upload PDF")
    pdf = st.file_uploader("PDF upload karo", type="pdf")
    if pdf:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(pdf.read())
            pdf_path = tmp.name
        
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        st.session_state.pdf_text = text
        os.remove(pdf_path)
        st.success("PDF Loaded! Ab sawaal poocho.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("PDF se sawaal poocho"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.pdf_text == "":
            response = "Pehle PDF upload karo bhai."
        else:
            full_prompt = f"Is PDF content ke basis pe jawab do:\n\nPDF:\n{st.session_state.pdf_text[:30000]}\n\nSawal: {prompt}"
            response = model.generate_content(full_prompt).text
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

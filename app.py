import streamlit as st
import os
from google import genai
from pypdf import PdfReader

st.set_page_config(page_title="PDF Chat with Gemini")
st.title("PDF Chat - Maintenance AI")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)
model_name = 'gemini-2.0-flash'

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    st.success("PDF Loaded! Ab sawaal poocho")
    
    user_question = st.text_input("PDF se sawaal poocho:")
    
    if user_question:
        # Yahan full_prompt banaya hai - ye missing tha
        full_prompt = f"""
        Neeche diye gaye PDF ke context se jawab do. Agar jawab PDF mein na ho to keh do "PDF mein ye maloomat nahi hai".
        
        PDF Context:
        {text}
        
        Sawal: {user_question}
        """
        
        with st.spinner("Jawab tayar ho raha hai..."):
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            st.write(response.text)
   

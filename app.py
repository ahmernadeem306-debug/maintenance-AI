import streamlit as st
from google import genai
from pypdf import PdfReader

st.set_page_config(page_title="Maintenance AI")
st.title("Machine Maintenance Extractor ")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)
model_name = 'gemini-flash-latest'

uploaded_file = st.file_uploader("Upload Machine Maintenance PDF", type="pdf")

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    st.success("PDF Successfully Loaded!")
    
    if st.button("Extract Maintenance Points"):
        with st.spinner("Extracting key maintenance procedures..."):
            
            # Yahan prompt badal diya - ab English mein de ga
            full_prompt = f"""
            You are a professional maintenance engineer. Analyze the following machine manual text.
            
            Your task:
            1. Extract only maintenance-related procedures and checks
            2. Present them in clear, professional English
            3. Use bullet points and categorize by frequency
            4. Keep it concise and actionable. No extra explanation
            5. Focus on: daily checks, weekly tasks, monthly procedures, lubrication, safety protocols, cleaning
            6. If no maintenance info is found, state: "No maintenance procedures found in this document"

            Manual Text:
            {text}
            
            Use this exact format:
            
            **Daily Maintenance**
            - Inspect and clean steps and comb plates before operation
            - Ensure floor area around escalator is clear of obstructions
            - Verify comb plate teeth are not broken or bent
            - Check handrail condition and synchronization with steps
            
            **Weekly Maintenance**
            - [Point 1]
            
            **Monthly Maintenance**
            - [Point 1]
            
            **Safety Critical Checks**
            - [Point 1]
            """
            
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                st.subheader("Key Maintenance Procedures ")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Check your API key quota or try again in a few minutes.")
    

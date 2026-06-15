import streamlit as st
from google import genai
from pypdf import PdfReader

st.set_page_config(page_title="Maintenance AI")
st.title("Machine Maintenance Extractor 🔧")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)
model_name = 'gemini-flash-latest'  # Ye model free mein sabse stable hai

uploaded_file = st.file_uploader("Machine ki Maintenance PDF Upload Karo", type="pdf")

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    st.success("PDF Read Ho Gayi!")
    
    if st.button("Maintenance Points Nikalo"):
        with st.spinner("Important maintenance points nikal raha hoon..."):
            
            # Yahan prompt change kar diya - ab sawal nahi pooche ga
            full_prompt = f"""
            Tum ek maintenance expert ho. Neeche machine ki manual/maintenance file ka text hai.
            
            Tumhara kaam:
            1. Sirf maintenance se related important points nikalo
            2. Har point ko short aur easy Urdu ya Roman Urdu mein likho
            3. Bullets mein de do
            4. Faltu detail mat do. Sirf kaam ki baat: daily, weekly, monthly checks, lubrication, safety, cleaning
            5. Agar PDF mein maintenance na ho to keh do "Is PDF mein maintenance ki details nahi hain"

            PDF ka Text:
            {text}
            
            Output ka format ye ho:
            **Daily Maintenance:**
            - Point 1
            - Point 2
            
            **Weekly Maintenance:**
            - Point 1
            
            **Important Safety:**
            - Point 1
            """
            
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                st.subheader("Maintenance Ke Important Points 👇")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Error aa gaya bhai: {e}")
                st.info("Ho sakta hai API key expire ho ya quota khatam. Nayi key bana le Google AI Studio se.")

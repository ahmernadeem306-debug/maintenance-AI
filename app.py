import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import tempfile

st.set_page_config(page_title="MaintenoBot AI", page_icon="⚡")
st.title("⚡ MaintenoBot AI - Industrial PM Extractor")
st.caption("⚠️ Safety First: Follow LOTO. Use PPE. Verify with supervisor before execution.")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

@st.cache_resource
def load_pdf_and_create_db(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = FAISS.from_texts([chunk.page_content for chunk in chunks], embeddings)
    return vector_db

st.subheader("Upload Maintenance Manual PDF")
uploaded_pdf = st.file_uploader("Upload any equipment manual - Motor, Dyeing, Cable Tray, Boiler", type="pdf")

if uploaded_pdf:
    with st.spinner("Analyzing PDF and extracting maintenance data..."):
        vector_db = load_pdf_and_create_db(uploaded_pdf)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY, temperature=0)
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_db.as_retriever())

    st.success("PDF Processed Successfully.")

    task_type = st.radio(
        "Select Maintenance Type",
        ["Monthly PM Procedure", "Annual Overhaul Procedure", "Troubleshooting Guide"],
        horizontal=True
    )

    if st.button("Generate Professional Procedure ⚡", type="primary"):
        
        prompt = f"""
        You are a senior industrial maintenance engineer writing a standard operating procedure.
        
        Task: Extract the COMPLETE maintenance procedure for "{task_type}" from the uploaded manual.
        
        STRICT OUTPUT RULES:
        1. Language: Professional Industrial English Only. No Urdu.
        2. First line: "Equipment: [Exact name and model from manual]"
        3. Second line: "⚠️ Safety Critical: [One line safety instruction]"
        4. Then write "Procedure:" and list steps 1, 2, 3...
        5. Maximum 10 steps total. Each step = One line only, maximum 15 words.
        6. Use industrial verbs: Verify, Inspect, Record, Test, Clean, Tighten, Measure.
        7. Include frequency at end of each step: - Daily, - Weekly, - Monthly, - Quarterly, - Annually.
        8. Cover full cycle: Isolation, Inspection, Testing, Recording, Restoration.
        9. No explanations, no theory, no paragraphs. Only executable actions.
        10. If no maintenance procedure found: Reply "No maintenance procedure found in this document"
        
        Example Output:
        Equipment: Cable Tray System - Hot Dip Galvanized HDG-300
        ⚠️ Safety Critical: Implement LOTO, obtain height work permit, use full PPE
        Procedure:
        1. Isolate power supply and apply LOTO tags - Before start
        2. Conduct visual inspection for physical damage - Monthly
        3. Verify tightness of all nuts and bolts - Monthly
        4. Inspect for rust or corrosion at joints - Quarterly
        5. Clean dust and debris to prevent fire hazard - Monthly
        6. Test earthing continuity resistance below 1 ohm - Annually
        7. Verify cable loading within design capacity - Annually
        8. Record all defects and actions in maintenance log - After completion
        9. Remove tools and restore work area cleanliness - End
        10. Remove LOTO with supervisor verification and energize - End
        """

        with st.spinner("Generating industrial-grade procedure..."):
            result = qa_chain.run(prompt)

        st.subheader("Professional Maintenance Procedure:")
        st.code(result, language="text")
        
        st.download_button(
            label="Download SOP as TXT",
            data=result,
            file_name="PM_SOP_Short.txt",
            mime="text/plain"
        )
        st.success("💡 This SOP is ready for site use. Print and attach to equipment.")

else:
    st.info("👆 Upload a maintenance manual or SOP PDF to begin")
    st.markdown("""
    **What This Tool Does:**
    1. Auto-detects equipment name from PDF
    2. Extracts complete PM procedure in 8-10 lines
    3. Outputs in professional industrial English format
    4. Ready for direct use by technicians
    
    **Compatible PDFs:** OEM Manuals, Company SOPs, IEEE Standards, IOM Documents
    """)

st.markdown("---")
st.caption("RAG-Powered | Auto Equipment Detection | Industrial Standard Output")

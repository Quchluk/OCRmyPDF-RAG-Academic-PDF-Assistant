import os
import streamlit as st
import tempfile
import subprocess
import fitz  # PyMuPDF
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
assert openai_api_key, "❌ OPENAI_API_KEY not found in environment variables"

# Streamlit UI
st.title("📄 OCRmyPDF + RAG Academic PDF Assistant")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        input_pdf_path = tmp_file.name

    # Check for existing text in PDF
    st.info("🔍 Checking if the PDF already contains text...")
    doc_check = fitz.open(input_pdf_path)
    has_text = any(page.get_text().strip() for page in doc_check)
    doc_check.close()

    if has_text:
        st.warning("⚠️ The PDF already contains text. OCR is not required.")
        output_pdf_path = input_pdf_path
    else:
        # OCR processing
        output_pdf_path = input_pdf_path.replace(".pdf", "_ocr.pdf")
        st.success("✅ PDF uploaded. Running OCRmyPDF...")
        try:
            subprocess.run(["ocrmypdf", input_pdf_path, output_pdf_path], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"❌ OCR failed: {e}")
            st.stop()
        st.success("✅ OCR completed. Extracting text...")

    # Extract text from PDF
    doc = fitz.open(output_pdf_path)
    docs = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text and text.strip():
            docs.append(Document(page_content=text, metadata={"page": i+1}))
    doc.close()

    if not docs:
        st.error("❌ No text found in the PDF.")
        st.stop()

    st.success(f"✅ Pages extracted: {len(docs)}")

    # Split text into chunks
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500 * 5,  # ~500 words × ~5 characters per word
        chunk_overlap=100 * 5,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = text_splitter.split_documents(docs)

    # Embed and index
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # RAG setup
    llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0.0)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="map_reduce"
    )

    query = st.text_input("Enter your question:")

    if query:
        with st.spinner("🔎 Retrieving and generating exact quotes..."):
            retrieved_docs = retriever.get_relevant_documents(query)
            joined_docs = "\n\n".join(doc.page_content for doc in retrieved_docs)

            prompt = f'''
You are an academic assistant helping a researcher analyze a document.

The user has asked the following question:
"{query}"

Below are extracted passages from the document. Your task is to select up to **three exact quotations** from these passages that directly answer or relate to the user's question.

✳️ Each quotation must be:
- Verbatim (copied exactly from the input text)
- Brief (1–3 sentences)
- Relevant to the user's query

Do not explain or paraphrase anything. Just return a list of quotes, one per line, optionally with a page number in parentheses if identifiable.

--- BEGIN TEXT ---
{joined_docs}
--- END TEXT ---
'''

            response = llm.invoke(prompt)

        st.markdown("### ✅ Exact Quotes:")
        st.write(response)

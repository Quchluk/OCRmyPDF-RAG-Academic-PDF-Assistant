# 📄 OCRmyPDF + RAG PDF Assistant

This Streamlit app lets you upload a scanned or digital PDF and interact with it using a Retrieval-Augmented Generation (RAG) pipeline.
It uses OCRmyPDF for text extraction, FAISS for semantic search, and OpenAI's GPT for answering questions.

---

## ✅ Features
- 📥 Upload any PDF (scanned or digital)
- 🔎 Automatically runs OCR (if needed) using `ocrmypdf`
- 🧠 By deafult chunks text into ~500-word segments with 100-word overlap
- 🧬 Embeds text using `OpenAIEmbeddings`
- 🗂 Creates a per-document FAISS vector index
- 🤖 Uses GPT (via LangChain) to answer user questions
- 📚 Displays page-specific citations
- ✨ Highlights the most relevant section inside each chunk based on query-word overlap

---

## 🚀 Usage
1. Clone the repo
2. Install dependencies:
```bash
pip install -r requirements.txt
brew install tesseract ghostscript  # for OCRmyPDF
```
3. Add `.env` file with your OpenAI key:
```env
OPENAI_API_KEY=sk-...
```
4. Run the app:
```bash
streamlit run app.py
```

---

### 📦 System dependencies (required for OCR):
```bash
brew install tesseract ghostscript
```

---

## 🧠 Example use cases
- Academic reading assistant 
- Searchable interface for scanned historical documents
- Lightweight Q&A assistant for any PDF

---

## ✍️ Author
Anton Smirnov — [github.com/Quchluk](https://github.com/Quchluk)

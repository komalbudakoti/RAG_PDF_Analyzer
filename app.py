from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_groq import ChatGroq
import os
import tempfile
from pathlib import Path

import streamlit as st

# 1. Load the keys from Streamlit secrets
api_key = st.secrets["GROQ_API_KEY"]
# Global variable to store the current QA chain
qa_chain = None

# =========================
# LOAD + PROCESS DOCUMENTS
# =========================
def load_rag_from_file(file_path):
    """Load and process a PDF file into a RAG chain"""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)

    embedding = HuggingFaceEmbeddings()
    db = FAISS.from_documents(chunks, embedding)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    llm = ChatGroq(model_name="llama-3.1-8b-instant")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    return qa

def process_uploaded_file(uploaded_file):
    """Process an uploaded file and return the QA chain"""
    global qa_chain
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_path = tmp_file.name
    
    try:
        # Load and process the file
        qa_chain = load_rag_from_file(tmp_path)
        return True, "Document loaded successfully!"
    except Exception as e:
        return False, f"Error loading document: {str(e)}"
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass

# =========================
# QUERY FUNCTION
# =========================
def ask_question(query):
    """Ask a question using the loaded QA chain"""
    if qa_chain is None:
        return "Please upload a document first."
    
    try:
        response = qa_chain.run(query)
        return response
    except Exception as e:
        return f"Error processing query: {str(e)}"
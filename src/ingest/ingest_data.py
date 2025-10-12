"""
Módulo: ingest_data.py
Descripción: Carga documentos institucionales del colegio, limpia texto y los divide en fragmentos (chunks).
Autor: Tania Herrera
Fecha: Octubre 2025
"""

import os
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_documents(path="data/docs"):
    loader = DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    return splitter.split_documents(documents)

if __name__ == "__main__":
    docs = load_documents()
    chunks = split_documents(docs)
    print(f"Documentos procesados: {len(chunks)} fragmentos generados.")
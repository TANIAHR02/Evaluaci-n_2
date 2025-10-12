"""
FASE 5 – Pipeline RAG (IE3 y IE4)
Módulo: rag_pipeline.py
Descripción: Pipeline completo RAG para SchoolBot - carga documentos, genera embeddings y almacena en base vectorial
Autor: Tania Herrera
Fecha: Octubre 2025
"""

import os
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA

def load_documents(path="data/docs"):
    """Carga documentos del directorio especificado"""
    loader = DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

def split_documents(documents):
    """Divide documentos en fragmentos (chunks)"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    return splitter.split_documents(documents)

def create_embeddings():
    """Crea embeddings usando HuggingFace"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    return embeddings

def create_vectorstore(chunks, embeddings, persist_directory="data/vector_db"):
    """Crea y persiste la base de datos vectorial"""
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vectorstore

def create_qa_chain(vectorstore):
    """Crea cadena de pregunta-respuesta con RAG"""
    llm = Ollama(model="mistral:7b")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
    )
    return qa_chain

def setup_rag_pipeline():
    """Configura el pipeline RAG completo"""
    print("Iniciando pipeline RAG para SchoolBot...")
    
    # 1. Cargar documentos
    print("1. Cargando documentos...")
    documents = load_documents()
    print(f"   Documentos cargados: {len(documents)}")
    
    # 2. Dividir en chunks
    print("2. Dividiendo documentos en fragmentos...")
    chunks = split_documents(documents)
    print(f"   Fragmentos generados: {len(chunks)}")
    
    # 3. Crear embeddings
    print("3. Generando embeddings...")
    embeddings = create_embeddings()
    print("   Embeddings creados")
    
    # 4. Crear base de datos vectorial
    print("4. Creando base de datos vectorial...")
    vectorstore = create_vectorstore(chunks, embeddings)
    print("   Base de datos vectorial creada")
    
    # 5. Crear cadena QA
    print("5. Configurando cadena de pregunta-respuesta...")
    qa_chain = create_qa_chain(vectorstore)
    print("   Cadena QA configurada")
    
    print("✅ Pipeline RAG configurado exitosamente!")
    return qa_chain

def query_schoolbot(question, qa_chain):
    """Realiza una consulta al SchoolBot"""
    response = qa_chain.run(question)
    return response

if __name__ == "__main__":
    # Configurar pipeline
    qa_chain = setup_rag_pipeline()
    
    # Ejemplo de consulta
    question = "¿Cuáles son los horarios de clases del colegio?"
    print(f"\nPregunta: {question}")
    answer = query_schoolbot(question, qa_chain)
    print(f"Respuesta: {answer}")

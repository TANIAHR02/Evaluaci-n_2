"""
SchoolBot - Asistente Inteligente Escolar
Módulo de Generación de Embeddings

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo se encarga de generar embeddings vectoriales para los documentos
procesados, utilizando modelos de sentence-transformers optimizados para
contenido en español y el contexto educativo.
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pickle
import json
from datetime import datetime

# Dependencias para embeddings
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModel

# Dependencias para base de datos vectorial
import chromadb
from chromadb.config import Settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Clase principal para la generación de embeddings vectoriales.
    
    Esta clase maneja la generación de embeddings usando modelos de
    sentence-transformers, optimizados para contenido educativo en español.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Inicializa el generador de embeddings.
        
        Args:
            model_name (str): Nombre del modelo de sentence-transformers a usar
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_dim = 384  # Dimensión del modelo por defecto
        
        logger.info(f"EmbeddingGenerator inicializado con modelo: {model_name}")
        logger.info(f"Dispositivo utilizado: {self.device}")
    
    def load_model(self):
        """
        Carga el modelo de sentence-transformers.
        """
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Modelo cargado exitosamente. Dimensión: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Error cargando modelo: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Genera un embedding para un texto dado.
        
        Args:
            text (str): Texto para generar embedding
            
        Returns:
            np.ndarray: Vector embedding normalizado
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Generar embedding
            embedding = self.model.encode(text, convert_to_tensor=True)
            
            # Normalizar el embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            # Convertir a numpy array
            embedding = embedding.cpu().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Genera embeddings para una lista de textos en lotes.
        
        Args:
            texts (List[str]): Lista de textos para procesar
            batch_size (int): Tamaño del lote para procesamiento
            
        Returns:
            List[np.ndarray]: Lista de embeddings generados
        """
        if self.model is None:
            self.load_model()
        
        try:
            embeddings = []
            
            # Procesar en lotes para eficiencia
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_tensor=True,
                    show_progress_bar=True
                )
                
                # Normalizar embeddings
                batch_embeddings = batch_embeddings / torch.norm(batch_embeddings, dim=1, keepdim=True)
                
                # Convertir a numpy y agregar a la lista
                embeddings.extend(batch_embeddings.cpu().numpy())
                
                logger.info(f"Procesado lote {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            logger.info(f"Generados {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generando embeddings en lote: {str(e)}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesa el texto antes de generar embeddings.
        
        Args:
            text (str): Texto a preprocesar
            
        Returns:
            str: Texto preprocesado
        """
        # Limpiar texto básico
        text = text.strip()
        
        # Remover caracteres de control
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Normalizar espacios
        text = ' '.join(text.split())
        
        # Truncar si es muy largo (límite del modelo)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        return text

class VectorDatabase:
    """
    Clase para manejar la base de datos vectorial ChromaDB.
    
    Esta clase proporciona una interfaz para almacenar y consultar
    embeddings en la base de datos vectorial.
    """
    
    def __init__(self, persist_directory: str = "data/vector_db"):
        """
        Inicializa la base de datos vectorial.
        
        Args:
            persist_directory (str): Directorio para persistir la base de datos
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        # Crear directorio si no existe
        os.makedirs(persist_directory, exist_ok=True)
        
        logger.info(f"VectorDatabase inicializada en: {persist_directory}")
    
    def initialize(self):
        """
        Inicializa la conexión con ChromaDB.
        """
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Crear o obtener colección
            self.collection = self.client.get_or_create_collection(
                name="school_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("Conexión con ChromaDB establecida")
            
        except Exception as e:
            logger.error(f"Error inicializando ChromaDB: {str(e)}")
            raise
    
    def store_embeddings(self, chunks: List[Dict[str, Any]], embeddings: List[np.ndarray]):
        """
        Almacena chunks con sus embeddings en la base de datos.
        
        Args:
            chunks (List[Dict[str, Any]]): Lista de chunks con metadatos
            embeddings (List[np.ndarray]): Lista de embeddings correspondientes
        """
        if self.collection is None:
            self.initialize()
        
        try:
            # Preparar datos para ChromaDB
            ids = [chunk['id'] for chunk in chunks]
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # Convertir embeddings a lista de listas
            embedding_list = [embedding.tolist() for embedding in embeddings]
            
            # Almacenar en ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embedding_list,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Almacenados {len(chunks)} chunks en la base de datos vectorial")
            
        except Exception as e:
            logger.error(f"Error almacenando embeddings: {str(e)}")
            raise
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 5, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca documentos similares a un embedding de consulta.
        
        Args:
            query_embedding (np.ndarray): Embedding de la consulta
            top_k (int): Número de resultados a retornar
            filters (Optional[Dict[str, Any]]): Filtros de metadatos
            
        Returns:
            List[Dict[str, Any]]: Lista de documentos similares
        """
        if self.collection is None:
            self.initialize()
        
        try:
            # Realizar búsqueda
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=filters
            )
            
            # Formatear resultados
            similar_docs = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                }
                similar_docs.append(doc)
            
            logger.info(f"Encontrados {len(similar_docs)} documentos similares")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error en búsqueda similar: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección.
        
        Returns:
            Dict[str, Any]: Estadísticas de la colección
        """
        if self.collection is None:
            self.initialize()
        
        try:
            count = self.collection.count()
            
            # Obtener metadatos de algunos documentos para análisis
            sample_results = self.collection.get(limit=100)
            
            # Analizar tipos de documentos
            doc_types = {}
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas']:
                    doc_type = metadata.get('document_type', 'unknown')
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            stats = {
                'total_documents': count,
                'document_types': doc_types,
                'last_updated': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {'error': str(e)}

class EmbeddingPipeline:
    """
    Pipeline completo para la generación y almacenamiento de embeddings.
    
    Esta clase coordina todo el proceso de generación de embeddings,
    desde el procesamiento de chunks hasta su almacenamiento en la base de datos.
    """
    
    def __init__(self, vector_db_path: str = "data/vector_db"):
        """
        Inicializa el pipeline de embeddings.
        
        Args:
            vector_db_path (str): Ruta a la base de datos vectorial
        """
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = VectorDatabase(vector_db_path)
        
        logger.info("EmbeddingPipeline inicializado")
    
    def process_chunks(self, chunks: List[Dict[str, Any]]) -> Tuple[List[np.ndarray], List[Dict[str, Any]]]:
        """
        Procesa una lista de chunks generando sus embeddings.
        
        Args:
            chunks (List[Dict[str, Any]]): Lista de chunks a procesar
            
        Returns:
            Tuple[List[np.ndarray], List[Dict[str, Any]]]: Embeddings y chunks procesados
        """
        try:
            # Preprocesar textos
            texts = [self.embedding_generator.preprocess_text(chunk['text']) for chunk in chunks]
            
            # Generar embeddings
            embeddings = self.embedding_generator.generate_embeddings_batch(texts)
            
            # Agregar información de embedding a los chunks
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunk = chunk.copy()
                processed_chunk['embedding_dimension'] = len(embeddings[i])
                processed_chunk['processed_at'] = datetime.now().isoformat()
                processed_chunks.append(processed_chunk)
            
            logger.info(f"Procesados {len(chunks)} chunks con embeddings")
            return embeddings, processed_chunks
            
        except Exception as e:
            logger.error(f"Error procesando chunks: {str(e)}")
            raise
    
    def store_in_database(self, chunks: List[Dict[str, Any]], embeddings: List[np.ndarray]):
        """
        Almacena chunks y embeddings en la base de datos vectorial.
        
        Args:
            chunks (List[Dict[str, Any]]): Chunks procesados
            embeddings (List[np.ndarray]): Embeddings correspondientes
        """
        try:
            self.vector_db.store_embeddings(chunks, embeddings)
            logger.info("Chunks y embeddings almacenados en la base de datos")
            
        except Exception as e:
            logger.error(f"Error almacenando en base de datos: {str(e)}")
            raise
    
    def search_documents(self, query: str, top_k: int = 5, 
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca documentos similares a una consulta.
        
        Args:
            query (str): Consulta de búsqueda
            top_k (int): Número de resultados
            filters (Optional[Dict[str, Any]]): Filtros de metadatos
            
        Returns:
            List[Dict[str, Any]]: Documentos similares encontrados
        """
        try:
            # Generar embedding para la consulta
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Buscar en la base de datos
            results = self.vector_db.search_similar(query_embedding, top_k, filters)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda de documentos: {str(e)}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la base de datos vectorial.
        
        Returns:
            Dict[str, Any]: Estadísticas de la base de datos
        """
        return self.vector_db.get_collection_stats()

# Función principal para ejecutar el pipeline
def main():
    """
    Función principal para ejecutar el pipeline de embeddings.
    """
    # Inicializar pipeline
    pipeline = EmbeddingPipeline()
    
    # Ejemplo de uso
    try:
        # Obtener estadísticas de la base de datos
        stats = pipeline.get_database_stats()
        print("Estadísticas de la base de datos vectorial:")
        print(json.dumps(stats, indent=2))
        
        # Ejemplo de búsqueda
        query = "¿Cuáles son los horarios de clases?"
        results = pipeline.search_documents(query, top_k=3)
        
        print(f"\nResultados para la consulta: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['metadata'].get('file_name', 'Unknown')}")
            print(f"   Distancia: {result['distance']:.4f}")
            print(f"   Texto: {result['text'][:100]}...")
            print()
            
    except Exception as e:
        logger.error(f"Error en el pipeline principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()



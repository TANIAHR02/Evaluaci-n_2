"""
SchoolBot - Asistente Inteligente Escolar
Módulo de Retrieval y Búsqueda Semántica

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo implementa el sistema de retrieval semántico que permite
encontrar información relevante en los documentos del colegio basándose
en consultas en lenguaje natural.
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
import re

# Dependencias para búsqueda semántica
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Dependencias para base de datos vectorial
import chromadb
from chromadb.config import Settings

# Dependencias para procesamiento de texto
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticRetriever:
    """
    Clase principal para la búsqueda semántica en documentos escolares.
    
    Esta clase implementa un sistema de retrieval híbrido que combina
    búsqueda semántica con re-ranking para obtener los resultados más relevantes.
    """
    
    def __init__(self, vector_db_path: str = "data/vector_db", 
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Inicializa el retriever semántico.
        
        Args:
            vector_db_path (str): Ruta a la base de datos vectorial
            embedding_model (str): Modelo para generar embeddings
            rerank_model (str): Modelo para re-ranking de resultados
        """
        self.vector_db_path = vector_db_path
        self.embedding_model_name = embedding_model
        self.rerank_model_name = rerank_model
        
        # Inicializar modelos
        self.embedding_model = None
        self.rerank_model = None
        self.vector_db = None
        
        # Configuración
        self.similarity_threshold = 0.7
        self.max_results = 10
        self.rerank_top_k = 20
        
        # Inicializar recursos de NLTK
        self._setup_nltk()
        
        logger.info("SemanticRetriever inicializado")
    
    def _setup_nltk(self):
        """
        Configura recursos de NLTK necesarios.
        """
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('spanish'))
    
    def initialize_models(self):
        """
        Inicializa los modelos de embedding y re-ranking.
        """
        try:
            # Cargar modelo de embeddings
            self.embedding_model = SentenceTransformer(
                self.embedding_model_name,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            # Cargar modelo de re-ranking
            self.rerank_model = CrossEncoder(self.rerank_model_name)
            
            logger.info("Modelos inicializados correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando modelos: {str(e)}")
            raise
    
    def initialize_vector_db(self):
        """
        Inicializa la conexión con la base de datos vectorial.
        """
        try:
            self.vector_db = chromadb.PersistentClient(
                path=self.vector_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.vector_db.get_collection("school_documents")
            
            logger.info("Conexión con base de datos vectorial establecida")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos vectorial: {str(e)}")
            raise
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocesa la consulta para mejorar la búsqueda.
        
        Args:
            query (str): Consulta original
            
        Returns:
            str: Consulta preprocesada
        """
        # Limpiar y normalizar
        query = query.strip().lower()
        
        # Remover caracteres especiales pero mantener acentos
        query = re.sub(r'[^\w\sáéíóúüñÁÉÍÓÚÜÑ]', ' ', query)
        
        # Normalizar espacios
        query = ' '.join(query.split())
        
        # Expandir abreviaciones comunes
        abbreviations = {
            'horarios': 'horario de clases',
            'fechas': 'fecha de evaluaciones',
            'notas': 'calificaciones',
            'reglamento': 'reglamento escolar',
            'calendario': 'calendario académico'
        }
        
        for abbr, full in abbreviations.items():
            query = query.replace(abbr, full)
        
        return query
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Genera embedding para una consulta.
        
        Args:
            query (str): Consulta de búsqueda
            
        Returns:
            np.ndarray: Embedding de la consulta
        """
        if self.embedding_model is None:
            self.initialize_models()
        
        try:
            # Preprocesar consulta
            processed_query = self.preprocess_query(query)
            
            # Generar embedding
            embedding = self.embedding_model.encode(processed_query, convert_to_tensor=True)
            
            # Normalizar
            embedding = embedding / torch.norm(embedding)
            
            return embedding.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Error generando embedding de consulta: {str(e)}")
            raise
    
    def search_similar_documents(self, query_embedding: np.ndarray, 
                                top_k: int = 20, 
                                filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca documentos similares en la base de datos vectorial.
        
        Args:
            query_embedding (np.ndarray): Embedding de la consulta
            top_k (int): Número de documentos a recuperar
            filters (Optional[Dict[str, Any]]): Filtros de metadatos
            
        Returns:
            List[Dict[str, Any]]: Documentos similares encontrados
        """
        if self.collection is None:
            self.initialize_vector_db()
        
        try:
            # Realizar búsqueda en ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=filters
            )
            
            # Formatear resultados
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i],  # Convertir distancia a similitud
                    'rank': i + 1
                }
                documents.append(doc)
            
            logger.info(f"Encontrados {len(documents)} documentos similares")
            return documents
            
        except Exception as e:
            logger.error(f"Error en búsqueda de documentos: {str(e)}")
            raise
    
    def rerank_documents(self, query: str, documents: List[Dict[str, Any]], 
                        top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Re-ordena documentos usando un modelo de re-ranking.
        
        Args:
            query (str): Consulta original
            documents (List[Dict[str, Any]]): Documentos a re-ordenar
            top_k (int): Número de documentos finales
            
        Returns:
            List[Dict[str, Any]]: Documentos re-ordenados
        """
        if self.rerank_model is None:
            self.initialize_models()
        
        try:
            if not documents:
                return []
            
            # Preparar pares query-documento para re-ranking
            query_doc_pairs = [(query, doc['text']) for doc in documents]
            
            # Calcular scores de re-ranking
            rerank_scores = self.rerank_model.predict(query_doc_pairs)
            
            # Agregar scores a los documentos
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(rerank_scores[i])
            
            # Ordenar por score de re-ranking
            reranked_docs = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
            
            # Retornar solo los top_k
            return reranked_docs[:top_k]
            
        except Exception as e:
            logger.error(f"Error en re-ranking: {str(e)}")
            # En caso de error, retornar documentos originales
            return documents[:top_k]
    
    def filter_by_relevance(self, documents: List[Dict[str, Any]], 
                           threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Filtra documentos por relevancia usando umbral de similitud.
        
        Args:
            documents (List[Dict[str, Any]]): Documentos a filtrar
            threshold (float): Umbral de similitud mínima
            
        Returns:
            List[Dict[str, Any]]: Documentos relevantes
        """
        relevant_docs = [
            doc for doc in documents 
            if doc.get('similarity_score', 0) >= threshold
        ]
        
        logger.info(f"Filtrados {len(relevant_docs)} documentos relevantes de {len(documents)}")
        return relevant_docs
    
    def search(self, query: str, 
               user_type: str = "general",
               top_k: int = 5,
               use_reranking: bool = True,
               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda semántica completa.
        
        Args:
            query (str): Consulta de búsqueda
            user_type (str): Tipo de usuario (estudiante, apoderado, profesor)
            top_k (int): Número de resultados finales
            use_reranking (bool): Si usar re-ranking
            filters (Optional[Dict[str, Any]]): Filtros adicionales
            
        Returns:
            List[Dict[str, Any]]: Documentos relevantes encontrados
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.generate_query_embedding(query)
            
            # Aplicar filtros específicos por tipo de usuario
            user_filters = self._get_user_filters(user_type)
            if filters:
                user_filters.update(filters)
            
            # Buscar documentos similares
            similar_docs = self.search_similar_documents(
                query_embedding, 
                top_k=self.rerank_top_k if use_reranking else top_k,
                filters=user_filters
            )
            
            # Filtrar por relevancia
            relevant_docs = self.filter_by_relevance(similar_docs, self.similarity_threshold)
            
            # Aplicar re-ranking si está habilitado
            if use_reranking and relevant_docs:
                final_docs = self.rerank_documents(query, relevant_docs, top_k)
            else:
                final_docs = relevant_docs[:top_k]
            
            # Agregar metadatos de búsqueda
            for doc in final_docs:
                doc['search_metadata'] = {
                    'query': query,
                    'user_type': user_type,
                    'search_time': datetime.now().isoformat(),
                    'reranking_used': use_reranking
                }
            
            logger.info(f"Búsqueda completada: {len(final_docs)} resultados para '{query}'")
            return final_docs
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {str(e)}")
            raise
    
    def _get_user_filters(self, user_type: str) -> Dict[str, Any]:
        """
        Obtiene filtros específicos para cada tipo de usuario.
        
        Args:
            user_type (str): Tipo de usuario
            
        Returns:
            Dict[str, Any]: Filtros aplicables
        """
        filters = {}
        
        if user_type == "estudiante":
            # Los estudiantes pueden acceder a información general y estudiantil
            filters = {
                "document_type": {"$in": ["reglamento_escolar", "calendario_academico", "menu_almuerzos", "documento_general"]}
            }
        elif user_type == "apoderado":
            # Los apoderados pueden acceder a circulares y información administrativa
            filters = {
                "document_type": {"$in": ["circular_apoderados", "reglamento_escolar", "calendario_academico", "manual_procedimientos"]}
            }
        elif user_type == "profesor":
            # Los profesores pueden acceder a toda la información
            filters = {}
        
        return filters
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Genera sugerencias de búsqueda basadas en consultas parciales.
        
        Args:
            partial_query (str): Consulta parcial
            
        Returns:
            List[str]: Sugerencias de búsqueda
        """
        suggestions = [
            "horarios de clases",
            "fechas de evaluaciones",
            "reglamento estudiantil",
            "calendario académico",
            "menú de almuerzos",
            "procedimientos administrativos",
            "circular para apoderados",
            "manual de procedimientos"
        ]
        
        # Filtrar sugerencias que contengan la consulta parcial
        partial_lower = partial_query.lower()
        filtered_suggestions = [
            suggestion for suggestion in suggestions
            if partial_lower in suggestion.lower()
        ]
        
        return filtered_suggestions[:5]  # Retornar máximo 5 sugerencias
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de búsquedas realizadas.
        
        Returns:
            Dict[str, Any]: Estadísticas de búsqueda
        """
        try:
            if self.collection is None:
                self.initialize_vector_db()
            
            # Obtener estadísticas de la colección
            total_docs = self.collection.count()
            
            # Obtener muestra de documentos para análisis
            sample_results = self.collection.get(limit=1000)
            
            # Analizar tipos de documentos
            doc_types = {}
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas']:
                    doc_type = metadata.get('document_type', 'unknown')
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            analytics = {
                'total_documents': total_docs,
                'document_types': doc_types,
                'last_updated': datetime.now().isoformat(),
                'search_capabilities': {
                    'semantic_search': True,
                    'reranking': True,
                    'user_filtering': True,
                    'suggestions': True
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error obteniendo analytics: {str(e)}")
            return {'error': str(e)}

class QueryProcessor:
    """
    Clase para procesamiento avanzado de consultas.
    
    Esta clase maneja la interpretación y expansión de consultas
    para mejorar la precisión de la búsqueda semántica.
    """
    
    def __init__(self):
        """
        Inicializa el procesador de consultas.
        """
        self.query_expansions = {
            'horario': ['horarios', 'clases', 'aula', 'profesor'],
            'evaluacion': ['examen', 'prueba', 'nota', 'calificacion'],
            'reglamento': ['normas', 'reglas', 'conducta', 'disciplina'],
            'fecha': ['fechas', 'calendario', 'evento', 'actividad'],
            'almuerzo': ['comida', 'menu', 'casino', 'alimentacion']
        }
    
    def expand_query(self, query: str) -> str:
        """
        Expande una consulta con términos relacionados.
        
        Args:
            query (str): Consulta original
            
        Returns:
            str: Consulta expandida
        """
        expanded_terms = []
        query_lower = query.lower()
        
        for term, expansions in self.query_expansions.items():
            if term in query_lower:
                expanded_terms.extend(expansions)
        
        if expanded_terms:
            expanded_query = f"{query} {' '.join(expanded_terms)}"
            return expanded_query
        
        return query
    
    def classify_query_intent(self, query: str) -> str:
        """
        Clasifica la intención de la consulta.
        
        Args:
            query (str): Consulta a clasificar
            
        Returns:
            str: Tipo de intención identificada
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['horario', 'clase', 'aula']):
            return 'horarios'
        elif any(word in query_lower for word in ['evaluacion', 'examen', 'nota']):
            return 'evaluaciones'
        elif any(word in query_lower for word in ['reglamento', 'norma', 'regla']):
            return 'reglamento'
        elif any(word in query_lower for word in ['fecha', 'calendario', 'evento']):
            return 'fechas'
        elif any(word in query_lower for word in ['almuerzo', 'comida', 'menu']):
            return 'alimentacion'
        else:
            return 'general'

# Función principal para ejecutar el retriever
def main():
    """
    Función principal para probar el sistema de retrieval.
    """
    # Inicializar retriever
    retriever = SemanticRetriever()
    
    # Ejemplo de búsqueda
    try:
        query = "¿Cuáles son los horarios de clases de matemáticas?"
        results = retriever.search(query, user_type="estudiante", top_k=3)
        
        print(f"Resultados para: '{query}'")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['metadata'].get('file_name', 'Unknown')}")
            print(f"   Similitud: {result['similarity_score']:.4f}")
            print(f"   Re-ranking: {result.get('rerank_score', 'N/A')}")
            print(f"   Texto: {result['text'][:150]}...")
            print()
        
        # Obtener analytics
        analytics = retriever.get_search_analytics()
        print("Analytics de búsqueda:")
        print(json.dumps(analytics, indent=2))
        
    except Exception as e:
        logger.error(f"Error en el retriever principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()



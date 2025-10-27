"""
SchoolBot Agent - Memory Manager
Sistema de Memoria de Corto y Largo Plazo

Autor: Tania Herrera y Camila Armijo
Fecha: 27 Octubre 2025
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import json
import pickle
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# LangChain imports
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Entrada de memoria"""
    id: str
    timestamp: datetime
    content: str
    memory_type: str  # 'short_term', 'long_term', 'episodic', 'semantic'
    importance: float  # 0.0 a 1.0
    tags: List[str]
    context: Dict[str, Any]
    access_count: int = 0
    last_accessed: Optional[datetime] = None

@dataclass
class MemoryStats:
    """Estadísticas de memoria"""
    total_entries: int
    short_term_entries: int
    long_term_entries: int
    episodic_entries: int
    semantic_entries: int
    hit_rate: float
    average_importance: float

class MemoryManager:
    """
    Gestor de memoria de corto y largo plazo para el agente SchoolBot
    
    Características:
    - Memoria de corto plazo: Conversaciones recientes
    - Memoria de largo plazo: Información persistente
    - Memoria episódica: Eventos específicos
    - Memoria semántica: Conocimiento general
    - Recuperación semántica: Búsqueda por similitud
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el gestor de memoria
        
        Args:
            config: Configuración de memoria
        """
        self.config = config
        self.memory_path = config.get("memory_path", "data/memory")
        self.max_short_term = config.get("max_short_term", 100)
        self.max_long_term = config.get("max_long_term", 1000)
        
        # Memoria de corto plazo (buffer circular)
        self.short_term_memory = deque(maxlen=self.max_short_term)
        
        # Memoria de largo plazo (persistente)
        self.long_term_memory = {}
        
        # Memoria episódica (eventos específicos)
        self.episodic_memory = {}
        
        # Memoria semántica (conocimiento general)
        self.semantic_memory = {}
        
        # Vectorizador para búsqueda semántica
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Embeddings para memoria semántica
        self.embeddings = None
        self.vector_store = None
        
        # Estadísticas
        self.stats = MemoryStats(
            total_entries=0,
            short_term_entries=0,
            long_term_entries=0,
            episodic_entries=0,
            semantic_entries=0,
            hit_rate=0.0,
            average_importance=0.0
        )
        
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Inicializa el sistema de memoria"""
        try:
            # Crear directorio de memoria si no existe
            os.makedirs(self.memory_path, exist_ok=True)
            
            # Inicializar embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Cargar memoria persistente
            self._load_persistent_memory()
            
            # Inicializar vector store para memoria semántica
            self._initialize_vector_store()
            
            logger.info("Sistema de memoria inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando memoria: {str(e)}")
            raise
    
    def _load_persistent_memory(self):
        """Carga memoria persistente desde disco"""
        try:
            memory_file = os.path.join(self.memory_path, "long_term_memory.pkl")
            
            if os.path.exists(memory_file):
                with open(memory_file, 'rb') as f:
                    self.long_term_memory = pickle.load(f)
                
                logger.info(f"Memoria persistente cargada: {len(self.long_term_memory)} entradas")
            
        except Exception as e:
            logger.error(f"Error cargando memoria persistente: {str(e)}")
    
    def _save_persistent_memory(self):
        """Guarda memoria persistente en disco"""
        try:
            memory_file = os.path.join(self.memory_path, "long_term_memory.pkl")
            
            with open(memory_file, 'wb') as f:
                pickle.dump(self.long_term_memory, f)
            
            logger.info("Memoria persistente guardada")
            
        except Exception as e:
            logger.error(f"Error guardando memoria persistente: {str(e)}")
    
    def _initialize_vector_store(self):
        """Inicializa el vector store para memoria semántica"""
        try:
            vector_path = os.path.join(self.memory_path, "semantic_vectors")
            
            if os.path.exists(vector_path):
                self.vector_store = Chroma(
                    persist_directory=vector_path,
                    embedding_function=self.embeddings
                )
            else:
                self.vector_store = Chroma(
                    persist_directory=vector_path,
                    embedding_function=self.embeddings
                )
            
            logger.info("Vector store de memoria semántica inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando vector store: {str(e)}")
    
    def store_interaction(self, interaction: Dict[str, Any]):
        """
        Almacena una interacción en memoria
        
        Args:
            interaction: Datos de la interacción
        """
        try:
            # Crear entrada de memoria
            memory_entry = MemoryEntry(
                id=f"interaction_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                content=interaction.get("request", ""),
                memory_type="short_term",
                importance=self._calculate_importance(interaction),
                tags=self._extract_tags(interaction),
                context=interaction.get("context", {})
            )
            
            # Almacenar en memoria de corto plazo
            self.short_term_memory.append(memory_entry)
            
            # Evaluar si debe promoverse a memoria de largo plazo
            if memory_entry.importance > 0.7:
                self._promote_to_long_term(memory_entry)
            
            # Actualizar estadísticas
            self._update_stats()
            
            logger.info(f"Interacción almacenada en memoria: {memory_entry.id}")
            
        except Exception as e:
            logger.error(f"Error almacenando interacción: {str(e)}")
    
    def store_feedback(self, feedback: Dict[str, Any]):
        """
        Almacena feedback del usuario
        
        Args:
            feedback: Datos del feedback
        """
        try:
            feedback_entry = MemoryEntry(
                id=f"feedback_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                content=feedback.get("content", ""),
                memory_type="episodic",
                importance=0.8,  # Feedback siempre es importante
                tags=["feedback", feedback.get("type", "general")],
                context=feedback
            )
            
            # Almacenar en memoria episódica
            self.episodic_memory[feedback_entry.id] = feedback_entry
            
            # Actualizar estadísticas
            self._update_stats()
            
            logger.info(f"Feedback almacenado: {feedback_entry.id}")
            
        except Exception as e:
            logger.error(f"Error almacenando feedback: {str(e)}")
    
    def retrieve_memory(self, query: str, memory_type: Optional[str] = None, limit: int = 5) -> List[MemoryEntry]:
        """
        Recupera memoria relevante para una consulta
        
        Args:
            query: Consulta de búsqueda
            memory_type: Tipo de memoria a buscar
            limit: Número máximo de resultados
            
        Returns:
            Lista de entradas de memoria relevantes
        """
        try:
            results = []
            
            # Buscar en memoria de corto plazo
            if memory_type is None or memory_type == "short_term":
                short_term_results = self._search_short_term(query, limit)
                results.extend(short_term_results)
            
            # Buscar en memoria de largo plazo
            if memory_type is None or memory_type == "long_term":
                long_term_results = self._search_long_term(query, limit)
                results.extend(long_term_results)
            
            # Buscar en memoria episódica
            if memory_type is None or memory_type == "episodic":
                episodic_results = self._search_episodic(query, limit)
                results.extend(episodic_results)
            
            # Buscar en memoria semántica
            if memory_type is None or memory_type == "semantic":
                semantic_results = self._search_semantic(query, limit)
                results.extend(semantic_results)
            
            # Ordenar por relevancia y limitar resultados
            results = self._rank_results(query, results)[:limit]
            
            # Actualizar contadores de acceso
            for result in results:
                result.access_count += 1
                result.last_accessed = datetime.now()
            
            logger.info(f"Memoria recuperada: {len(results)} entradas para '{query}'")
            
            return results
            
        except Exception as e:
            logger.error(f"Error recuperando memoria: {str(e)}")
            return []
    
    def _search_short_term(self, query: str, limit: int) -> List[MemoryEntry]:
        """Busca en memoria de corto plazo"""
        results = []
        
        for entry in self.short_term_memory:
            if self._is_relevant(query, entry.content):
                results.append(entry)
        
        return results[:limit]
    
    def _search_long_term(self, query: str, limit: int) -> List[MemoryEntry]:
        """Busca en memoria de largo plazo"""
        results = []
        
        for entry_id, entry in self.long_term_memory.items():
            if self._is_relevant(query, entry.content):
                results.append(entry)
        
        return results[:limit]
    
    def _search_episodic(self, query: str, limit: int) -> List[MemoryEntry]:
        """Busca en memoria episódica"""
        results = []
        
        for entry_id, entry in self.episodic_memory.items():
            if self._is_relevant(query, entry.content):
                results.append(entry)
        
        return results[:limit]
    
    def _search_semantic(self, query: str, limit: int) -> List[MemoryEntry]:
        """Busca en memoria semántica usando embeddings"""
        results = []
        
        try:
            if self.vector_store:
                # Buscar documentos similares
                docs = self.vector_store.similarity_search(query, k=limit)
                
                for doc in docs:
                    # Crear entrada de memoria desde documento
                    entry = MemoryEntry(
                        id=doc.metadata.get("id", "unknown"),
                        timestamp=datetime.fromisoformat(doc.metadata.get("timestamp", datetime.now().isoformat())),
                        content=doc.page_content,
                        memory_type="semantic",
                        importance=doc.metadata.get("importance", 0.5),
                        tags=doc.metadata.get("tags", []),
                        context=doc.metadata.get("context", {})
                    )
                    results.append(entry)
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {str(e)}")
        
        return results
    
    def _is_relevant(self, query: str, content: str) -> bool:
        """Determina si el contenido es relevante para la consulta"""
        try:
            # Usar vectorizador para calcular similitud
            texts = [query, content]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity > 0.3  # Umbral de relevancia
            
        except Exception as e:
            logger.error(f"Error calculando relevancia: {str(e)}")
            return False
    
    def _rank_results(self, query: str, results: List[MemoryEntry]) -> List[MemoryEntry]:
        """Ordena resultados por relevancia"""
        try:
            # Calcular puntuación de relevancia para cada resultado
            scored_results = []
            
            for result in results:
                # Similitud de contenido
                content_similarity = self._calculate_similarity(query, result.content)
                
                # Factor de importancia
                importance_factor = result.importance
                
                # Factor de acceso reciente
                recency_factor = self._calculate_recency_factor(result)
                
                # Puntuación combinada
                score = (
                    content_similarity * 0.5 +
                    importance_factor * 0.3 +
                    recency_factor * 0.2
                )
                
                scored_results.append((score, result))
            
            # Ordenar por puntuación
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            return [result for score, result in scored_results]
            
        except Exception as e:
            logger.error(f"Error ordenando resultados: {str(e)}")
            return results
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud entre dos textos"""
        try:
            texts = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def _calculate_recency_factor(self, entry: MemoryEntry) -> float:
        """Calcula factor de recencia"""
        try:
            days_ago = (datetime.now() - entry.timestamp).days
            return max(0.0, 1.0 - (days_ago / 30.0))  # Decae en 30 días
        except:
            return 0.0
    
    def _calculate_importance(self, interaction: Dict[str, Any]) -> float:
        """Calcula la importancia de una interacción"""
        importance = 0.5  # Base
        
        # Factor de longitud de respuesta
        response_length = len(interaction.get("response", ""))
        if response_length > 200:
            importance += 0.2
        
        # Factor de análisis de complejidad
        analysis = interaction.get("analysis", {})
        if analysis.get("complexity") == "complex":
            importance += 0.3
        
        # Factor de herramientas utilizadas
        tools_used = len(analysis.get("tools_needed", []))
        importance += min(0.2, tools_used * 0.1)
        
        return min(1.0, importance)
    
    def _extract_tags(self, interaction: Dict[str, Any]) -> List[str]:
        """Extrae tags de una interacción"""
        tags = []
        
        # Tags basados en análisis
        analysis = interaction.get("analysis", {})
        if analysis.get("intent"):
            tags.append(f"intent:{analysis['intent']}")
        
        if analysis.get("tools_needed"):
            for tool in analysis["tools_needed"]:
                tags.append(f"tool:{tool}")
        
        # Tags basados en contexto
        context = interaction.get("context", {})
        if context.get("user_type"):
            tags.append(f"user:{context['user_type']}")
        
        return tags
    
    def _promote_to_long_term(self, entry: MemoryEntry):
        """Promueve una entrada a memoria de largo plazo"""
        try:
            entry.memory_type = "long_term"
            self.long_term_memory[entry.id] = entry
            
            # También agregar a memoria semántica si es muy importante
            if entry.importance > 0.8:
                self._add_to_semantic_memory(entry)
            
            logger.info(f"Entrada promovida a memoria de largo plazo: {entry.id}")
            
        except Exception as e:
            logger.error(f"Error promoviendo entrada: {str(e)}")
    
    def _add_to_semantic_memory(self, entry: MemoryEntry):
        """Agrega entrada a memoria semántica"""
        try:
            if self.vector_store:
                # Crear documento para vector store
                doc = Document(
                    page_content=entry.content,
                    metadata={
                        "id": entry.id,
                        "timestamp": entry.timestamp.isoformat(),
                        "importance": entry.importance,
                        "tags": entry.tags,
                        "context": entry.context,
                        "memory_type": "semantic"
                    }
                )
                
                # Agregar al vector store
                self.vector_store.add_documents([doc])
                
                logger.info(f"Entrada agregada a memoria semántica: {entry.id}")
            
        except Exception as e:
            logger.error(f"Error agregando a memoria semántica: {str(e)}")
    
    def _update_stats(self):
        """Actualiza estadísticas de memoria"""
        self.stats.total_entries = (
            len(self.short_term_memory) +
            len(self.long_term_memory) +
            len(self.episodic_memory) +
            len(self.semantic_memory)
        )
        
        self.stats.short_term_entries = len(self.short_term_memory)
        self.stats.long_term_entries = len(self.long_term_memory)
        self.stats.episodic_entries = len(self.episodic_memory)
        self.stats.semantic_entries = len(self.semantic_memory)
        
        # Calcular importancia promedio
        all_entries = list(self.short_term_memory) + list(self.long_term_memory.values()) + list(self.episodic_memory.values())
        if all_entries:
            self.stats.average_importance = sum(entry.importance for entry in all_entries) / len(all_entries)
    
    def get_summary(self) -> str:
        """Obtiene resumen de la memoria"""
        try:
            # Obtener entradas más importantes de los últimos 7 días
            recent_entries = []
            
            for entry in self.short_term_memory:
                if (datetime.now() - entry.timestamp).days <= 7:
                    recent_entries.append(entry)
            
            # Ordenar por importancia
            recent_entries.sort(key=lambda x: x.importance, reverse=True)
            
            # Crear resumen
            summary_parts = []
            for entry in recent_entries[:5]:  # Top 5 más importantes
                summary_parts.append(f"- {entry.content[:100]}...")
            
            return "\n".join(summary_parts) if summary_parts else "No hay memoria reciente significativa."
            
        except Exception as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return "Error generando resumen de memoria."
    
    def get_hit_rate(self) -> float:
        """Calcula tasa de aciertos de memoria"""
        try:
            total_accesses = 0
            successful_accesses = 0
            
            all_entries = list(self.short_term_memory) + list(self.long_term_memory.values()) + list(self.episodic_memory.values())
            
            for entry in all_entries:
                total_accesses += entry.access_count
                if entry.access_count > 0:
                    successful_accesses += 1
            
            return successful_accesses / len(all_entries) if all_entries else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando tasa de aciertos: {str(e)}")
            return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de memoria"""
        return {
            "stats": asdict(self.stats),
            "memory_path": self.memory_path,
            "vector_store_available": self.vector_store is not None,
            "embeddings_available": self.embeddings is not None
        }
    
    def save_memory(self):
        """Guarda memoria persistente"""
        try:
            self._save_persistent_memory()
            
            if self.vector_store:
                self.vector_store.persist()
            
            logger.info("Memoria guardada correctamente")
            
        except Exception as e:
            logger.error(f"Error guardando memoria: {str(e)}")
    
    def clear_memory(self, memory_type: Optional[str] = None):
        """Limpia memoria"""
        try:
            if memory_type is None or memory_type == "short_term":
                self.short_term_memory.clear()
            
            if memory_type is None or memory_type == "long_term":
                self.long_term_memory.clear()
            
            if memory_type is None or memory_type == "episodic":
                self.episodic_memory.clear()
            
            if memory_type is None or memory_type == "semantic":
                if self.vector_store:
                    # Eliminar vector store y recrear
                    import shutil
                    vector_path = os.path.join(self.memory_path, "semantic_vectors")
                    if os.path.exists(vector_path):
                        shutil.rmtree(vector_path)
                    self._initialize_vector_store()
            
            self._update_stats()
            logger.info(f"Memoria limpiada: {memory_type or 'all'}")
            
        except Exception as e:
            logger.error(f"Error limpiando memoria: {str(e)}")

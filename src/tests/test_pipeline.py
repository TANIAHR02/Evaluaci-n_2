"""
SchoolBot - Asistente Inteligente Escolar
Tests del Pipeline Completo

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo contiene tests unitarios e integración para validar
el funcionamiento completo del pipeline de SchoolBot, incluyendo
ingesta de documentos, generación de embeddings, retrieval y API.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import json
import numpy as np
from datetime import datetime

# Agregar el directorio src al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos a testear
from ingest.ingest_data import DocumentProcessor, DocumentIngestionPipeline
from embeddings.generate_embeddings import EmbeddingGenerator, VectorDatabase, EmbeddingPipeline
from retriever.retriever import SemanticRetriever, QueryProcessor
from api.app import app
from fastapi.testclient import TestClient

# Configuración de tests
TEST_DATA_DIR = "test_data"
TEST_DOCUMENTS = [
    {
        "filename": "reglamento_escolar.pdf",
        "content": "REGLAMENTO ESCOLAR\n\n1. HORARIOS DE CLASES\nLas clases se desarrollan de lunes a viernes de 8:00 a 16:00 horas.\n\n2. NORMAS DE CONDUCTA\nLos estudiantes deben mantener un comportamiento respetuoso en todo momento.",
        "document_type": "reglamento_escolar"
    },
    {
        "filename": "calendario_academico.xlsx",
        "content": "CALENDARIO ACADÉMICO 2024\n\nEnero: Vacaciones de verano\nFebrero: Inicio de clases\nMarzo: Evaluaciones parciales\nAbril: Vacaciones de invierno",
        "document_type": "calendario_academico"
    },
    {
        "filename": "circular_apoderados.docx",
        "content": "CIRCULAR PARA APODERADOS\n\nEstimados apoderados:\n\nLes informamos sobre las próximas actividades del colegio.\n\nReunión de apoderados: 15 de marzo\nEvaluaciones: 20-25 de marzo",
        "document_type": "circular_apoderados"
    }
]

class TestDocumentProcessor:
    """Tests para el procesador de documentos"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.processor = DocumentProcessor(chunk_size=256, chunk_overlap=50)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_document(self, filename: str, content: str) -> str:
        """Crea un documento de prueba"""
        file_path = os.path.join(self.temp_dir, filename)
        
        if filename.endswith('.txt'):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif filename.endswith('.pdf'):
            # Para tests, crear un archivo de texto que simule PDF
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return file_path
    
    def test_document_processor_initialization(self):
        """Test: Inicialización del procesador"""
        assert self.processor.chunk_size == 256
        assert self.processor.chunk_overlap == 50
        assert self.processor.stemmer is not None
    
    def test_text_cleaning(self):
        """Test: Limpieza de texto"""
        dirty_text = "  Este   es un   texto\n\n\ncon   espacios   extra.  "
        cleaned = self.processor.clean_text(dirty_text)
        expected = "Este es un texto con espacios extra."
        assert cleaned == expected
    
    def test_text_chunking(self):
        """Test: División de texto en chunks"""
        long_text = "Esta es una oración. " * 50  # Texto largo
        chunks = self.processor.chunk_text(long_text)
        
        assert len(chunks) > 1
        assert all(chunk['tokens'] <= self.processor.chunk_size for chunk in chunks)
        assert all('id' in chunk for chunk in chunks)
        assert all('text' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_document_id_generation(self):
        """Test: Generación de ID único de documento"""
        file_path = self.create_test_document("test.txt", "contenido de prueba")
        doc_id = self.processor.generate_document_id(file_path)
        
        assert doc_id is not None
        assert len(doc_id) > 0
        assert isinstance(doc_id, str)
    
    def test_document_type_inference(self):
        """Test: Inferencia de tipo de documento"""
        test_cases = [
            ("reglamento_estudiantil.pdf", "reglamento_escolar"),
            ("calendario_2024.xlsx", "calendario_academico"),
            ("circular_marzo.docx", "circular_apoderados"),
            ("menu_semana.pdf", "menu_almuerzos"),
            ("manual_admin.docx", "manual_procedimientos"),
            ("documento_general.txt", "documento_general")
        ]
        
        for filename, expected_type in test_cases:
            inferred_type = self.processor._infer_document_type(filename)
            assert inferred_type == expected_type

class TestEmbeddingGenerator:
    """Tests para el generador de embeddings"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.generator = EmbeddingGenerator()
    
    def test_embedding_generator_initialization(self):
        """Test: Inicialización del generador"""
        assert self.generator.model_name is not None
        assert self.generator.embedding_dim == 384
        assert self.generator.device in ["cuda", "cpu"]
    
    def test_text_preprocessing(self):
        """Test: Preprocesamiento de texto"""
        text = "  Este es un texto\ncon saltos de línea   y espacios extra.  "
        processed = self.generator.preprocess_text(text)
        
        assert processed == "Este es un texto con saltos de línea y espacios extra."
        assert len(processed) <= 512  # Límite del modelo
    
    def test_single_embedding_generation(self):
        """Test: Generación de embedding individual"""
        text = "Este es un texto de prueba para generar embeddings."
        embedding = self.generator.generate_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == self.generator.embedding_dim
        assert np.allclose(np.linalg.norm(embedding), 1.0, atol=1e-6)  # Normalizado
    
    def test_batch_embedding_generation(self):
        """Test: Generación de embeddings en lote"""
        texts = [
            "Primer texto de prueba",
            "Segundo texto de prueba",
            "Tercer texto de prueba"
        ]
        
        embeddings = self.generator.generate_embeddings_batch(texts, batch_size=2)
        
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        assert all(emb.shape[0] == self.generator.embedding_dim for emb in embeddings)

class TestVectorDatabase:
    """Tests para la base de datos vectorial"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_db = VectorDatabase(self.temp_dir)
        self.vector_db.initialize()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_vector_database_initialization(self):
        """Test: Inicialización de la base de datos"""
        assert self.vector_db.client is not None
        assert self.vector_db.collection is not None
    
    def test_store_and_retrieve_embeddings(self):
        """Test: Almacenamiento y recuperación de embeddings"""
        # Crear datos de prueba
        chunks = [
            {
                'id': 'test_chunk_1',
                'text': 'Primer documento de prueba',
                'metadata': {'document_type': 'test', 'file_name': 'test1.txt'}
            },
            {
                'id': 'test_chunk_2',
                'text': 'Segundo documento de prueba',
                'metadata': {'document_type': 'test', 'file_name': 'test2.txt'}
            }
        ]
        
        embeddings = [
            np.random.rand(384).astype(np.float32),
            np.random.rand(384).astype(np.float32)
        ]
        
        # Almacenar
        self.vector_db.store_embeddings(chunks, embeddings)
        
        # Verificar que se almacenaron
        stats = self.vector_db.get_collection_stats()
        assert stats['total_documents'] == 2
    
    def test_similarity_search(self):
        """Test: Búsqueda por similitud"""
        # Crear datos de prueba
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'horarios de clases de matemáticas',
                'metadata': {'document_type': 'reglamento'}
            },
            {
                'id': 'chunk_2',
                'text': 'fechas de evaluaciones de ciencias',
                'metadata': {'document_type': 'calendario'}
            }
        ]
        
        embeddings = [
            np.array([1.0, 0.0, 0.0, 0.0] + [0.0] * 380),  # Vector para "horarios"
            np.array([0.0, 1.0, 0.0, 0.0] + [0.0] * 380)   # Vector para "fechas"
        ]
        
        # Almacenar
        self.vector_db.store_embeddings(chunks, embeddings)
        
        # Buscar
        query_embedding = np.array([0.9, 0.1, 0.0, 0.0] + [0.0] * 380)
        results = self.vector_db.search_similar(query_embedding, top_k=2)
        
        assert len(results) == 2
        assert results[0]['id'] == 'chunk_1'  # Debería ser el más similar

class TestSemanticRetriever:
    """Tests para el retriever semántico"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.retriever = SemanticRetriever(vector_db_path=self.temp_dir)
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_retriever_initialization(self):
        """Test: Inicialización del retriever"""
        assert self.retriever.similarity_threshold == 0.7
        assert self.retriever.max_results == 10
        assert self.retriever.rerank_top_k == 20
    
    def test_query_preprocessing(self):
        """Test: Preprocesamiento de consultas"""
        query = "  ¿Cuáles son los HORARIOS de clases?  "
        processed = self.retriever.preprocess_query(query)
        
        assert processed == "¿cuáles son los horario de clases"
        assert processed.islower()
    
    def test_user_filters(self):
        """Test: Filtros por tipo de usuario"""
        # Test filtro para estudiante
        student_filters = self.retriever._get_user_filters("estudiante")
        assert "document_type" in student_filters
        assert "reglamento_escolar" in student_filters["document_type"]["$in"]
        
        # Test filtro para apoderado
        parent_filters = self.retriever._get_user_filters("apoderado")
        assert "circular_apoderados" in parent_filters["document_type"]["$in"]
        
        # Test filtro para profesor (sin restricciones)
        teacher_filters = self.retriever._get_user_filters("profesor")
        assert teacher_filters == {}

class TestQueryProcessor:
    """Tests para el procesador de consultas"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.processor = QueryProcessor()
    
    def test_query_expansion(self):
        """Test: Expansión de consultas"""
        query = "horario de clases"
        expanded = self.processor.expand_query(query)
        
        assert "horarios" in expanded
        assert "clases" in expanded
        assert "aula" in expanded
    
    def test_query_intent_classification(self):
        """Test: Clasificación de intención de consulta"""
        test_cases = [
            ("¿Cuáles son los horarios?", "horarios"),
            ("¿Cuándo son las evaluaciones?", "evaluaciones"),
            ("¿Qué dice el reglamento?", "reglamento"),
            ("¿Cuándo es el evento?", "fechas"),
            ("¿Qué hay de almuerzo?", "alimentacion"),
            ("¿Cómo está el clima?", "general")
        ]
        
        for query, expected_intent in test_cases:
            intent = self.processor.classify_query_intent(query)
            assert intent == expected_intent

class TestAPI:
    """Tests para la API REST"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test: Endpoint raíz"""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """Test: Health check"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime" in data
        assert "components" in data
    
    def test_user_registration(self):
        """Test: Registro de usuario"""
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpassword123",
            "user_type": "estudiante",
            "full_name": "Usuario de Prueba"
        }
        
        response = self.client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["username"] == "test_user"
    
    def test_user_login(self):
        """Test: Login de usuario"""
        # Primero registrar usuario
        user_data = {
            "username": "login_test_user",
            "email": "login@example.com",
            "password": "testpassword123",
            "user_type": "estudiante",
            "full_name": "Usuario Login Test"
        }
        
        self.client.post("/api/v1/auth/register", json=user_data)
        
        # Luego hacer login
        login_data = {
            "username": "login_test_user",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user_type" in data

class TestIntegrationPipeline:
    """Tests de integración para el pipeline completo"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_docs_dir = os.path.join(self.temp_dir, "test_docs")
        os.makedirs(self.test_docs_dir, exist_ok=True)
        
        # Crear documentos de prueba
        for doc in TEST_DOCUMENTS:
            file_path = os.path.join(self.test_docs_dir, doc["filename"])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc["content"])
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_pipeline(self):
        """Test: Pipeline completo de ingesta a búsqueda"""
        # 1. Ingesta de documentos
        pipeline = DocumentIngestionPipeline(self.test_docs_dir)
        processed_docs = pipeline.process_all_documents()
        
        assert len(processed_docs) == len(TEST_DOCUMENTS)
        
        # 2. Generación de embeddings
        embedding_pipeline = EmbeddingPipeline(self.temp_dir)
        
        all_chunks = []
        for doc in processed_docs:
            all_chunks.extend(doc['chunks'])
        
        embeddings, processed_chunks = embedding_pipeline.process_chunks(all_chunks)
        
        assert len(embeddings) == len(processed_chunks)
        
        # 3. Almacenamiento en base de datos vectorial
        embedding_pipeline.store_in_database(processed_chunks, embeddings)
        
        # 4. Búsqueda semántica
        retriever = SemanticRetriever(vector_db_path=self.temp_dir)
        retriever.initialize_models()
        retriever.initialize_vector_db()
        
        query = "¿Cuáles son los horarios de clases?"
        results = retriever.search(query, user_type="estudiante", top_k=3)
        
        assert len(results) > 0
        assert all('similarity_score' in result for result in results)
        assert all('text' in result for result in results)

# Fixtures de pytest
@pytest.fixture
def sample_documents():
    """Fixture con documentos de muestra"""
    return TEST_DOCUMENTS

@pytest.fixture
def temp_directory():
    """Fixture con directorio temporal"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

# Tests de rendimiento
class TestPerformance:
    """Tests de rendimiento del sistema"""
    
    def test_embedding_generation_performance(self):
        """Test: Rendimiento de generación de embeddings"""
        generator = EmbeddingGenerator()
        
        # Crear lista de textos de prueba
        texts = [f"Texto de prueba número {i}" for i in range(100)]
        
        import time
        start_time = time.time()
        
        embeddings = generator.generate_embeddings_batch(texts, batch_size=32)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(embeddings) == 100
        assert processing_time < 30  # Debe procesar 100 textos en menos de 30 segundos
    
    def test_search_performance(self):
        """Test: Rendimiento de búsqueda semántica"""
        # Este test requeriría una base de datos vectorial poblada
        # Se implementaría con datos de prueba más extensos
        pass

# Función principal para ejecutar tests
def main():
    """
    Función principal para ejecutar todos los tests.
    """
    # Configurar pytest
    pytest_args = [
        "-v",  # Verbose
        "--tb=short",  # Traceback corto
        "--strict-markers",  # Marcadores estrictos
        "--disable-warnings",  # Deshabilitar warnings
        __file__  # Archivo actual
    ]
    
    # Ejecutar tests
    exit_code = pytest.main(pytest_args)
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)



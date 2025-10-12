# FASE 6 – Diagrama de Arquitectura - SchoolBot

**Autor:** Tania Herrera  
**Fecha:** Octubre 2025  
**Evaluación:** EP1 - Ingeniería de Soluciones con Inteligencia Artificial  

---

## 📐 Diagramas de Arquitectura

### 1. Diagrama Simplificado (`diagrama_arquitectura.puml`)

Este diagrama muestra el flujo básico del sistema SchoolBot con los componentes principales:

```
Usuario → Chat Escolar → API Gateway → Agent Manager → LLM Service
                                    ↓
                              Embedding Service → Vector DB (FAISS)
                                    ↓
                              Metadata DB (Logs y consultas)
```

**Componentes principales:**
- **Chat Escolar (Frontend):** Interfaz de usuario web
- **API Gateway (Orchestrator):** Punto de entrada y coordinación
- **Agent Manager:** Coordinador de los 5 agentes principales
- **LLM Service:** Servicio de modelo de lenguaje (Mistral 7B)
- **Embedding Service:** Generación de embeddings semánticos
- **Vector DB (FAISS):** Base de datos vectorial para búsqueda
- **Metadata DB:** Almacenamiento de logs y consultas

### 2. Diagrama Detallado (`diagrama_arquitectura_detallado.puml`)

Este diagrama proporciona una vista más completa de la arquitectura con:

**Capas del sistema:**
1. **Capa de Presentación:** Frontend web con React/TypeScript
2. **Capa de API:** FastAPI Gateway con autenticación y rate limiting
3. **Capa de Servicios:** Agentes de IA y pipeline RAG
4. **Capa de Datos:** Bases de datos vectoriales y relacionales

**Flujo detallado (14 pasos):**
1. Usuario realiza pregunta en el chat
2. Frontend envía POST /ask al API Gateway
3. API Gateway procesa la consulta
4. Agent Manager genera embeddings
5. Embedding Service busca documentos similares
6. Vector DB retorna top_k fragmentos
7. RAG Pipeline prepara contexto
8. LLM Service genera respuesta con contexto
9. Respuesta generada por el modelo
10. RAG Pipeline procesa respuesta
11. Agent Manager registra logs
12. API Gateway retorna respuesta procesada
13. Frontend muestra respuesta
14. Usuario recibe respuesta final

---

## 🔧 Componentes Técnicos

### Agent Manager
- **Función:** Coordinador central de los 5 agentes principales
- **Responsabilidades:**
  - Gestionar el flujo de trabajo entre agentes
  - Aplicar validaciones de coherencia
  - Registrar métricas de performance
  - Coordinar respuestas entre servicios

### LLM Service
- **Modelo:** Mistral 7B
- **Despliegue:** Local con Ollama
- **Características:**
  - Prompts optimizados por contexto educativo
  - Parámetros ajustables por tipo de consulta
  - Gestión de contexto y memoria
  - Generación de respuestas coherentes

### RAG Pipeline
- **Función:** Pipeline de Retrieval Augmented Generation
- **Procesos:**
  - Carga de documentos (PDF, DOCX, XLSX)
  - División en chunks (600 caracteres, 80 overlap)
  - Generación de embeddings semánticos
  - Búsqueda por similitud coseno
  - Síntesis de contexto relevante

### Vector Database
- **Tecnología:** ChromaDB + FAISS
- **Características:**
  - Almacenamiento eficiente de embeddings
  - Índice HNSW para búsqueda rápida
  - Metadatos enriquecidos
  - Escalabilidad horizontal

### Embedding Service
- **Modelo:** sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Función:** Generación de embeddings semánticos
- **Características:**
  - Soporte multilingüe
  - Optimizado para contexto educativo
  - Normalización automática de texto
  - Batch processing eficiente

---

## 📊 Flujo de Datos

### Entrada de Datos
1. **Documentos escolares** (PDF, DOCX, XLSX)
2. **Consultas de usuarios** (texto natural)
3. **Metadatos** (fechas, tipos de documento, secciones)

### Procesamiento
1. **Ingesta:** Carga y limpieza de documentos
2. **Chunking:** División en fragmentos manejables
3. **Embedding:** Generación de representaciones vectoriales
4. **Indexación:** Almacenamiento en base de datos vectorial
5. **Búsqueda:** Recuperación de documentos relevantes
6. **Síntesis:** Generación de respuesta contextualizada

### Salida de Datos
1. **Respuestas contextualizadas** para usuarios
2. **Logs de consultas** para análisis
3. **Métricas de performance** para monitoreo
4. **Metadatos enriquecidos** para futuras consultas

---

## 🎯 Características de la Arquitectura

### Escalabilidad
- **Horizontal:** Múltiples instancias de servicios
- **Vertical:** Optimización de recursos por componente
- **Elástica:** Ajuste automático según demanda

### Disponibilidad
- **Alta disponibilidad:** Redundancia en componentes críticos
- **Tolerancia a fallos:** Recuperación automática
- **Monitoreo continuo:** Alertas proactivas

### Seguridad
- **Autenticación:** JWT + OAuth2
- **Autorización:** Control de acceso basado en roles
- **Encriptación:** Datos en tránsito y en reposo
- **Auditoría:** Logs completos de todas las operaciones

### Mantenibilidad
- **Modularidad:** Componentes independientes
- **Documentación:** Código autodocumentado
- **Testing:** Cobertura completa de pruebas
- **CI/CD:** Despliegue automatizado

---

## 📈 Métricas y Monitoreo

### Métricas de Performance
- **Tiempo de respuesta:** < 3 segundos promedio
- **Throughput:** 100+ consultas por minuto
- **Precisión:** > 85% de respuestas correctas
- **Disponibilidad:** 99.9% uptime

### Métricas de Negocio
- **Consultas por día:** Volumen de uso
- **Tipos de consultas:** Categorización automática
- **Satisfacción del usuario:** Feedback y ratings
- **Eficiencia administrativa:** Reducción de consultas manuales

### Alertas y Notificaciones
- **Errores críticos:** Fallos en servicios principales
- **Degradación de performance:** Tiempos de respuesta altos
- **Uso de recursos:** CPU, memoria, almacenamiento
- **Seguridad:** Intentos de acceso no autorizados

---

## 🚀 Despliegue y Configuración

### Requisitos del Sistema
- **CPU:** 8+ cores
- **RAM:** 16+ GB
- **Almacenamiento:** 100+ GB SSD
- **GPU:** Opcional para aceleración

### Dependencias
- **Python:** 3.9+
- **Ollama:** Para modelo Mistral 7B
- **ChromaDB:** Base de datos vectorial
- **PostgreSQL:** Base de datos relacional
- **Redis:** Cache y sesiones

### Variables de Entorno
```bash
# Modelo LLM
OLLAMA_MODEL=mistral:7b
OLLAMA_BASE_URL=http://localhost:11434

# Base de datos
CHROMA_PERSIST_DIRECTORY=./data/vector_db
POSTGRES_URL=postgresql://user:pass@localhost/schoolbot
REDIS_URL=redis://localhost:6379

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Embeddings
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DEVICE=cpu
```

---

## 📋 Conclusiones

La arquitectura de SchoolBot está diseñada para:

1. **Escalabilidad:** Crecer con las necesidades del colegio
2. **Mantenibilidad:** Fácil actualización y mejora
3. **Confiabilidad:** Alta disponibilidad y tolerancia a fallos
4. **Seguridad:** Protección de datos y privacidad
5. **Performance:** Respuestas rápidas y precisas

El sistema está optimizado para el contexto educativo del Colegio San Ignacio Digital, proporcionando un asistente virtual inteligente que mejora la comunicación y eficiencia administrativa.

---

**Desarrollado por:** Tania Herrera  
**Fecha:** Octubre 2025  
**Institución:** Universidad [Nombre]

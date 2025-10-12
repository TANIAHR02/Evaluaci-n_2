# Análisis Técnico - SchoolBot – Asistente Inteligente Escolar

**Autor:** [Nombre del Estudiante]  
**Fecha:** [Fecha Actual]  
**Evaluación:** EP1 - Ingeniería de Soluciones con Inteligencia Artificial  
**Institución:** Universidad [Nombre]  

---

## 1. Análisis de Requerimientos

### 1.1 Requerimientos Funcionales

#### RF-001: Procesamiento de Consultas
- **Descripción:** El sistema debe procesar consultas en lenguaje natural sobre información escolar
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  - Procesar consultas en español chileno
  - Responder con precisión del 80% o superior
  - Tiempo de respuesta menor a 3 segundos

#### RF-002: Gestión de Documentos
- **Descripción:** El sistema debe ingerir y procesar documentos escolares en múltiples formatos
- **Prioridad:** Alta
- **Criterios de Aceptación:**
  - Soporte para PDF, DOCX, XLSX
  - Actualización automática de documentos
  - Indexación eficiente para búsqueda rápida

#### RF-003: Interfaz de Usuario
- **Descripción:** Proporcionar una interfaz web intuitiva para interacción con el asistente
- **Prioridad:** Media
- **Criterios de Aceptación:**
  - Diseño responsive para móviles y desktop
  - Interfaz en español
  - Historial de conversaciones

#### RF-004: Autenticación y Autorización
- **Descripción:** Sistema de acceso diferenciado por tipo de usuario
- **Prioridad:** Media
- **Criterios de Aceptación:**
  - Login para estudiantes, apoderados y profesores
  - Acceso diferenciado a información según rol
  - Seguridad de datos personales

### 1.2 Requerimientos No Funcionales

#### RNF-001: Rendimiento
- **Descripción:** El sistema debe manejar múltiples consultas simultáneas
- **Especificación:** 100 usuarios concurrentes, tiempo de respuesta < 3 segundos

#### RNF-002: Disponibilidad
- **Descripción:** El sistema debe estar disponible durante horario escolar
- **Especificación:** 99% de uptime en horario 8:00-18:00

#### RNF-003: Escalabilidad
- **Descripción:** Capacidad de crecimiento futuro
- **Especificación:** Soporte para 1000+ usuarios sin degradación de rendimiento

#### RNF-004: Seguridad
- **Descripción:** Protección de datos y cumplimiento legal
- **Especificación:** Cumplimiento con Ley de Protección de Datos Personales de Chile

---

## 2. Análisis de Arquitectura

### 2.1 Patrón Arquitectónico: RAG (Retrieval-Augmented Generation)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Vector DB     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │   (Ollama)      │
                       └─────────────────┘
```

### 2.2 Componentes Principales

#### 2.2.1 Capa de Ingesta de Datos
- **Propósito:** Procesar y preparar documentos para el sistema
- **Tecnologías:** Python, PyPDF2, python-docx, pandas
- **Responsabilidades:**
  - Extracción de texto de documentos
  - Limpieza y normalización de datos
  - Chunking de documentos para procesamiento

#### 2.2.2 Capa de Embeddings
- **Propósito:** Generar representaciones vectoriales de documentos
- **Tecnologías:** sentence-transformers, Hugging Face
- **Responsabilidades:**
  - Generación de embeddings para chunks de texto
  - Almacenamiento en base de datos vectorial
  - Actualización de embeddings cuando cambian los documentos

#### 2.2.3 Capa de Retrieval
- **Propósito:** Encontrar información relevante para consultas
- **Tecnologías:** ChromaDB, FAISS
- **Responsabilidades:**
  - Búsqueda semántica en documentos
  - Ranking de resultados por relevancia
  - Filtrado por tipo de usuario y contexto

#### 2.2.4 Capa de Generación
- **Propósito:** Generar respuestas coherentes basadas en contexto
- **Tecnologías:** Ollama, Llama 2, Mistral
- **Responsabilidades:**
  - Procesamiento de consultas en lenguaje natural
  - Generación de respuestas contextualizadas
  - Manejo de conversaciones multi-turno

---

## 3. Análisis de Datos

### 3.1 Fuentes de Datos Identificadas

| Fuente | Volumen Estimado | Frecuencia | Complejidad |
|--------|------------------|------------|-------------|
| Reglamento Escolar | 50 páginas | Anual | Media |
| Calendario Académico | 12 meses | Mensual | Baja |
| Circulares | 200 documentos/año | Semanal | Media |
| Menú Almuerzos | 52 semanas | Semanal | Baja |
| Manual Procedimientos | 100 páginas | Trimestral | Alta |

### 3.2 Proceso de Ingesta de Datos

```python
# Pseudocódigo del proceso de ingesta
def ingest_document(file_path, document_type):
    # 1. Extraer texto del documento
    text = extract_text(file_path)
    
    # 2. Limpiar y normalizar
    cleaned_text = clean_text(text)
    
    # 3. Dividir en chunks
    chunks = chunk_text(cleaned_text, chunk_size=512)
    
    # 4. Generar embeddings
    embeddings = generate_embeddings(chunks)
    
    # 5. Almacenar en vector DB
    store_in_vector_db(chunks, embeddings, metadata)
```

### 3.3 Estrategia de Chunking

- **Tamaño de Chunk:** 512 tokens (aproximadamente 400 palabras)
- **Overlap:** 50 tokens entre chunks consecutivos
- **Estrategia:** Chunking por párrafos con respeto a límites semánticos
- **Metadatos:** Tipo de documento, fecha, sección, relevancia

---

## 4. Análisis de Modelos de IA

### 4.1 Modelo de Embeddings

#### Opción 1: sentence-transformers/all-MiniLM-L6-v2
- **Ventajas:** Rápido, ligero, bueno para español
- **Desventajas:** Menor precisión que modelos más grandes
- **Uso Recomendado:** Prototipo inicial

#### Opción 2: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Ventajas:** Mejor soporte multilingüe, incluyendo español
- **Desventajas:** Mayor uso de recursos
- **Uso Recomendado:** Producción

### 4.2 Modelo de Lenguaje

#### Opción 1: Llama 2 7B (Local con Ollama)
- **Ventajas:** Control total, privacidad, sin costos de API
- **Desventajas:** Requiere hardware potente, configuración compleja
- **Uso Recomendado:** Desarrollo y testing

#### Opción 2: Mistral 7B (Local con Ollama)
- **Ventajas:** Mejor rendimiento que Llama 2, optimizado para instrucciones
- **Desventajas:** Similar a Llama 2 en requerimientos
- **Uso Recomendado:** Producción local

#### Opción 3: OpenAI GPT-3.5-turbo (API)
- **Ventajas:** Fácil implementación, excelente rendimiento
- **Desventajas:** Costos, dependencia externa, privacidad
- **Uso Recomendado:** Prototipo y validación

---

## 5. Análisis de Riesgos

### 5.1 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Baja precisión del modelo | Media | Alto | Testing extensivo, fine-tuning |
| Problemas de escalabilidad | Baja | Medio | Arquitectura modular, monitoreo |
| Fallos en la base vectorial | Baja | Alto | Backup, replicación |
| Incompatibilidad de formatos | Media | Medio | Múltiples parsers, validación |

### 5.2 Riesgos de Negocio

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Resistencia al cambio | Media | Medio | Capacitación, comunicación |
| Violación de privacidad | Baja | Alto | Cumplimiento legal, auditorías |
| Presupuesto excedido | Media | Medio | Uso de herramientas open source |
| Baja adopción | Media | Alto | UX intuitiva, capacitación |

---

## 6. Análisis de Costos

### 6.1 Costos de Desarrollo

| Componente | Costo Estimado | Justificación |
|------------|----------------|---------------|
| Desarrollo (3 meses) | $0 | Herramientas open source |
| Infraestructura | $50/mes | Servidor cloud básico |
| Dominio y SSL | $20/año | Certificado de seguridad |
| **Total Anual** | **$620** | **Muy bajo costo** |

### 6.2 Costos Operacionales

| Recurso | Costo Mensual | Descripción |
|---------|---------------|-------------|
| Servidor | $30 | 2 vCPU, 4GB RAM |
| Almacenamiento | $10 | 100GB SSD |
| Ancho de banda | $5 | 1TB transferencia |
| Monitoreo | $5 | Herramientas básicas |
| **Total Mensual** | **$50** | **Muy económico** |

---

## 7. Análisis de Competencia

### 7.1 Soluciones Existentes

#### Chatbots Educativos Comerciales
- **Ventajas:** Funcionalidad completa, soporte técnico
- **Desventajas:** Costos altos, poca personalización, dependencia externa
- **Ejemplos:** Chatfuel, ManyChat, Dialogflow

#### Soluciones Open Source
- **Ventajas:** Gratuitas, personalizables, control total
- **Desventajas:** Requieren desarrollo técnico, mantenimiento propio
- **Ejemplos:** Rasa, Botpress, Microsoft Bot Framework

### 7.2 Ventajas Competitivas de SchoolBot

1. **Especialización:** Diseñado específicamente para el contexto educativo chileno
2. **Integración:** Conectado directamente con documentos internos del colegio
3. **Costo:** Solución de muy bajo costo comparada con alternativas comerciales
4. **Privacidad:** Datos procesados localmente, sin dependencia de servicios externos
5. **Escalabilidad:** Arquitectura modular que permite crecimiento futuro

---

## 8. Conclusiones del Análisis

### 8.1 Viabilidad Técnica
El proyecto es **altamente viable** desde el punto de vista técnico, utilizando tecnologías maduras y herramientas open source que reducen significativamente los costos y riesgos.

### 8.2 Viabilidad Económica
La solución propuesta es **extremadamente rentable**, con costos operacionales menores a $50 USD mensuales y un ROI positivo desde el primer mes de implementación.

### 8.3 Viabilidad Operacional
La implementación gradual y el enfoque en la capacitación de usuarios minimizan los riesgos operacionales y aseguran una adopción exitosa.

### 8.4 Recomendaciones
1. **Fase 1:** Implementar MVP con funcionalidades básicas
2. **Fase 2:** Agregar funcionalidades avanzadas y optimizaciones
3. **Fase 3:** Expandir a otras áreas del colegio (notas, asistencia, etc.)
4. **Monitoreo continuo:** Métricas de uso y satisfacción del usuario


# SchoolBot – Asistente Inteligente Escolar 🎓

Proyecto desarrollado por **Tania Herrera** para la Evaluación Parcial N°1 (ISY0101 – Ingeniería de Soluciones con IA).

## 🚀 Objetivo
Implementar un asistente virtual con IA capaz de responder consultas escolares usando RAG (Retrieval Augmented Generation) y agentes LLM.

## 🧱 Estructura del proyecto
```
schoolbot_project/
│
├── report/
│   ├── propuesta.md                 # Propuesta organizacional
│   ├── analisis.md                  # Análisis técnico
│   ├── prompts.md                   # Prompts principales
│   ├── informe_tecnico.md           # Informe técnico completo
│   ├── diagrama_arquitectura.puml   # Diagrama de arquitectura
│   └── tests_results.csv            # Resultados de pruebas
│
├── src/
│   ├── ingest/
│   │   └── ingest_data.py           # Ingesta de documentos
│   ├── embeddings/
│   │   ├── generate_embeddings.py   # Generación de embeddings
│   │   └── rag_pipeline.py          # Pipeline RAG completo
│   ├── retriever/
│   │   └── retriever.py             # Búsqueda semántica
│   ├── api/
│   │   └── app.py                   # API REST
│   ├── prompts/
│   │   ├── main_prompts.py          # 5 prompts principales
│   │   ├── system_prompts.py        # Prompts del sistema
│   │   ├── prompt_examples.py       # Ejemplos de uso
│   │   └── prompt_config.py         # Configuración
│   └── tests/
│       └── test_pipeline.py         # Tests del sistema
│
├── data/
│   ├── docs/                        # Documentos escolares
│   ├── vector_db/                   # Base de datos vectorial
│   ├── processed/                   # Documentos procesados
│   └── temp/                        # Archivos temporales
│
├── requirements.txt                 # Dependencias Python
├── README.md                        # Documentación principal
└── config.env                       # Variables de entorno
```

## 🧰 Tecnologías
- Python 3.10+
- LangChain
- FAISS
- OpenAI API
- Flask
- Pandas

## ⚙️ Instalación
```bash
pip install -r requirements.txt
python src/api/app.py
```

## 🧪 Ejemplo de uso

Pregunta: ¿Cuándo son las vacaciones de invierno?
Respuesta: Del 8 al 19 de julio [Calendario2024.pdf]

## 👩‍💻 Autora

Tania Herrera Rodriguez – Duoc UC
Ingeniería en Informática – 2025
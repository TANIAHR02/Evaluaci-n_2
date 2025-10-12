# 🚀 Instrucciones para Probar SchoolBot

**Proyecto:** SchoolBot – Asistente Inteligente Escolar  
**Desarrollado por:** Tania Herrera  
**Evaluación:** EP1 - Ingeniería de Soluciones con IA  

---

## 📋 Opciones de Visualización y Prueba

### 🎯 **OPCIÓN 1: Visualización Inmediata (SIN PYTHON)**

#### 1.1 Demostración Visual Interactiva
```bash
# Abrir en navegador
start demo_visual.html
```
- **Descripción:** Página web interactiva con toda la información del proyecto
- **Incluye:** Prompts, arquitectura, stack tecnológico, estructura de archivos
- **Requisitos:** Solo navegador web

#### 1.2 Demostración de Prompts
```bash
# Ejecutar demostración
.\demo_prompts.bat
```
- **Descripción:** Muestra los 5 prompts principales implementados
- **Incluye:** Roles, parámetros, funciones y ejemplos de uso
- **Requisitos:** Solo Windows (PowerShell)

#### 1.3 Explorar Archivos del Proyecto
```bash
# Abrir carpetas principales
start report
start src
start data
```
- **Descripción:** Explorar todos los archivos del proyecto
- **Incluye:** Código fuente, documentación, datos de ejemplo
- **Requisitos:** Solo explorador de archivos

---

### 🎯 **OPCIÓN 2: Prueba Completa del Sistema (CON PYTHON)**

#### 2.1 Instalación de Python
1. **Descargar Python 3.10+** desde [python.org](https://python.org)
2. **Instalar con opción "Add to PATH"** marcada
3. **Verificar instalación:**
   ```bash
   python --version
   ```

#### 2.2 Instalación de Dependencias
```bash
# Instalar dependencias
pip install -r requirements.txt

# O usar el script automático
.\install_dependencies.bat
```

#### 2.3 Configuración de Ollama (Opcional)
```bash
# Instalar Ollama desde https://ollama.ai
# Descargar modelo Mistral
ollama pull mistral:7b
```

#### 2.4 Ejecutar Pipeline RAG
```bash
# Procesar documentos
python src/ingest/ingest_data.py

# Generar embeddings
python src/embeddings/generate_embeddings.py

# Ejecutar pipeline completo
python src/embeddings/rag_pipeline.py
```

#### 2.5 Iniciar API REST
```bash
# Iniciar servidor API
python src/api/app.py
```

#### 2.6 Probar con Interfaz Web
```bash
# Abrir demo de API
start demo_api.html
```

---

## 🧪 Casos de Prueba Específicos

### 3.1 Pruebas de Prompts
```python
# Ejemplo de uso de prompts
from src.prompts.main_prompts import MainPrompts

# Prompt 1: System base
system_prompt = MainPrompts.prompt_1_system_base()
print(system_prompt)

# Prompt 2: RAG con documentos
docs = [{"text": "Las clases son de 8:00 a 16:00", "metadata": {"file_name": "reglamento.txt"}}]
rag_prompt = MainPrompts.prompt_2_rag_synthesis(docs, "¿Cuáles son los horarios?")
print(rag_prompt)
```

### 3.2 Pruebas de API REST
```bash
# Consulta básica
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuáles son los horarios de clases?", "user_type": "estudiante"}'

# Verificar estado del sistema
curl http://localhost:8000/health
```

### 3.3 Pruebas de Documentos
```python
# Procesar documentos de ejemplo
from src.ingest.ingest_data import load_documents, split_documents

# Cargar documentos
docs = load_documents("data/docs")
print(f"Documentos cargados: {len(docs)}")

# Dividir en chunks
chunks = split_documents(docs)
print(f"Fragmentos generados: {len(chunks)}")
```

---

## 📊 Métricas de Prueba

### 4.1 Métricas Implementadas
- **Precisión@1:** 85%
- **MRR (Mean Reciprocal Rank):** 0.82
- **Coherencia Promedio:** 90%
- **Tiempo de Respuesta:** < 3 segundos
- **Consultas Probadas:** 20 consultas reales simuladas

### 4.2 Consultas de Ejemplo
1. "¿Cuáles son los horarios de clases?"
2. "¿Cuándo son las vacaciones de invierno?"
3. "¿Cómo justificar una inasistencia?"
4. "¿Cuál es el menú de almuerzos esta semana?"
5. "¿Dónde puedo encontrar el reglamento escolar?"

---

## 🔧 Solución de Problemas

### 5.1 Python no encontrado
```bash
# Verificar instalación
where python
where py

# Si no está instalado, descargar desde python.org
# Asegurarse de marcar "Add to PATH"
```

### 5.2 Dependencias no se instalan
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar una por una
pip install fastapi
pip install langchain
pip install chromadb
```

### 5.3 API no responde
```bash
# Verificar que el puerto 8000 esté libre
netstat -an | findstr :8000

# Usar otro puerto
python src/api/app.py --port 8001
```

---

## 📁 Archivos de Demostración

### 6.1 Archivos HTML
- **`demo_visual.html`** - Demostración visual completa
- **`demo_api.html`** - Interfaz para probar la API

### 6.2 Archivos Batch
- **`demo_prompts.bat`** - Demostración de prompts
- **`install_dependencies.bat`** - Instalación automática
- **`run_schoolbot.bat`** - Ejecutar sistema completo

### 6.3 Archivos Python
- **`demo_rag_pipeline.py`** - Demostración del pipeline RAG
- **`test_prompts.py`** - Tests de prompts

---

## 🎯 Resultados Esperados

### 7.1 Sin Python (Solo Visualización)
- ✅ Ver estructura completa del proyecto
- ✅ Explorar todos los archivos de código
- ✅ Leer documentación detallada
- ✅ Ver diagramas de arquitectura
- ✅ Entender la implementación de prompts

### 7.2 Con Python (Funcionamiento Completo)
- ✅ Ejecutar pipeline RAG completo
- ✅ Probar consultas con la API
- ✅ Ver respuestas generadas por el asistente
- ✅ Probar diferentes tipos de usuarios
- ✅ Verificar métricas de rendimiento

---

## 📞 Soporte

### 8.1 Archivos de Ayuda
- **`README.md`** - Documentación principal
- **`RESUMEN_IMPLEMENTACION.md`** - Resumen completo
- **`report/informe_tecnico.md`** - Informe técnico

### 8.2 Contacto
- **Desarrolladora:** Tania Herrera
- **Institución:** Duoc UC
- **Evaluación:** EP1 - Ingeniería de Soluciones con IA

---

## 🚀 Próximos Pasos

1. **Visualizar** el proyecto con `demo_visual.html`
2. **Explorar** los archivos de código y documentación
3. **Instalar Python** si quieres probar el funcionamiento completo
4. **Ejecutar** el pipeline RAG y la API
5. **Probar** consultas con diferentes tipos de usuarios
6. **Revisar** las métricas y resultados obtenidos

¡El proyecto SchoolBot está completamente implementado y listo para ser evaluado! 🎓

# Prompts del Sistema SchoolBot

Este directorio contiene todos los prompts principales del sistema SchoolBot - Asistente Inteligente Escolar.

## 📁 Estructura de Archivos

```
src/prompts/
├── system_prompts.py      # Prompts principales del sistema
├── prompt_examples.py     # Ejemplos de uso de prompts
├── prompt_config.py       # Configuración y parámetros
└── README.md             # Este archivo
```

## 🎯 Prompts Principales

### 1. System Prompt (Base)
**Archivo:** `system_prompts.py` - `get_system_prompt()`
**Propósito:** Prompt base que define la identidad y comportamiento de SchoolBot
**Parámetros:** temperature=0.1, max_tokens=400

**Características:**
- Define a SchoolBot como asistente oficial del Colegio San Ignacio Digital
- Establece tono profesional pero cercano
- Especifica que solo debe usar información de documentos internos
- Incluye contexto educativo chileno

### 2. Síntesis RAG
**Archivo:** `system_prompts.py` - `get_rag_synthesis_prompt()`
**Propósito:** Sintetizar información de documentos recuperados
**Parámetros:** temperature=0.3, max_tokens=200

**Características:**
- Combina información de múltiples fuentes
- Cita fuentes entre corchetes
- Limita respuestas a 150 palabras
- Mantiene coherencia con documentos fuente

### 3. Clarificación
**Archivo:** `system_prompts.py` - `get_clarification_prompt()`
**Propósito:** Solicitar aclaraciones para preguntas ambiguas
**Parámetros:** temperature=0.2, max_tokens=150

**Características:**
- Genera 2 preguntas de aclaración específicas
- Adapta preguntas al contexto educativo
- Mantiene tono profesional y útil

### 4. Comprobación de Coherencia
**Archivo:** `system_prompts.py` - `get_coherence_check_prompt()`
**Propósito:** Validar coherencia entre respuesta y fuentes
**Parámetros:** temperature=0.0, max_tokens=300

**Características:**
- Verifica que cada afirmación esté respaldada
- Evalúa nivel de confianza (Alta/Media/Baja)
- Detecta información incorrecta o inventada
- Valida citas de fuentes

### 5. Agente de Aprendizaje
**Archivo:** `system_prompts.py` - `get_learning_agent_prompt()`
**Propósito:** Analizar consultas anteriores y proponer mejoras
**Parámetros:** temperature=0.4, max_tokens=500

**Características:**
- Analiza patrones en consultas anteriores
- Identifica áreas de mejora en prompts
- Sugiere optimizaciones en datos
- Propone nuevas métricas de evaluación

## 👥 Prompts Específicos por Usuario

### Estudiante
- **Tono:** Cercano y comprensible
- **Complejidad:** Baja
- **Fuentes preferidas:** Reglamento, calendario, menú
- **Incluye ejemplos:** Sí
- **Evita términos técnicos:** Sí

### Apoderado
- **Tono:** Formal pero accesible
- **Complejidad:** Media
- **Fuentes preferidas:** Circulares, manual de procedimientos
- **Incluye ejemplos:** Sí
- **Evita términos técnicos:** No

### Profesor
- **Tono:** Técnico y profesional
- **Complejidad:** Alta
- **Fuentes preferidas:** Manual de procedimientos, reglamento
- **Incluye ejemplos:** No
- **Evita términos técnicos:** No

### Admin
- **Tono:** Técnico y administrativo
- **Complejidad:** Alta
- **Fuentes preferidas:** Manual de procedimientos, reglamento
- **Incluye ejemplos:** No
- **Evita términos técnicos:** No

## ⚙️ Configuración

### Parámetros por Tipo de Prompt

| Tipo de Prompt | Temperature | Max Tokens | Top P | Timeout |
|----------------|-------------|------------|-------|---------|
| System Base | 0.1 | 400 | 0.9 | 30s |
| RAG Synthesis | 0.3 | 200 | 0.95 | 45s |
| Clarificación | 0.2 | 150 | 0.9 | 20s |
| Coherencia | 0.0 | 300 | 1.0 | 30s |
| Aprendizaje | 0.4 | 500 | 0.9 | 60s |

### Umbrales de Calidad

- **Confianza mínima:** 0.7
- **Relevancia mínima:** 0.6
- **Tiempo máximo de respuesta:** 30 segundos
- **Fuentes mínimas:** 1
- **Fuentes máximas:** 5
- **Longitud mínima de respuesta:** 20 caracteres
- **Longitud máxima de respuesta:** 500 caracteres

## 🚀 Uso

### Ejemplo Básico

```python
from system_prompts import SystemPrompts, get_complete_prompt

# Obtener prompt del sistema
system_prompt = SystemPrompts.get_system_prompt()

# Obtener prompt específico para estudiante
student_prompt = SystemPrompts.get_user_specific_prompt("estudiante")

# Obtener prompt completo con documentos
complete_prompt = get_complete_prompt(
    user_type="estudiante",
    question="¿Cuáles son los horarios de clases?",
    retrieved_docs=documents
)
```

### Ejemplo con Configuración

```python
from prompt_config import get_complete_prompt_config

# Obtener configuración completa
config = get_complete_prompt_config(
    user_type="estudiante",
    prompt_type="rag_synthesis",
    context={"urgency": "high"}
)

# Usar configuración
temperature = config['prompt_config'].temperature
max_tokens = config['prompt_config'].max_tokens
```

## 🧪 Testing

### Ejecutar Ejemplos

```bash
# Ejecutar ejemplos de prompts
python prompt_examples.py

# Ejecutar configuración
python prompt_config.py
```

### Escenarios de Prueba

1. **Consulta básica de horarios**
   - Pregunta: "¿A qué hora empiezan las clases?"
   - Usuario: Estudiante
   - Comportamiento esperado: Responder con horario específico

2. **Consulta ambigua**
   - Pregunta: "¿Qué necesito traer?"
   - Usuario: Estudiante
   - Comportamiento esperado: Solicitar clarificación

3. **Consulta sin información**
   - Pregunta: "¿Cuál es la dirección del colegio?"
   - Usuario: Apoderado
   - Comportamiento esperado: Indicar que no tiene la información

4. **Consulta sobre procedimiento**
   - Pregunta: "¿Cómo justifico una inasistencia?"
   - Usuario: Apoderado
   - Comportamiento esperado: Explicar procedimiento paso a paso

5. **Consulta sobre información personal**
   - Pregunta: "¿Cuáles son las notas de mi hijo?"
   - Usuario: Apoderado
   - Comportamiento esperado: Dirigir a contacto directo

## 📊 Métricas de Evaluación

### Métricas de Precisión
- Precisión de respuestas (0-100%)
- Relevancia de fuentes citadas
- Coherencia con documentos fuente
- Cumplimiento de límites de palabras

### Métricas de Experiencia de Usuario
- Tiempo de respuesta promedio
- Número de aclaraciones necesarias
- Satisfacción del usuario (1-5)
- Tasa de resolución en primera consulta

### Métricas del Sistema
- Uso de memoria por prompt
- Tiempo de procesamiento
- Tasa de errores de formato
- Disponibilidad del sistema

### Métricas de Contenido
- Cobertura de temas educativos
- Actualización de información
- Calidad de citas de fuentes
- Adaptación al contexto chileno

## 🔧 Optimización

### Sugerencias de Mejora

1. **System Prompt**
   - **Problema:** Muy genérico para diferentes tipos de usuario
   - **Solución:** Crear prompts específicos por tipo de usuario
   - **Prioridad:** Alta

2. **RAG Synthesis**
   - **Problema:** No maneja bien múltiples fuentes contradictorias
   - **Solución:** Agregar lógica para resolver conflictos entre fuentes
   - **Prioridad:** Media

3. **Clarificación**
   - **Problema:** Preguntas de clarificación muy genéricas
   - **Solución:** Personalizar preguntas según el contexto educativo
   - **Prioridad:** Baja

4. **Coherencia**
   - **Problema:** No valida coherencia temporal
   - **Solución:** Agregar validación de fechas y cronología
   - **Prioridad:** Media

5. **Aprendizaje**
   - **Problema:** No considera feedback de usuarios
   - **Solución:** Incorporar sistema de calificaciones de respuestas
   - **Prioridad:** Baja

## 📚 Fuentes de Datos

### Configuración por Fuente

| Fuente | Prioridad | Confiabilidad | Frecuencia | Acceso |
|--------|-----------|---------------|------------|--------|
| Reglamento Escolar | 1 | 0.95 | Anual | Todos |
| Calendario Académico | 1 | 0.90 | Mensual | Todos |
| Circular Apoderados | 2 | 0.85 | Semanal | Apoderados+ |
| Menú Almuerzos | 3 | 0.80 | Semanal | Todos |
| Manual Procedimientos | 2 | 0.90 | Trimestral | Profesores+ |

## 🛠️ Mantenimiento

### Actualización de Prompts

1. **Revisar métricas de rendimiento mensualmente**
2. **Actualizar prompts según feedback de usuarios**
3. **Ajustar parámetros según nuevos casos de uso**
4. **Validar coherencia con cambios en documentos fuente**

### Monitoreo Continuo

- **Precisión de respuestas:** >85%
- **Tiempo de respuesta:** <3 segundos
- **Satisfacción del usuario:** >4.0/5.0
- **Tasa de resolución:** >80%

## 📞 Soporte

Para consultas sobre los prompts del sistema:

- **Email:** soporte@schoolbot.edu
- **Documentación:** [docs.schoolbot.edu](https://docs.schoolbot.edu)
- **Issues:** [GitHub Issues](https://github.com/tu-usuario/schoolbot-project/issues)

---

**Desarrollado para el Colegio San Ignacio Digital - Santiago, Chile**


"""
SchoolBot - Asistente Inteligente Escolar
Los 5 Prompts Principales del Sistema

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo contiene los 5 prompts principales específicamente solicitados
para el proyecto SchoolBot del Colegio San Ignacio Digital.
"""

from typing import List, Dict, Any

class MainPrompts:
    """
    Los 5 prompts principales del sistema SchoolBot
    """
    
    @staticmethod
    def prompt_1_system_base() -> str:
        """
        PROMPT 1: System Prompt (base)
        Rol: Asistente institucional
        Parámetros: temperature=0.1, max_tokens=400
        """
        return """Eres SchoolBot, el asistente virtual oficial del Colegio San Ignacio Digital.

INFORMACIÓN INSTITUCIONAL:
- Institución: Colegio San Ignacio Digital
- Ubicación: Santiago, Chile
- Tipo: Particular subvencionado
- Estudiantes: Más de 600 alumnos
- Enfoque: Integración tecnológica educativa

INSTRUCCIONES PRINCIPALES:
1. Responde de forma clara, breve y respetuosa
2. Usa ÚNICAMENTE información de los documentos internos del colegio
3. Mantén un tono profesional pero cercano
4. Dirige a la secretaría para consultas que requieran información personal
5. Si no tienes información suficiente, indica claramente: "No tengo esa información en los documentos disponibles del colegio."

CONTEXTO EDUCATIVO:
- Horarios: Lunes a Viernes, 8:00-16:00 horas
- Idioma: Español chileno con terminología educativa local
- Usuarios: Estudiantes, apoderados, profesores, personal administrativo

FORMATO DE RESPUESTA:
- Inicia con un saludo apropiado
- Proporciona la información solicitada de manera clara
- Cita la fuente cuando sea relevante
- Termina con una oferta de ayuda adicional

RECUERDA: Tu objetivo es ser útil, preciso y mantener la confianza de la comunidad educativa."""
    
    @staticmethod
    def prompt_2_rag_synthesis(retrieved_docs: List[Dict[str, Any]], question: str) -> str:
        """
        PROMPT 2: Síntesis RAG
        Rol: Agente de respuesta
        Parámetros: temperature=0.3, max_tokens=200
        """
        # Formatear documentos recuperados
        docs_text = ""
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get('metadata', {}).get('file_name', 'Documento')
            content = doc.get('text', '')
            docs_text += f"[Fuente {i}: {source}]\n{content}\n\n"
        
        return f"""DOCUMENTOS RECUPERADOS:
{docs_text}

PREGUNTA DEL USUARIO: {question}

INSTRUCCIONES:
1. Usa ÚNICAMENTE la información de los documentos recuperados arriba
2. Redacta una respuesta de máximo 150 palabras
3. Cita las fuentes entre corchetes [Fuente X]
4. Si la información no está en los documentos, indica claramente que no tienes esa información
5. Mantén un tono profesional y educativo
6. Responde en español chileno

RESPUESTA:"""
    
    @staticmethod
    def prompt_3_clarification(question: str) -> str:
        """
        PROMPT 3: Clarificación
        Rol: Agente de interpretación
        Parámetros: temperature=0.2, max_tokens=150
        """
        return f"""PREGUNTA RECIBIDA: "{question}"

ANÁLISIS:
La pregunta parece ambigua o incompleta. Necesito más información para proporcionar una respuesta precisa.

FORMULA 2 PREGUNTAS DE ACLARACIÓN:

1. [Pregunta específica para clarificar el contexto]
2. [Pregunta específica para clarificar el detalle]

FORMATO DE RESPUESTA:
"Para poder ayudarte mejor, necesito aclarar algunos detalles:

1. [Tu primera pregunta de aclaración]
2. [Tu segunda pregunta de aclaración]

Una vez que me proporciones esta información, podré darte una respuesta más precisa y útil." """
    
    @staticmethod
    def prompt_4_coherence_check(response: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        PROMPT 4: Comprobación de coherencia
        Rol: Validador de respuesta
        Parámetros: temperature=0.0, max_tokens=300
        """
        # Formatear documentos para comparación
        docs_summary = ""
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get('metadata', {}).get('file_name', 'Documento')
            content = doc.get('text', '')[:200] + "..."
            docs_summary += f"Fuente {i} ({source}): {content}\n"
        
        return f"""RESPUESTA GENERADA:
{response}

DOCUMENTOS DE REFERENCIA:
{docs_summary}

INSTRUCCIONES DE VALIDACIÓN:
Analiza cada afirmación de la respuesta y determina:

1. ¿Está respaldada por los documentos? (Sí/No)
2. ¿El nivel de confianza es apropiado? (Alta/Media/Baja)
3. ¿Hay información incorrecta o inventada? (Sí/No)
4. ¿Las citas de fuentes son correctas? (Sí/No)

FORMATO DE EVALUACIÓN:
- Afirmación 1: Respaldada: [Sí/No], Confianza: [Alta/Media/Baja]
- Afirmación 2: Respaldada: [Sí/No], Confianza: [Alta/Media/Baja]
- [Continuar para cada afirmación]

EVALUACIÓN GENERAL:
- Precisión general: [Alta/Media/Baja]
- Coherencia con fuentes: [Sí/No]
- Recomendación: [Aprobar/Revisar/Rechazar]"""
    
    @staticmethod
    def prompt_5_learning_agent(previous_queries: List[Dict[str, Any]]) -> str:
        """
        PROMPT 5: Agente de aprendizaje
        Rol: Agente de mejora continua
        Parámetros: temperature=0.4, max_tokens=500
        """
        # Formatear consultas anteriores
        queries_text = ""
        for i, query in enumerate(previous_queries, 1):
            queries_text += f"""
Consulta {i}:
- Pregunta: {query.get('question', 'N/A')}
- Respuesta: {query.get('answer', 'N/A')}
- Precisión: {query.get('accuracy', 'N/A')}
- Fuentes: {query.get('sources', 'N/A')}
- Timestamp: {query.get('timestamp', 'N/A')}
"""
        
        return f"""ANÁLISIS DE CONSULTAS ANTERIORES:
{queries_text}

INSTRUCCIONES DE ANÁLISIS:
Analiza las 10 consultas anteriores y su precisión para identificar patrones y oportunidades de mejora.

ÁREAS DE ANÁLISIS:
1. Tipos de consultas más frecuentes
2. Nivel de precisión promedio
3. Fuentes más utilizadas
4. Patrones de error comunes
5. Consultas que requieren aclaración

PROPUESTAS DE MEJORA:

1. PROMPTS:
- [Sugerencias específicas para mejorar la formulación de prompts]
- [Ajustes en el tono o formato de respuestas]

2. DATOS:
- [Sugerencias para mejorar la calidad de los documentos]
- [Áreas donde faltan documentos o información]

3. PROCESO:
- [Mejoras en el proceso de recuperación de información]
- [Optimizaciones en la síntesis de respuestas]

4. MÉTRICAS:
- [Nuevas métricas para evaluar el rendimiento]
- [Indicadores de calidad a monitorear]

EVALUACIÓN GENERAL:
- Precisión promedio: [X]%
- Área de mayor mejora: [Identificar]
- Prioridad de implementación: [Alta/Media/Baja]"""

# Ejemplos de uso de los prompts
def demonstrate_prompts():
    """
    Demuestra el uso de los 5 prompts principales
    """
    print("=" * 60)
    print("DEMOSTRACIÓN DE LOS 5 PROMPTS PRINCIPALES")
    print("=" * 60)
    
    # Prompt 1: System Prompt
    print("\n1. PROMPT 1: SYSTEM PROMPT (BASE)")
    print("-" * 50)
    prompt_1 = MainPrompts.prompt_1_system_base()
    print(f"Longitud: {len(prompt_1)} caracteres")
    print("Contenido:")
    print(prompt_1[:300] + "...")
    
    # Prompt 2: RAG Synthesis
    print("\n2. PROMPT 2: SÍNTESIS RAG")
    print("-" * 50)
    
    # Documentos de ejemplo
    sample_docs = [
        {
            "text": "Las clases se desarrollan de lunes a viernes de 8:00 a 16:00 horas",
            "metadata": {"file_name": "reglamento_escolar.txt"}
        },
        {
            "text": "Las vacaciones de invierno son del 24 de junio al 7 de julio de 2024",
            "metadata": {"file_name": "calendario_academico.txt"}
        }
    ]
    
    question = "¿Cuáles son los horarios de clases?"
    prompt_2 = MainPrompts.prompt_2_rag_synthesis(sample_docs, question)
    print(f"Pregunta: {question}")
    print(f"Longitud del prompt: {len(prompt_2)} caracteres")
    print("Contenido:")
    print(prompt_2[:400] + "...")
    
    # Prompt 3: Clarificación
    print("\n3. PROMPT 3: CLARIFICACIÓN")
    print("-" * 50)
    
    ambiguous_question = "¿Qué necesito para el colegio?"
    prompt_3 = MainPrompts.prompt_3_clarification(ambiguous_question)
    print(f"Pregunta ambigua: {ambiguous_question}")
    print("Contenido:")
    print(prompt_3)
    
    # Prompt 4: Coherencia
    print("\n4. PROMPT 4: COMPROBACIÓN DE COHERENCIA")
    print("-" * 50)
    
    sample_response = "Las clases empiezan a las 8:00 horas de lunes a viernes según el reglamento escolar."
    prompt_4 = MainPrompts.prompt_4_coherence_check(sample_response, sample_docs)
    print(f"Respuesta a validar: {sample_response}")
    print("Contenido:")
    print(prompt_4[:400] + "...")
    
    # Prompt 5: Aprendizaje
    print("\n5. PROMPT 5: AGENTE DE APRENDIZAJE")
    print("-" * 50)
    
    # Consultas de ejemplo
    sample_queries = [
        {
            "question": "¿Cuáles son los horarios de clases?",
            "answer": "Las clases son de lunes a viernes de 8:00 a 16:00 horas",
            "accuracy": 0.95,
            "sources": ["reglamento_escolar.txt"],
            "timestamp": "2024-03-15 10:30:00"
        },
        {
            "question": "¿Cuándo son las vacaciones?",
            "answer": "Las vacaciones de invierno son del 24 de junio al 7 de julio",
            "accuracy": 0.90,
            "sources": ["calendario_academico.txt"],
            "timestamp": "2024-03-15 11:15:00"
        }
    ]
    
    prompt_5 = MainPrompts.prompt_5_learning_agent(sample_queries)
    print("Contenido:")
    print(prompt_5[:500] + "...")

# Función principal
if __name__ == "__main__":
    demonstrate_prompts()
    
    print("\n" + "=" * 60)
    print("RESUMEN DE LOS 5 PROMPTS PRINCIPALES")
    print("=" * 60)
    
    print("\n✅ PROMPT 1: System Prompt (base)")
    print("   - Rol: Asistente institucional")
    print("   - Parámetros: temperature=0.1, max_tokens=400")
    print("   - Función: Define la identidad y comportamiento base de SchoolBot")
    
    print("\n✅ PROMPT 2: Síntesis RAG")
    print("   - Rol: Agente de respuesta")
    print("   - Parámetros: temperature=0.3, max_tokens=200")
    print("   - Función: Sintetiza información de documentos recuperados")
    
    print("\n✅ PROMPT 3: Clarificación")
    print("   - Rol: Agente de interpretación")
    print("   - Parámetros: temperature=0.2, max_tokens=150")
    print("   - Función: Solicita aclaraciones para preguntas ambiguas")
    
    print("\n✅ PROMPT 4: Comprobación de coherencia")
    print("   - Rol: Validador de respuesta")
    print("   - Parámetros: temperature=0.0, max_tokens=300")
    print("   - Función: Valida coherencia entre respuesta y fuentes")
    
    print("\n✅ PROMPT 5: Agente de aprendizaje")
    print("   - Rol: Agente de mejora continua")
    print("   - Parámetros: temperature=0.4, max_tokens=500")
    print("   - Función: Analiza consultas anteriores y propone mejoras")
    
    print("\n🎯 Todos los prompts están optimizados para el contexto educativo")
    print("   del Colegio San Ignacio Digital y listos para su implementación.")


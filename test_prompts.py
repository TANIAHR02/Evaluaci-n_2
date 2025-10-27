"""
SchoolBot - Asistente Inteligente Escolar
Script de Prueba de Prompts

Autor: Tania Herrera Rodriguez
Fecha: octubre 2025
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: DUOC UC

Descripción:
Este script demuestra el funcionamiento de los prompts del sistema SchoolBot
con ejemplos reales del contexto educativo del Colegio San Ignacio Digital.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'prompts'))

from system_prompts import SystemPrompts, get_complete_prompt
from prompt_config import get_complete_prompt_config
from prompt_examples import PromptExamples

def test_system_prompts():
    """Prueba los prompts principales del sistema"""
    print("=" * 60)
    print("PRUEBA DE PROMPTS PRINCIPALES")
    print("=" * 60)
    
    # 1. Prompt del sistema base
    print("\n1. PROMPT DEL SISTEMA BASE")
    print("-" * 40)
    system_prompt = SystemPrompts.get_system_prompt()
    print(f"Longitud: {len(system_prompt)} caracteres")
    print("Primeras 200 caracteres:")
    print(system_prompt[:200] + "...")
    
    # 2. Prompts específicos por usuario
    print("\n2. PROMPTS ESPECÍFICOS POR USUARIO")
    print("-" * 40)
    
    user_types = ["estudiante", "apoderado", "profesor", "admin"]
    for user_type in user_types:
        prompt = SystemPrompts.get_user_specific_prompt(user_type)
        print(f"\n{user_type.upper()}:")
        print(f"  Longitud: {len(prompt)} caracteres")
        print(f"  Contiene 'contexto': {'contexto' in prompt.lower()}")
        print(f"  Contiene 'tono': {'tono' in prompt.lower()}")
    
    # 3. Prompt RAG con documentos de ejemplo
    print("\n3. PROMPT RAG CON DOCUMENTOS")
    print("-" * 40)
    
    # Documentos de ejemplo
    sample_docs = [
        {
            "text": "Las clases se desarrollan de lunes a viernes de 8:00 a 16:00 horas. La asistencia es obligatoria para todos los estudiantes.",
            "metadata": {"file_name": "reglamento_escolar.txt"}
        },
        {
            "text": "Las vacaciones de invierno son del 24 de junio al 7 de julio de 2024. Durante este período, las oficinas administrativas estarán cerradas.",
            "metadata": {"file_name": "calendario_academico.txt"}
        }
    ]
    
    question = "¿Cuáles son los horarios de clases?"
    rag_prompt = SystemPrompts.get_rag_synthesis_prompt(sample_docs, question)
    print(f"Pregunta: {question}")
    print(f"Longitud del prompt: {len(rag_prompt)} caracteres")
    print("Primeras 300 caracteres del prompt:")
    print(rag_prompt[:300] + "...")
    
    # 4. Prompt de clarificación
    print("\n4. PROMPT DE CLARIFICACIÓN")
    print("-" * 40)
    
    ambiguous_question = "¿Qué necesito para el colegio?"
    clarification_prompt = SystemPrompts.get_clarification_prompt(ambiguous_question)
    print(f"Pregunta ambigua: {ambiguous_question}")
    print("Prompt de clarificación generado:")
    print(clarification_prompt)
    
    # 5. Prompt de comprobación de coherencia
    print("\n5. PROMPT DE COMPROBACIÓN DE COHERENCIA")
    print("-" * 40)
    
    sample_response = "Las clases empiezan a las 8:00 horas de lunes a viernes según el reglamento escolar."
    coherence_prompt = SystemPrompts.get_coherence_check_prompt(sample_response, sample_docs)
    print(f"Respuesta a validar: {sample_response}")
    print("Prompt de validación generado:")
    print(coherence_prompt[:400] + "...")

def test_prompt_configurations():
    """Prueba las configuraciones de prompts"""
    print("\n" + "=" * 60)
    print("PRUEBA DE CONFIGURACIONES DE PROMPTS")
    print("=" * 60)
    
    # Configuraciones por tipo de usuario
    user_types = ["estudiante", "apoderado", "profesor", "admin"]
    
    for user_type in user_types:
        print(f"\n{user_type.upper()}:")
        print("-" * 20)
        
        config = get_complete_prompt_config(user_type, "rag_synthesis")
        
        print(f"  Temperature: {config['prompt_config'].temperature}")
        print(f"  Max tokens: {config['prompt_config'].max_tokens}")
        print(f"  Tono: {config['user_config']['tone']}")
        print(f"  Complejidad: {config['user_config']['complexity']}")
        print(f"  Longitud máxima: {config['user_config']['max_response_length']}")
        print(f"  Incluye ejemplos: {config['user_config']['include_examples']}")
        print(f"  Evita términos técnicos: {config['user_config']['avoid_technical_terms']}")

def test_example_scenarios():
    """Prueba escenarios de ejemplo"""
    print("\n" + "=" * 60)
    print("PRUEBA DE ESCENARIOS DE EJEMPLO")
    print("=" * 60)
    
    examples = PromptExamples()
    
    # Obtener escenarios de prueba
    test_scenarios = examples.get_test_scenarios()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['scenario']}")
        print(f"   Pregunta: {scenario['question']}")
        print(f"   Usuario: {scenario['user_type']}")
        print(f"   Comportamiento esperado: {scenario['expected_behavior']}")
        
        # Generar prompt completo para este escenario
        if scenario['test_documents']:
            complete_prompt = get_complete_prompt(
                user_type=scenario['user_type'],
                question=scenario['question'],
                retrieved_docs=scenario['test_documents']
            )
            print(f"   Longitud del prompt: {len(complete_prompt)} caracteres")
        else:
            # Para consultas sin documentos, usar prompt básico
            system_prompt = SystemPrompts.get_system_prompt()
            user_prompt = SystemPrompts.get_user_specific_prompt(scenario['user_type'])
            context_prompt = SystemPrompts.get_context_building_prompt(
                scenario['question'], 
                scenario['user_type']
            )
            complete_prompt = f"{system_prompt}\n\n{user_prompt}\n\n{context_prompt}"
            print(f"   Longitud del prompt: {len(complete_prompt)} caracteres")

def test_error_handling():
    """Prueba el manejo de errores"""
    print("\n" + "=" * 60)
    print("PRUEBA DE MANEJO DE ERRORES")
    print("=" * 60)
    
    error_types = ["no_information", "ambiguous_question", "technical_error", "privacy_concern"]
    
    for error_type in error_types:
        print(f"\n{error_type.upper()}:")
        print("-" * 30)
        
        error_prompt = SystemPrompts.get_error_handling_prompt(
            error_type, 
            f"Contexto de prueba para {error_type}"
        )
        print(error_prompt)

def test_learning_agent():
    """Prueba el agente de aprendizaje"""
    print("\n" + "=" * 60)
    print("PRUEBA DE AGENTE DE APRENDIZAJE")
    print("=" * 60)
    
    # Consultas de ejemplo para análisis
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
        },
        {
            "question": "¿Cómo justifico una inasistencia?",
            "answer": "Debe presentar certificado médico o justificativo del apoderado dentro de 48 horas",
            "accuracy": 0.85,
            "sources": ["manual_procedimientos.txt"],
            "timestamp": "2024-03-15 14:20:00"
        }
    ]
    
    learning_prompt = SystemPrompts.get_learning_agent_prompt(sample_queries)
    print("Prompt de análisis de aprendizaje generado:")
    print(learning_prompt[:500] + "...")

def test_quality_assurance():
    """Prueba el aseguramiento de calidad"""
    print("\n" + "=" * 60)
    print("PRUEBA DE ASEGURAMIENTO DE CALIDAD")
    print("=" * 60)
    
    # Respuesta de ejemplo para evaluar
    sample_response = "Las clases empiezan a las 8:00 horas de lunes a viernes según el reglamento escolar del colegio."
    sample_question = "¿A qué hora empiezan las clases?"
    sample_sources = [
        {
            "text": "Las clases se desarrollan de lunes a viernes de 8:00 a 16:00 horas",
            "metadata": {"file_name": "reglamento_escolar.txt"}
        }
    ]
    
    qa_prompt = SystemPrompts.get_quality_assurance_prompt(
        sample_response, 
        sample_question, 
        sample_sources
    )
    
    print(f"Pregunta: {sample_question}")
    print(f"Respuesta: {sample_response}")
    print("\nPrompt de evaluación de calidad:")
    print(qa_prompt)

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("INICIANDO PRUEBAS DE PROMPTS - SCHOOLBOT")
    print("=" * 60)
    
    try:
        # Ejecutar todas las pruebas
        test_system_prompts()
        test_prompt_configurations()
        test_example_scenarios()
        test_error_handling()
        test_learning_agent()
        test_quality_assurance()
        
        print("\n" + "=" * 60)
        print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
        # Mostrar resumen
        print("\nRESUMEN DE PRUEBAS:")
        print("- ✅ Prompts principales del sistema")
        print("- ✅ Configuraciones por tipo de usuario")
        print("- ✅ Escenarios de ejemplo")
        print("- ✅ Manejo de errores")
        print("- ✅ Agente de aprendizaje")
        print("- ✅ Aseguramiento de calidad")
        
        print("\nLos prompts están listos para ser utilizados en el sistema SchoolBot.")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {str(e)}")
        print("Verifica que todos los archivos de prompts estén disponibles.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


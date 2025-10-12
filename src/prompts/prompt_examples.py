"""
SchoolBot - Asistente Inteligente Escolar
Ejemplos de Uso de Prompts

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo contiene ejemplos prácticos de uso de los prompts
del sistema SchoolBot con casos reales del Colegio San Ignacio Digital.
"""

from typing import Dict, List, Any
from system_prompts import SystemPrompts, get_complete_prompt

class PromptExamples:
    """
    Clase con ejemplos prácticos de uso de prompts
    """
    
    @staticmethod
    def get_example_queries() -> List[Dict[str, Any]]:
        """
        Retorna ejemplos de consultas típicas del colegio
        """
        return [
            {
                "question": "¿Cuáles son los horarios de clases?",
                "user_type": "estudiante",
                "expected_response_type": "información_básica",
                "difficulty": "baja"
            },
            {
                "question": "¿Cuándo son las vacaciones de invierno?",
                "user_type": "apoderado",
                "expected_response_type": "fechas_importantes",
                "difficulty": "baja"
            },
            {
                "question": "¿Cómo justifico una inasistencia de mi hijo?",
                "user_type": "apoderado",
                "expected_response_type": "procedimiento_administrativo",
                "difficulty": "media"
            },
            {
                "question": "¿Cuáles son los criterios de evaluación para matemáticas?",
                "user_type": "profesor",
                "expected_response_type": "política_académica",
                "difficulty": "alta"
            },
            {
                "question": "¿Qué documentos necesito para matricular a mi hijo?",
                "user_type": "apoderado",
                "expected_response_type": "procedimiento_administrativo",
                "difficulty": "media"
            },
            {
                "question": "¿Cuál es el menú de almuerzos de esta semana?",
                "user_type": "estudiante",
                "expected_response_type": "información_específica",
                "difficulty": "baja"
            },
            {
                "question": "¿Puedo cambiar el horario de mi hijo?",
                "user_type": "apoderado",
                "expected_response_type": "procedimiento_administrativo",
                "difficulty": "alta"
            },
            {
                "question": "¿Cuáles son las normas de conducta en el colegio?",
                "user_type": "estudiante",
                "expected_response_type": "reglamento",
                "difficulty": "baja"
            }
        ]
    
    @staticmethod
    def get_example_documents() -> List[Dict[str, Any]]:
        """
        Retorna ejemplos de documentos típicos del colegio
        """
        return [
            {
                "file_name": "reglamento_escolar.txt",
                "content": "Las clases se desarrollan de lunes a viernes de 8:00 a 16:00 horas. La asistencia es obligatoria para todos los estudiantes.",
                "document_type": "reglamento_escolar",
                "relevance_score": 0.95
            },
            {
                "file_name": "calendario_academico.txt",
                "content": "Las vacaciones de invierno son del 24 de junio al 7 de julio de 2024.",
                "document_type": "calendario_academico",
                "relevance_score": 0.90
            },
            {
                "file_name": "manual_procedimientos.txt",
                "content": "Para justificar una inasistencia, debe presentar certificado médico o justificativo del apoderado dentro de 48 horas.",
                "document_type": "manual_procedimientos",
                "relevance_score": 0.85
            },
            {
                "file_name": "menu_almuerzos.txt",
                "content": "Lunes: Pollo asado con arroz y ensalada. Martes: Pescado a la plancha con puré de papas.",
                "document_type": "menu_almuerzos",
                "relevance_score": 0.80
            }
        ]
    
    @staticmethod
    def demonstrate_prompt_usage():
        """
        Demuestra el uso de los diferentes prompts
        """
        print("=" * 60)
        print("DEMOSTRACIÓN DE PROMPTS - SCHOOLBOT")
        print("=" * 60)
        
        # Ejemplo 1: Prompt del sistema
        print("\n1. PROMPT DEL SISTEMA (BASE)")
        print("-" * 40)
        system_prompt = SystemPrompts.get_system_prompt()
        print(system_prompt[:200] + "...")
        
        # Ejemplo 2: Prompt específico para estudiante
        print("\n2. PROMPT ESPECÍFICO PARA ESTUDIANTE")
        print("-" * 40)
        student_prompt = SystemPrompts.get_user_specific_prompt("estudiante")
        print(student_prompt[:200] + "...")
        
        # Ejemplo 3: Prompt RAG con documentos
        print("\n3. PROMPT RAG CON DOCUMENTOS")
        print("-" * 40)
        question = "¿Cuáles son los horarios de clases?"
        documents = PromptExamples.get_example_documents()[:2]
        rag_prompt = SystemPrompts.get_rag_synthesis_prompt(documents, question)
        print(rag_prompt[:300] + "...")
        
        # Ejemplo 4: Prompt de clarificación
        print("\n4. PROMPT DE CLARIFICACIÓN")
        print("-" * 40)
        ambiguous_question = "¿Qué necesito para el colegio?"
        clarification_prompt = SystemPrompts.get_clarification_prompt(ambiguous_question)
        print(clarification_prompt)
        
        # Ejemplo 5: Prompt completo
        print("\n5. PROMPT COMPLETO")
        print("-" * 40)
        complete_prompt = get_complete_prompt(
            user_type="estudiante",
            question="¿Cuáles son los horarios de clases?",
            retrieved_docs=documents
        )
        print(complete_prompt[:400] + "...")
    
    @staticmethod
    def get_test_scenarios() -> List[Dict[str, Any]]:
        """
        Retorna escenarios de prueba para los prompts
        """
        return [
            {
                "scenario": "Consulta básica de horarios",
                "question": "¿A qué hora empiezan las clases?",
                "user_type": "estudiante",
                "expected_behavior": "responder con horario específico",
                "test_documents": [
                    {
                        "text": "Las clases empiezan a las 8:00 horas de lunes a viernes",
                        "metadata": {"file_name": "reglamento_escolar.txt"}
                    }
                ]
            },
            {
                "scenario": "Consulta ambigua que requiere clarificación",
                "question": "¿Qué necesito traer?",
                "user_type": "estudiante",
                "expected_behavior": "solicitar clarificación",
                "test_documents": []
            },
            {
                "scenario": "Consulta sin información disponible",
                "question": "¿Cuál es la dirección del colegio?",
                "user_type": "apoderado",
                "expected_behavior": "indicar que no tiene la información",
                "test_documents": []
            },
            {
                "scenario": "Consulta sobre procedimiento administrativo",
                "question": "¿Cómo justifico una inasistencia?",
                "user_type": "apoderado",
                "expected_behavior": "explicar procedimiento paso a paso",
                "test_documents": [
                    {
                        "text": "Para justificar una inasistencia, debe presentar certificado médico o justificativo del apoderado dentro de 48 horas en secretaría",
                        "metadata": {"file_name": "manual_procedimientos.txt"}
                    }
                ]
            },
            {
                "scenario": "Consulta sobre información personal",
                "question": "¿Cuáles son las notas de mi hijo?",
                "user_type": "apoderado",
                "expected_behavior": "dirigir a contacto directo por privacidad",
                "test_documents": []
            }
        ]
    
    @staticmethod
    def get_prompt_optimization_suggestions() -> List[Dict[str, Any]]:
        """
        Retorna sugerencias para optimizar los prompts
        """
        return [
            {
                "prompt_type": "system_prompt",
                "current_issue": "Muy genérico para diferentes tipos de usuario",
                "suggestion": "Crear prompts específicos por tipo de usuario",
                "priority": "alta"
            },
            {
                "prompt_type": "rag_synthesis",
                "current_issue": "No maneja bien múltiples fuentes contradictorias",
                "suggestion": "Agregar lógica para resolver conflictos entre fuentes",
                "priority": "media"
            },
            {
                "prompt_type": "clarification",
                "current_issue": "Preguntas de clarificación muy genéricas",
                "suggestion": "Personalizar preguntas según el contexto educativo",
                "priority": "baja"
            },
            {
                "prompt_type": "coherence_check",
                "current_issue": "No valida coherencia temporal",
                "suggestion": "Agregar validación de fechas y cronología",
                "priority": "media"
            },
            {
                "prompt_type": "learning_agent",
                "current_issue": "No considera feedback de usuarios",
                "suggestion": "Incorporar sistema de calificaciones de respuestas",
                "priority": "baja"
            }
        ]
    
    @staticmethod
    def get_metrics_for_prompts() -> Dict[str, Any]:
        """
        Retorna métricas sugeridas para evaluar los prompts
        """
        return {
            "accuracy_metrics": [
                "Precisión de respuestas (0-100%)",
                "Relevancia de fuentes citadas",
                "Coherencia con documentos fuente",
                "Cumplimiento de límites de palabras"
            ],
            "user_experience_metrics": [
                "Tiempo de respuesta promedio",
                "Número de aclaraciones necesarias",
                "Satisfacción del usuario (1-5)",
                "Tasa de resolución en primera consulta"
            ],
            "system_metrics": [
                "Uso de memoria por prompt",
                "Tiempo de procesamiento",
                "Tasa de errores de formato",
                "Disponibilidad del sistema"
            ],
            "content_metrics": [
                "Cobertura de temas educativos",
                "Actualización de información",
                "Calidad de citas de fuentes",
                "Adaptación al contexto chileno"
            ]
        }

# Función principal para demostrar el uso
def main():
    """
    Función principal para demostrar el uso de los prompts
    """
    examples = PromptExamples()
    
    # Demostrar uso de prompts
    examples.demonstrate_prompt_usage()
    
    # Mostrar escenarios de prueba
    print("\n" + "=" * 60)
    print("ESCENARIOS DE PRUEBA")
    print("=" * 60)
    
    test_scenarios = examples.get_test_scenarios()
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['scenario']}")
        print(f"   Pregunta: {scenario['question']}")
        print(f"   Usuario: {scenario['user_type']}")
        print(f"   Comportamiento esperado: {scenario['expected_behavior']}")
    
    # Mostrar sugerencias de optimización
    print("\n" + "=" * 60)
    print("SUGERENCIAS DE OPTIMIZACIÓN")
    print("=" * 60)
    
    suggestions = examples.get_prompt_optimization_suggestions()
    for suggestion in suggestions:
        print(f"\n- {suggestion['prompt_type']}: {suggestion['suggestion']}")
        print(f"  Prioridad: {suggestion['priority']}")
    
    # Mostrar métricas
    print("\n" + "=" * 60)
    print("MÉTRICAS DE EVALUACIÓN")
    print("=" * 60)
    
    metrics = examples.get_metrics_for_prompts()
    for category, metric_list in metrics.items():
        print(f"\n{category.upper()}:")
        for metric in metric_list:
            print(f"  - {metric}")

if __name__ == "__main__":
    main()


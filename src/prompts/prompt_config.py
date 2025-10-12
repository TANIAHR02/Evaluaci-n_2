"""
SchoolBot - Asistente Inteligente Escolar
Configuración de Prompts

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo contiene la configuración y parámetros para los prompts
del sistema SchoolBot, incluyendo temperaturas, límites de tokens y configuraciones específicas.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    """Tipos de prompts del sistema"""
    SYSTEM_BASE = "system_base"
    RAG_SYNTHESIS = "rag_synthesis"
    CLARIFICATION = "clarification"
    COHERENCE_CHECK = "coherence_check"
    LEARNING_AGENT = "learning_agent"
    USER_SPECIFIC = "user_specific"
    ERROR_HANDLING = "error_handling"
    CONTEXT_BUILDING = "context_building"
    QUALITY_ASSURANCE = "quality_assurance"

class UserType(Enum):
    """Tipos de usuario del sistema"""
    ESTUDIANTE = "estudiante"
    APODERADO = "apoderado"
    PROFESOR = "profesor"
    ADMIN = "admin"

@dataclass
class PromptConfig:
    """Configuración para un prompt específico"""
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop_sequences: List[str]
    timeout: int  # en segundos
    retry_attempts: int

class PromptConfiguration:
    """
    Clase principal para la configuración de prompts
    """
    
    # Configuraciones base para cada tipo de prompt
    PROMPT_CONFIGS = {
        PromptType.SYSTEM_BASE: PromptConfig(
            temperature=0.1,
            max_tokens=400,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Usuario:", "SchoolBot:"],
            timeout=30,
            retry_attempts=3
        ),
        
        PromptType.RAG_SYNTHESIS: PromptConfig(
            temperature=0.3,
            max_tokens=200,
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            stop_sequences=["\n\n", "Fuente:", "Documento:"],
            timeout=45,
            retry_attempts=2
        ),
        
        PromptType.CLARIFICATION: PromptConfig(
            temperature=0.2,
            max_tokens=150,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Pregunta:"],
            timeout=20,
            retry_attempts=2
        ),
        
        PromptType.COHERENCE_CHECK: PromptConfig(
            temperature=0.0,
            max_tokens=300,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Evaluación:"],
            timeout=30,
            retry_attempts=2
        ),
        
        PromptType.LEARNING_AGENT: PromptConfig(
            temperature=0.4,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.1,
            stop_sequences=["\n\n", "Análisis:", "Recomendación:"],
            timeout=60,
            retry_attempts=1
        ),
        
        PromptType.USER_SPECIFIC: PromptConfig(
            temperature=0.2,
            max_tokens=300,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Contexto:", "Instrucciones:"],
            timeout=25,
            retry_attempts=2
        ),
        
        PromptType.ERROR_HANDLING: PromptConfig(
            temperature=0.1,
            max_tokens=200,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Respuesta:"],
            timeout=15,
            retry_attempts=3
        ),
        
        PromptType.CONTEXT_BUILDING: PromptConfig(
            temperature=0.1,
            max_tokens=250,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Contexto:"],
            timeout=20,
            retry_attempts=2
        ),
        
        PromptType.QUALITY_ASSURANCE: PromptConfig(
            temperature=0.0,
            max_tokens=400,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop_sequences=["\n\n", "Evaluación:", "Recomendación:"],
            timeout=30,
            retry_attempts=2
        )
    }
    
    # Configuraciones específicas por tipo de usuario
    USER_SPECIFIC_CONFIGS = {
        UserType.ESTUDIANTE: {
            "tone": "cercano y comprensible",
            "complexity": "baja",
            "max_response_length": 150,
            "preferred_sources": ["reglamento_escolar", "calendario_academico", "menu_almuerzos"],
            "avoid_technical_terms": True,
            "include_examples": True
        },
        
        UserType.APODERADO: {
            "tone": "formal pero accesible",
            "complexity": "media",
            "max_response_length": 200,
            "preferred_sources": ["circular_apoderados", "manual_procedimientos", "reglamento_escolar"],
            "avoid_technical_terms": False,
            "include_examples": True
        },
        
        UserType.PROFESOR: {
            "tone": "técnico y profesional",
            "complexity": "alta",
            "max_response_length": 300,
            "preferred_sources": ["manual_procedimientos", "reglamento_escolar", "calendario_academico"],
            "avoid_technical_terms": False,
            "include_examples": False
        },
        
        UserType.ADMIN: {
            "tone": "técnico y administrativo",
            "complexity": "alta",
            "max_response_length": 400,
            "preferred_sources": ["manual_procedimientos", "reglamento_escolar"],
            "avoid_technical_terms": False,
            "include_examples": False
        }
    }
    
    # Configuraciones de calidad
    QUALITY_THRESHOLDS = {
        "min_confidence": 0.7,
        "min_relevance": 0.6,
        "max_response_time": 30,  # segundos
        "min_sources": 1,
        "max_sources": 5,
        "min_response_length": 20,
        "max_response_length": 500
    }
    
    # Configuraciones de contexto educativo
    EDUCATIONAL_CONTEXT = {
        "school_name": "Colegio San Ignacio Digital",
        "location": "Santiago, Chile",
        "school_type": "Particular subvencionado",
        "student_count": "Más de 600 alumnos",
        "focus": "Integración tecnológica educativa",
        "schedule": "Lunes a Viernes, 8:00-16:00 horas",
        "language": "Español chileno",
        "timezone": "America/Santiago"
    }
    
    # Configuraciones de manejo de errores
    ERROR_HANDLING = {
        "no_information": {
            "response_template": "No tengo esa información en los documentos disponibles del colegio. Te recomiendo contactar directamente con la secretaría del colegio.",
            "contact_info": "Teléfono: +56 2 1234 5678, Email: contacto@sanignacio.edu",
            "escalation": "secretaría"
        },
        "ambiguous_question": {
            "response_template": "Para poder ayudarte mejor, necesito que me proporciones más detalles sobre tu consulta.",
            "clarification_questions": 2,
            "max_clarification_attempts": 3
        },
        "technical_error": {
            "response_template": "Disculpa, estoy experimentando dificultades técnicas para procesar tu consulta.",
            "fallback_action": "suggest_direct_contact",
            "retry_after": 30  # segundos
        },
        "privacy_concern": {
            "response_template": "Por motivos de privacidad y protección de datos, no puedo proporcionar información personal sobre estudiantes.",
            "escalation": "profesor_jefe",
            "contact_info": "Contacta directamente con el profesor jefe correspondiente"
        }
    }
    
    # Configuraciones de fuentes de datos
    DATA_SOURCES = {
        "reglamento_escolar": {
            "priority": 1,
            "reliability": 0.95,
            "update_frequency": "anual",
            "user_access": ["estudiante", "apoderado", "profesor", "admin"]
        },
        "calendario_academico": {
            "priority": 1,
            "reliability": 0.90,
            "update_frequency": "mensual",
            "user_access": ["estudiante", "apoderado", "profesor", "admin"]
        },
        "circular_apoderados": {
            "priority": 2,
            "reliability": 0.85,
            "update_frequency": "semanal",
            "user_access": ["apoderado", "profesor", "admin"]
        },
        "menu_almuerzos": {
            "priority": 3,
            "reliability": 0.80,
            "update_frequency": "semanal",
            "user_access": ["estudiante", "apoderado", "profesor", "admin"]
        },
        "manual_procedimientos": {
            "priority": 2,
            "reliability": 0.90,
            "update_frequency": "trimestral",
            "user_access": ["profesor", "admin"]
        }
    }
    
    @classmethod
    def get_prompt_config(cls, prompt_type: PromptType) -> PromptConfig:
        """
        Obtiene la configuración para un tipo de prompt específico
        """
        return cls.PROMPT_CONFIGS.get(prompt_type, cls.PROMPT_CONFIGS[PromptType.SYSTEM_BASE])
    
    @classmethod
    def get_user_config(cls, user_type: UserType) -> Dict[str, Any]:
        """
        Obtiene la configuración específica para un tipo de usuario
        """
        return cls.USER_SPECIFIC_CONFIGS.get(user_type, cls.USER_SPECIFIC_CONFIGS[UserType.ESTUDIANTE])
    
    @classmethod
    def get_quality_thresholds(cls) -> Dict[str, Any]:
        """
        Obtiene los umbrales de calidad configurados
        """
        return cls.QUALITY_THRESHOLDS
    
    @classmethod
    def get_educational_context(cls) -> Dict[str, Any]:
        """
        Obtiene el contexto educativo del colegio
        """
        return cls.EDUCATIONAL_CONTEXT
    
    @classmethod
    def get_error_handling_config(cls, error_type: str) -> Dict[str, Any]:
        """
        Obtiene la configuración de manejo de errores para un tipo específico
        """
        return cls.ERROR_HANDLING.get(error_type, cls.ERROR_HANDLING["no_information"])
    
    @classmethod
    def get_data_source_config(cls, source_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración de una fuente de datos específica
        """
        return cls.DATA_SOURCES.get(source_name, {})
    
    @classmethod
    def validate_prompt_config(cls, config: PromptConfig) -> List[str]:
        """
        Valida una configuración de prompt y retorna errores encontrados
        """
        errors = []
        
        if config.temperature < 0.0 or config.temperature > 2.0:
            errors.append("Temperature debe estar entre 0.0 y 2.0")
        
        if config.max_tokens < 1 or config.max_tokens > 4000:
            errors.append("max_tokens debe estar entre 1 y 4000")
        
        if config.top_p < 0.0 or config.top_p > 1.0:
            errors.append("top_p debe estar entre 0.0 y 1.0")
        
        if config.frequency_penalty < -2.0 or config.frequency_penalty > 2.0:
            errors.append("frequency_penalty debe estar entre -2.0 y 2.0")
        
        if config.presence_penalty < -2.0 or config.presence_penalty > 2.0:
            errors.append("presence_penalty debe estar entre -2.0 y 2.0")
        
        if config.timeout < 5 or config.timeout > 300:
            errors.append("timeout debe estar entre 5 y 300 segundos")
        
        if config.retry_attempts < 0 or config.retry_attempts > 5:
            errors.append("retry_attempts debe estar entre 0 y 5")
        
        return errors
    
    @classmethod
    def get_optimized_config(cls, prompt_type: PromptType, user_type: UserType, 
                           context: Dict[str, Any] = None) -> PromptConfig:
        """
        Obtiene una configuración optimizada basada en el tipo de prompt, usuario y contexto
        """
        base_config = cls.get_prompt_config(prompt_type)
        user_config = cls.get_user_config(user_type)
        
        # Crear configuración optimizada
        optimized_config = PromptConfig(
            temperature=base_config.temperature,
            max_tokens=min(base_config.max_tokens, user_config.get("max_response_length", 300)),
            top_p=base_config.top_p,
            frequency_penalty=base_config.frequency_penalty,
            presence_penalty=base_config.presence_penalty,
            stop_sequences=base_config.stop_sequences,
            timeout=base_config.timeout,
            retry_attempts=base_config.retry_attempts
        )
        
        # Ajustar según contexto si se proporciona
        if context:
            if context.get("urgency") == "high":
                optimized_config.timeout = min(optimized_config.timeout, 15)
            if context.get("complexity") == "high":
                optimized_config.max_tokens = max(optimized_config.max_tokens, 400)
            if context.get("creativity_needed"):
                optimized_config.temperature = min(optimized_config.temperature + 0.2, 1.0)
        
        return optimized_config

# Función de utilidad para obtener configuración completa
def get_complete_prompt_config(user_type: str = "estudiante", 
                              prompt_type: str = "system_base",
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Obtiene la configuración completa para un prompt específico
    """
    try:
        user_enum = UserType(user_type)
        prompt_enum = PromptType(prompt_type)
        
        config = PromptConfiguration.get_optimized_config(prompt_enum, user_enum, context)
        user_config = PromptConfiguration.get_user_config(user_enum)
        quality_thresholds = PromptConfiguration.get_quality_thresholds()
        
        return {
            "prompt_config": config,
            "user_config": user_config,
            "quality_thresholds": quality_thresholds,
            "educational_context": PromptConfiguration.get_educational_context()
        }
    except ValueError as e:
        # Configuración por defecto si hay error
        return {
            "prompt_config": PromptConfiguration.get_prompt_config(PromptType.SYSTEM_BASE),
            "user_config": PromptConfiguration.get_user_config(UserType.ESTUDIANTE),
            "quality_thresholds": PromptConfiguration.get_quality_thresholds(),
            "educational_context": PromptConfiguration.get_educational_context()
        }

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de configuración para estudiante
    config = get_complete_prompt_config("estudiante", "rag_synthesis")
    print("Configuración para estudiante:")
    print(f"Temperature: {config['prompt_config'].temperature}")
    print(f"Max tokens: {config['prompt_config'].max_tokens}")
    print(f"Tono: {config['user_config']['tone']}")
    print(f"Complejidad: {config['user_config']['complexity']}")
    
    # Ejemplo de configuración para profesor
    config = get_complete_prompt_config("profesor", "rag_synthesis")
    print("\nConfiguración para profesor:")
    print(f"Temperature: {config['prompt_config'].temperature}")
    print(f"Max tokens: {config['prompt_config'].max_tokens}")
    print(f"Tono: {config['user_config']['tone']}")
    print(f"Complejidad: {config['user_config']['complexity']}")


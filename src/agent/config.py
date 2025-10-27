"""
SchoolBot Agent - Main Configuration
Configuración Principal del Agente Inteligente

Autor: Tania Herrera
Fecha: Diciembre 2024
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import json
from typing import Dict, Any

# Configuración principal del agente SchoolBot
AGENT_CONFIG = {
    # Configuración de memoria
    "memory": {
        "memory_path": "data/memory",
        "max_short_term": 100,
        "max_long_term": 1000,
        "vector_store_path": "data/memory/semantic_vectors",
        "embeddings_model": "text-embedding-ada-002"
    },
    
    # Configuración de planificación
    "planning": {
        "max_plan_steps": 10,
        "default_timeout": 300,
        "strategy_learning": True,
        "adaptive_planning": True
    },
    
    # Configuración del retriever
    "retriever": {
        "vector_db_path": "data/vector_db",
        "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "chunk_size": 600,
        "chunk_overlap": 80,
        "top_k": 5,
        "similarity_threshold": 0.7
    },
    
    # Configuración de plantillas
    "templates": {
        "templates_path": "data/templates",
        "supported_formats": ["pdf", "docx", "txt"],
        "auto_formatting": True
    },
    
    # Configuración del LLM
    "llm": {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 1000,
        "timeout": 30
    },
    
    # Configuración de herramientas
    "tools": {
        "query": {
            "enabled": True,
            "max_results": 10,
            "reranking": True
        },
        "writing": {
            "enabled": True,
            "templates_enabled": True,
            "auto_formatting": True
        },
        "reasoning": {
            "enabled": True,
            "analysis_depth": "detailed",
            "decision_logging": True
        }
    },
    
    # Configuración de sesiones
    "sessions": {
        "max_sessions": 100,
        "session_timeout": 3600,  # 1 hora
        "cleanup_interval": 300,   # 5 minutos
        "max_conversation_history": 50
    },
    
    # Configuración de monitoreo
    "monitoring": {
        "metrics_enabled": True,
        "logging_level": "INFO",
        "performance_tracking": True,
        "error_reporting": True
    },
    
    # Configuración de seguridad
    "security": {
        "rate_limiting": True,
        "max_requests_per_minute": 60,
        "input_validation": True,
        "output_filtering": True
    }
}

def get_config() -> Dict[str, Any]:
    """Obtiene la configuración del agente"""
    return AGENT_CONFIG.copy()

def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza la configuración con nuevos valores
    
    Args:
        updates: Diccionario con actualizaciones
        
    Returns:
        Configuración actualizada
    """
    config = AGENT_CONFIG.copy()
    
    def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    return deep_update(config, updates)

def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """
    Carga configuración desde archivo JSON
    
    Args:
        file_path: Ruta al archivo de configuración
        
    Returns:
        Configuración cargada
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
        
        return update_config(file_config)
        
    except Exception as e:
        print(f"Error cargando configuración desde {file_path}: {e}")
        return get_config()

def save_config_to_file(config: Dict[str, Any], file_path: str):
    """
    Guarda configuración en archivo JSON
    
    Args:
        config: Configuración a guardar
        file_path: Ruta del archivo
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuración guardada en {file_path}")
        
    except Exception as e:
        print(f"Error guardando configuración en {file_path}: {e}")

# Configuraciones específicas por tipo de usuario
USER_TYPE_CONFIGS = {
    "estudiante": {
        "tools": {
            "query": {"max_results": 5},
            "writing": {"templates_enabled": False},
            "reasoning": {"analysis_depth": "basic"}
        },
        "memory": {
            "max_short_term": 50
        }
    },
    "apoderado": {
        "tools": {
            "query": {"max_results": 8},
            "writing": {"templates_enabled": True},
            "reasoning": {"analysis_depth": "detailed"}
        },
        "memory": {
            "max_short_term": 75
        }
    },
    "profesor": {
        "tools": {
            "query": {"max_results": 10},
            "writing": {"templates_enabled": True},
            "reasoning": {"analysis_depth": "detailed"}
        },
        "memory": {
            "max_short_term": 100
        }
    },
    "admin": {
        "tools": {
            "query": {"max_results": 15},
            "writing": {"templates_enabled": True},
            "reasoning": {"analysis_depth": "comprehensive"}
        },
        "memory": {
            "max_short_term": 150
        }
    }
}

def get_user_config(user_type: str) -> Dict[str, Any]:
    """
    Obtiene configuración específica para tipo de usuario
    
    Args:
        user_type: Tipo de usuario
        
    Returns:
        Configuración específica del usuario
    """
    base_config = get_config()
    user_config = USER_TYPE_CONFIGS.get(user_type, {})
    
    return update_config(user_config)

# Configuraciones de entorno
ENVIRONMENT_CONFIGS = {
    "development": {
        "monitoring": {
            "logging_level": "DEBUG"
        },
        "security": {
            "rate_limiting": False
        }
    },
    "testing": {
        "memory": {
            "max_short_term": 10,
            "max_long_term": 50
        },
        "sessions": {
            "max_sessions": 10
        }
    },
    "production": {
        "monitoring": {
            "logging_level": "WARNING"
        },
        "security": {
            "rate_limiting": True,
            "max_requests_per_minute": 30
        }
    }
}

def get_environment_config(environment: str) -> Dict[str, Any]:
    """
    Obtiene configuración específica para entorno
    
    Args:
        environment: Entorno (development, testing, production)
        
    Returns:
        Configuración específica del entorno
    """
    base_config = get_config()
    env_config = ENVIRONMENT_CONFIGS.get(environment, {})
    
    return update_config(env_config)

# Función principal para obtener configuración completa
def get_complete_config(user_type: str = "estudiante", environment: str = "development") -> Dict[str, Any]:
    """
    Obtiene configuración completa combinando todas las fuentes
    
    Args:
        user_type: Tipo de usuario
        environment: Entorno
        
    Returns:
        Configuración completa
    """
    # Configuración base
    config = get_config()
    
    # Aplicar configuración de entorno
    env_config = ENVIRONMENT_CONFIGS.get(environment, {})
    config = update_config(env_config)
    
    # Aplicar configuración de usuario
    user_config = USER_TYPE_CONFIGS.get(user_type, {})
    config = update_config(user_config)
    
    return config

if __name__ == "__main__":
    # Ejemplo de uso
    print("=== CONFIGURACIÓN DEL AGENTE SCHOOLBOT ===")
    
    # Configuración base
    base_config = get_config()
    print(f"Configuración base cargada: {len(base_config)} secciones")
    
    # Configuración para estudiante
    student_config = get_user_config("estudiante")
    print(f"Configuración para estudiante: {student_config['tools']['query']['max_results']} resultados máximos")
    
    # Configuración completa
    complete_config = get_complete_config("profesor", "production")
    print(f"Configuración completa: {complete_config['security']['rate_limiting']} rate limiting")
    
    print("\n✅ Configuración del agente lista para usar")

"""
SchoolBot Agent - Agente Inteligente Escolar
EP2 - Ingeniería de Soluciones con IA

Autor: Tania Herrera
Fecha: Diciembre 2024
Institución: Duoc UC

Descripción:
Módulo principal del agente inteligente escolar con capacidades de:
- Memoria de corto y largo plazo
- Planificación y toma de decisiones
- Herramientas de consulta, escritura y razonamiento
- Autonomía funcional
"""

from .core_agent import SchoolBotAgent
from .memory_manager import MemoryManager
from .planning_engine import PlanningEngine
from .tools import QueryTool, WritingTool, ReasoningTool
from .orchestrator import AgentOrchestrator

__all__ = [
    'SchoolBotAgent',
    'MemoryManager', 
    'PlanningEngine',
    'QueryTool',
    'WritingTool',
    'ReasoningTool',
    'AgentOrchestrator'
]

__version__ = "2.0.0"

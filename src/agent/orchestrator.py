import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# Local imports
from .core_agent import SchoolBotAgent, AgentState, AgentContext
from .memory_manager import MemoryManager
from .planning_engine import PlanningEngine, PlanStatus
from .tools import QueryTool, WritingTool, ReasoningTool

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestrationMode(Enum):
    """Modos de orquestación"""
    AUTOMATIC = "automatic"
    SUPERVISED = "supervised"
    MANUAL = "manual"

@dataclass
class AgentSession:
    """Sesión del agente"""
    session_id: str
    user_id: str
    user_type: str
    created_at: datetime
    last_activity: datetime
    context: Dict[str, Any]
    active_tasks: List[str]
    conversation_history: List[Dict[str, Any]]

class AgentOrchestrator:
    """
    Orquestador principal del agente SchoolBot
    
    Responsabilidades:
    - Coordinar todos los componentes del agente
    - Gestionar sesiones de usuario
    - Ejecutar planes complejos
    - Monitorear rendimiento
    - Manejar errores y recuperación
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el orquestador
        
        Args:
            config: Configuración completa del sistema
        """
        self.config = config
        self.agent = None
        self.sessions = {}
        self.active_tasks = {}
        self.orchestration_mode = OrchestrationMode.AUTOMATIC
        
        # Métricas del sistema
        self.system_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "system_uptime": 0.0
        }
        
        self.start_time = datetime.now()
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Inicializa el agente principal"""
        try:
            # Configuración del agente
            agent_config = {
                "memory": self.config.get("memory", {}),
                "planning": self.config.get("planning", {}),
                "retriever": self.config.get("retriever", {}),
                "templates": self.config.get("templates", {}),
                "llm": self.config.get("llm", {})
            }
            
            # Crear agente
            self.agent = SchoolBotAgent(agent_config)
            
            logger.info("Orquestador: Agente inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando agente: {str(e)}")
            raise
    
    def create_session(self, user_id: str, user_type: str, context: Dict[str, Any] = None) -> str:
        """
        Crea una nueva sesión de usuario
        
        Args:
            user_id: ID del usuario
            user_type: Tipo de usuario
            context: Contexto inicial
            
        Returns:
            ID de la sesión creada
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            
            session = AgentSession(
                session_id=session_id,
                user_id=user_id,
                user_type=user_type,
                created_at=now,
                last_activity=now,
                context=context or {},
                active_tasks=[],
                conversation_history=[]
            )
            
            self.sessions[session_id] = session
            self.system_metrics["total_sessions"] += 1
            self.system_metrics["active_sessions"] += 1
            
            logger.info(f"Sesión creada: {session_id} para usuario {user_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creando sesión: {str(e)}")
            raise
    
    def process_request(self, session_id: str, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa una solicitud del usuario
        
        Args:
            session_id: ID de la sesión
            request: Solicitud del usuario
            context: Contexto adicional
            
        Returns:
            Respuesta del agente
        """
        start_time = datetime.now()
        
        try:
            # Verificar sesión
            if session_id not in self.sessions:
                raise ValueError(f"Sesión {session_id} no encontrada")
            
            session = self.sessions[session_id]
            session.last_activity = datetime.now()
            
            # Actualizar métricas
            self.system_metrics["total_requests"] += 1
            
            # Preparar contexto del usuario
            user_context = {
                "username": session.user_id,
                "user_type": session.user_type,
                "session_id": session_id,
                "conversation_history": session.conversation_history,
                "active_tasks": session.active_tasks,
                **(context or {})
            }
            
            # Procesar solicitud con el agente
            response = self.agent.process_request(request, user_context)
            
            # Actualizar sesión
            self._update_session(session, request, response)
            
            # Actualizar métricas
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(processing_time, response.get("error") is None)
            
            logger.info(f"Solicitud procesada en {processing_time:.2f}s para sesión {session_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando solicitud: {str(e)}")
            self.system_metrics["failed_requests"] += 1
            
            return {
                "error": str(e),
                "response": "Lo siento, ocurrió un error procesando tu solicitud.",
                "session_id": session_id
            }
    
    def _update_session(self, session: AgentSession, request: str, response: Dict[str, Any]):
        """Actualiza la sesión con nueva información"""
        try:
            # Agregar a historial de conversación
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "request": request,
                "response": response.get("response", ""),
                "analysis": response.get("analysis", {}),
                "plan": response.get("plan")
            }
            
            session.conversation_history.append(conversation_entry)
            
            # Mantener solo los últimos 50 mensajes
            if len(session.conversation_history) > 50:
                session.conversation_history = session.conversation_history[-50:]
            
            # Actualizar tareas activas si hay un plan
            plan = response.get("plan")
            if plan and plan.get("steps"):
                task_id = plan.get("id", "unknown")
                if task_id not in session.active_tasks:
                    session.active_tasks.append(task_id)
            
        except Exception as e:
            logger.error(f"Error actualizando sesión: {str(e)}")
    
    def execute_plan(self, session_id: str, plan_id: str) -> Dict[str, Any]:
        """
        Ejecuta un plan específico
        
        Args:
            session_id: ID de la sesión
            plan_id: ID del plan
            
        Returns:
            Resultado de la ejecución
        """
        try:
            # Verificar sesión
            if session_id not in self.sessions:
                raise ValueError(f"Sesión {session_id} no encontrada")
            
            session = self.sessions[session_id]
            
            # Ejecutar plan usando el motor de planificación
            if self.agent.planning_engine:
                result = self.agent.planning_engine.execute_plan(plan_id)
                
                # Actualizar sesión
                if plan_id in session.active_tasks:
                    session.active_tasks.remove(plan_id)
                
                logger.info(f"Plan {plan_id} ejecutado para sesión {session_id}")
                
                return result
            else:
                raise ValueError("Motor de planificación no disponible")
                
        except Exception as e:
            logger.error(f"Error ejecutando plan: {str(e)}")
            raise
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Obtiene estado de una sesión"""
        try:
            if session_id not in self.sessions:
                return {"error": "Sesión no encontrada"}
            
            session = self.sessions[session_id]
            
            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "user_type": session.user_type,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "active_tasks": session.active_tasks,
                "conversation_count": len(session.conversation_history),
                "context": session.context
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de sesión: {str(e)}")
            return {"error": str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Obtiene estado del agente"""
        try:
            agent_status = self.agent.get_status() if self.agent else {}
            
            return {
                "agent_status": agent_status,
                "system_metrics": self.system_metrics,
                "active_sessions": len(self.sessions),
                "orchestration_mode": self.orchestration_mode.value,
                "uptime": (datetime.now() - self.start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del agente: {str(e)}")
            return {"error": str(e)}
    
    def learn_from_feedback(self, session_id: str, feedback: Dict[str, Any]):
        """
        Aprende del feedback del usuario
        
        Args:
            session_id: ID de la sesión
            feedback: Feedback del usuario
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Sesión {session_id} no encontrada")
            
            # Agregar contexto de sesión al feedback
            session = self.sessions[session_id]
            feedback["session_context"] = {
                "user_type": session.user_type,
                "session_duration": (datetime.now() - session.created_at).total_seconds(),
                "conversation_count": len(session.conversation_history)
            }
            
            # Enviar feedback al agente
            if self.agent:
                self.agent.learn_from_feedback(feedback)
            
            logger.info(f"Feedback procesado para sesión {session_id}")
            
        except Exception as e:
            logger.error(f"Error procesando feedback: {str(e)}")
    
    def cleanup_sessions(self, max_age_hours: int = 24):
        """
        Limpia sesiones inactivas
        
        Args:
            max_age_hours: Edad máxima en horas
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            sessions_to_remove = []
            
            for session_id, session in self.sessions.items():
                if session.last_activity < cutoff_time:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.sessions[session_id]
                self.system_metrics["active_sessions"] -= 1
            
            logger.info(f"Sesiones limpiadas: {len(sessions_to_remove)}")
            
        except Exception as e:
            logger.error(f"Error limpiando sesiones: {str(e)}")
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Actualiza métricas del sistema"""
        try:
            if success:
                self.system_metrics["successful_requests"] += 1
            else:
                self.system_metrics["failed_requests"] += 1
            
            # Actualizar tiempo promedio de respuesta
            total_requests = self.system_metrics["total_requests"]
            current_avg = self.system_metrics["average_response_time"]
            self.system_metrics["average_response_time"] = (
                (current_avg * (total_requests - 1) + processing_time) / total_requests
            )
            
            # Actualizar tiempo de funcionamiento
            self.system_metrics["system_uptime"] = (
                datetime.now() - self.start_time
            ).total_seconds()
            
        except Exception as e:
            logger.error(f"Error actualizando métricas: {str(e)}")
    
    def set_orchestration_mode(self, mode: OrchestrationMode):
        """Establece el modo de orquestación"""
        self.orchestration_mode = mode
        logger.info(f"Modo de orquestación cambiado a: {mode.value}")
    
    def shutdown(self):
        """Cierra el orquestador de forma segura"""
        try:
            logger.info("Cerrando orquestador...")
            
            # Cerrar agente
            if self.agent:
                self.agent.shutdown()
            
            # Guardar métricas finales
            self.system_metrics["system_uptime"] = (
                datetime.now() - self.start_time
            ).total_seconds()
            
            logger.info("Orquestador cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando orquestador: {str(e)}")

# Función de utilidad para crear instancia del orquestador
def create_agent_orchestrator(config_path: str = None) -> AgentOrchestrator:
    """
    Crea una instancia del orquestador con configuración
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Instancia del orquestador
    """
    try:
        # Configuración por defecto
        default_config = {
            "memory": {
                "memory_path": "data/memory",
                "max_short_term": 100,
                "max_long_term": 1000
            },
            "planning": {
                "max_plan_steps": 10,
                "default_timeout": 300
            },
            "retriever": {
                "vector_db_path": "data/vector_db",
                "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            },
            "templates": {
                "templates_path": "data/templates"
            },
            "llm": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.3
            }
        }
        
        # Cargar configuración personalizada si existe
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                default_config.update(custom_config)
        
        # Crear orquestador
        orchestrator = AgentOrchestrator(default_config)
        
        logger.info("Orquestador creado correctamente")
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"Error creando orquestador: {str(e)}")
        raise

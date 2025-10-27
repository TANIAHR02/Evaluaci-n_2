"""
SchoolBot Agent - Core Agent Module
Agente Principal con Capacidades de Memoria y Planificación

Autor: Tania Herrera
Fecha: Octubre 2025
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# Local imports
from .memory_manager import MemoryManager
from .planning_engine import PlanningEngine
from .tools import QueryTool, WritingTool, ReasoningTool

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Estados del agente"""
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    ERROR = "error"

class TaskPriority(Enum):
    """Prioridades de tareas"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Estructura de una tarea"""
    id: str
    description: str
    priority: TaskPriority
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None
    context: Dict[str, Any] = None
    subtasks: List[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.subtasks is None:
            self.subtasks = []

@dataclass
class AgentContext:
    """Contexto del agente"""
    current_user: str
    user_type: str
    session_id: str
    conversation_history: List[Dict[str, Any]]
    active_tasks: List[Task]
    memory_summary: str
    last_interaction: datetime

class SchoolBotAgent:
    """
    Agente Inteligente Escolar con capacidades avanzadas de:
    - Memoria de corto y largo plazo
    - Planificación y toma de decisiones
    - Herramientas especializadas
    - Autonomía funcional
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el agente inteligente
        
        Args:
            config: Configuración del agente
        """
        self.config = config
        self.state = AgentState.IDLE
        self.context = None
        self.memory_manager = None
        self.planning_engine = None
        self.tools = {}
        self.agent_executor = None
        
        # Métricas del agente
        self.metrics = {
            "total_interactions": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_response_time": 0.0,
            "memory_hit_rate": 0.0
        }
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa todos los componentes del agente"""
        try:
            # Inicializar gestor de memoria
            self.memory_manager = MemoryManager(self.config.get("memory", {}))
            
            # Inicializar motor de planificación
            self.planning_engine = PlanningEngine(self.config.get("planning", {}))
            
            # Inicializar herramientas
            self._initialize_tools()
            
            # Inicializar ejecutor del agente
            self._initialize_agent_executor()
            
            logger.info("Agente SchoolBot inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando agente: {str(e)}")
            raise
    
    def _initialize_tools(self):
        """Inicializa las herramientas del agente"""
        try:
            # Herramienta de consulta
            self.tools["query"] = QueryTool(
                retriever_config=self.config.get("retriever", {}),
                memory_manager=self.memory_manager
            )
            
            # Herramienta de escritura
            self.tools["writing"] = WritingTool(
                templates_config=self.config.get("templates", {}),
                memory_manager=self.memory_manager
            )
            
            # Herramienta de razonamiento
            self.tools["reasoning"] = ReasoningTool(
                llm_config=self.config.get("llm", {}),
                memory_manager=self.memory_manager
            )
            
            logger.info("Herramientas del agente inicializadas")
            
        except Exception as e:
            logger.error(f"Error inicializando herramientas: {str(e)}")
            raise
    
    def _initialize_agent_executor(self):
        """Inicializa el ejecutor del agente con LangChain"""
        try:
            # Crear herramientas LangChain
            langchain_tools = []
            
            for name, tool in self.tools.items():
                langchain_tool = Tool(
                    name=tool.name,
                    description=tool.description,
                    func=tool.execute
                )
                langchain_tools.append(langchain_tool)
            
            # Crear memoria del agente
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Crear prompt del agente
            agent_prompt = self._create_agent_prompt()
            
            # Crear LLM
            llm = ChatOpenAI(
                temperature=0.1,
                model_name="gpt-3.5-turbo",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Crear agente ReAct
            agent = create_react_agent(
                llm=llm,
                tools=langchain_tools,
                prompt=agent_prompt
            )
            
            # Crear ejecutor del agente
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=langchain_tools,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            logger.info("Ejecutor del agente inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando ejecutor del agente: {str(e)}")
            raise
    
    def _create_agent_prompt(self) -> PromptTemplate:
        """Crea el prompt del agente"""
        template = """
Eres SchoolBot, un agente inteligente especializado en asistencia escolar del Colegio San Ignacio Digital.

INFORMACIÓN INSTITUCIONAL:
- Institución: Colegio San Ignacio Digital
- Ubicación: Santiago, Chile
- Tipo: Particular subvencionado
- Estudiantes: Más de 600 alumnos
- Enfoque: Integración tecnológica educativa

CAPACIDADES DEL AGENTE:
1. CONSULTA: Buscar información en documentos escolares
2. ESCRITURA: Generar reportes, comunicados y documentos
3. RAZONAMIENTO: Analizar situaciones y tomar decisiones

INSTRUCCIONES:
- Usa las herramientas disponibles para resolver tareas
- Mantén contexto de conversaciones anteriores
- Planifica tareas complejas en pasos más pequeños
- Aprende de interacciones previas
- Mantén un tono profesional pero cercano

HISTORIAL DE CONVERSACIÓN:
{chat_history}

HERRAMIENTAS DISPONIBLES:
{tools}

FORMATO DE RESPUESTA:
- Usa el formato: Thought -> Action -> Action Input -> Observation -> Thought -> Final Answer
- Sé específico en tus acciones
- Explica tu razonamiento

TAREA ACTUAL: {input}

RESPUESTA:
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["chat_history", "tools", "input"]
        )
    
    def process_request(self, request: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una solicitud del usuario
        
        Args:
            request: Solicitud del usuario
            user_context: Contexto del usuario
            
        Returns:
            Respuesta del agente
        """
        start_time = datetime.now()
        self.state = AgentState.THINKING
        
        try:
            # Actualizar contexto del agente
            self._update_context(user_context)
            
            # Analizar la solicitud
            analysis = self._analyze_request(request)
            
            # Planificar respuesta si es necesario
            if analysis["requires_planning"]:
                self.state = AgentState.PLANNING
                plan = self.planning_engine.create_plan(request, analysis, self.context)
            else:
                plan = None
            
            # Ejecutar respuesta
            self.state = AgentState.EXECUTING
            response = self._execute_response(request, plan)
            
            # Actualizar memoria
            self._update_memory(request, response, analysis)
            
            # Actualizar métricas
            self._update_metrics(start_time, True)
            
            self.state = AgentState.IDLE
            
            return {
                "response": response,
                "plan": plan,
                "analysis": analysis,
                "context": self.context,
                "metrics": self.metrics
            }
            
        except Exception as e:
            logger.error(f"Error procesando solicitud: {str(e)}")
            self.state = AgentState.ERROR
            self._update_metrics(start_time, False)
            
            return {
                "error": str(e),
                "response": "Lo siento, ocurrió un error procesando tu solicitud.",
                "state": self.state.value
            }
    
    def _update_context(self, user_context: Dict[str, Any]):
        """Actualiza el contexto del agente"""
        self.context = AgentContext(
            current_user=user_context.get("username", "unknown"),
            user_type=user_context.get("user_type", "estudiante"),
            session_id=user_context.get("session_id", "default"),
            conversation_history=user_context.get("conversation_history", []),
            active_tasks=user_context.get("active_tasks", []),
            memory_summary=self.memory_manager.get_summary() if self.memory_manager else "",
            last_interaction=datetime.now()
        )
    
    def _analyze_request(self, request: str) -> Dict[str, Any]:
        """Analiza la solicitud del usuario"""
        analysis = {
            "intent": "unknown",
            "complexity": "simple",
            "requires_planning": False,
            "tools_needed": [],
            "context_required": False
        }
        
        # Análisis de intención usando herramienta de razonamiento
        if self.tools["reasoning"]:
            intent_analysis = self.tools["reasoning"].analyze_intent(request)
            analysis.update(intent_analysis)
        
        # Determinar herramientas necesarias
        if any(keyword in request.lower() for keyword in ["buscar", "encontrar", "información"]):
            analysis["tools_needed"].append("query")
        
        if any(keyword in request.lower() for keyword in ["escribir", "crear", "generar", "reporte"]):
            analysis["tools_needed"].append("writing")
        
        if any(keyword in request.lower() for keyword in ["analizar", "decidir", "evaluar", "comparar"]):
            analysis["tools_needed"].append("reasoning")
        
        # Determinar complejidad
        if len(analysis["tools_needed"]) > 1 or analysis["intent"] == "complex_task":
            analysis["complexity"] = "complex"
            analysis["requires_planning"] = True
        
        return analysis
    
    def _execute_response(self, request: str, plan: Optional[Dict[str, Any]]) -> str:
        """Ejecuta la respuesta del agente"""
        try:
            if plan:
                # Ejecutar plan complejo
                return self._execute_plan(request, plan)
            else:
                # Ejecutar respuesta directa
                return self.agent_executor.run(input=request)
                
        except Exception as e:
            logger.error(f"Error ejecutando respuesta: {str(e)}")
            return f"Error ejecutando respuesta: {str(e)}"
    
    def _execute_plan(self, request: str, plan: Dict[str, Any]) -> str:
        """Ejecuta un plan complejo"""
        results = []
        
        for step in plan.get("steps", []):
            try:
                step_result = self._execute_step(step)
                results.append(step_result)
            except Exception as e:
                logger.error(f"Error ejecutando paso: {str(e)}")
                results.append(f"Error en paso: {str(e)}")
        
        # Sintetizar resultados
        if self.tools["reasoning"]:
            synthesis = self.tools["reasoning"].synthesize_results(results, request)
            return synthesis
        else:
            return "\n".join(results)
    
    def _execute_step(self, step: Dict[str, Any]) -> str:
        """Ejecuta un paso del plan"""
        tool_name = step.get("tool")
        action = step.get("action")
        parameters = step.get("parameters", {})
        
        if tool_name in self.tools:
            return self.tools[tool_name].execute(action, parameters)
        else:
            return f"Herramienta {tool_name} no disponible"
    
    def _update_memory(self, request: str, response: str, analysis: Dict[str, Any]):
        """Actualiza la memoria del agente"""
        if self.memory_manager:
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "request": request,
                "response": response,
                "analysis": analysis,
                "context": asdict(self.context) if self.context else {}
            }
            
            self.memory_manager.store_interaction(memory_entry)
    
    def _update_metrics(self, start_time: datetime, success: bool):
        """Actualiza las métricas del agente"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.metrics["total_interactions"] += 1
        
        if success:
            self.metrics["successful_tasks"] += 1
        else:
            self.metrics["failed_tasks"] += 1
        
        # Actualizar tiempo promedio de respuesta
        total_interactions = self.metrics["total_interactions"]
        current_avg = self.metrics["average_response_time"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_interactions - 1) + processing_time) / total_interactions
        )
        
        # Actualizar tasa de aciertos de memoria
        if self.memory_manager:
            self.metrics["memory_hit_rate"] = self.memory_manager.get_hit_rate()
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del agente"""
        return {
            "state": self.state.value,
            "context": asdict(self.context) if self.context else None,
            "metrics": self.metrics,
            "tools_available": list(self.tools.keys()),
            "memory_status": self.memory_manager.get_status() if self.memory_manager else None,
            "planning_status": self.planning_engine.get_status() if self.planning_engine else None
        }
    
    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """Aprende del feedback del usuario"""
        if self.memory_manager:
            self.memory_manager.store_feedback(feedback)
        
        # Actualizar estrategias basadas en feedback
        if self.planning_engine:
            self.planning_engine.update_strategies(feedback)
    
    def shutdown(self):
        """Cierra el agente de forma segura"""
        logger.info("Cerrando agente SchoolBot...")
        
        if self.memory_manager:
            self.memory_manager.save_memory()
        
        logger.info("Agente SchoolBot cerrado correctamente")

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
from collections import defaultdict

# LangChain imports
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlanStatus(Enum):
    """Estados de un plan"""
    CREATED = "created"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DecisionType(Enum):
    """Tipos de decisiones"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ITERATIVE = "iterative"

@dataclass
class PlanStep:
    """Paso de un plan"""
    id: str
    description: str
    tool: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_duration: int  # segundos
    priority: int  # 1-5
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class Plan:
    """Plan de ejecución"""
    id: str
    name: str
    description: str
    steps: List[PlanStep]
    status: PlanStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_estimated_duration: int = 0
    actual_duration: int = 0
    success_rate: float = 0.0

@dataclass
class DecisionContext:
    """Contexto para toma de decisiones"""
    user_type: str
    task_complexity: str
    available_tools: List[str]
    memory_context: Dict[str, Any]
    constraints: Dict[str, Any]
    preferences: Dict[str, Any]

class PlanningEngine:
    """
    Motor de planificación y toma de decisiones adaptativas
    
    Características:
    - Planificación jerárquica de tareas
    - Toma de decisiones basada en contexto
    - Adaptación dinámica de estrategias
    - Optimización de recursos
    - Aprendizaje de patrones de éxito
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el motor de planificación
        
        Args:
            config: Configuración del motor
        """
        self.config = config
        self.llm = None
        self.plans = {}
        self.decision_history = []
        self.strategy_patterns = defaultdict(list)
        self.performance_metrics = {}
        
        self._initialize_llm()
        self._load_strategies()
    
    def _initialize_llm(self):
        """Inicializa el modelo de lenguaje"""
        try:
            self.llm = ChatOpenAI(
                temperature=0.3,
                model_name="gpt-3.5-turbo",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("LLM inicializado para planificación")
        except Exception as e:
            logger.error(f"Error inicializando LLM: {str(e)}")
    
    def _load_strategies(self):
        """Carga estrategias de planificación predefinidas"""
        self.strategies = {
            "simple_query": {
                "pattern": ["query"],
                "success_rate": 0.9,
                "avg_duration": 5
            },
            "complex_analysis": {
                "pattern": ["query", "reasoning", "writing"],
                "success_rate": 0.8,
                "avg_duration": 30
            },
            "document_generation": {
                "pattern": ["query", "writing"],
                "success_rate": 0.85,
                "avg_duration": 20
            },
            "multi_step_research": {
                "pattern": ["query", "reasoning", "query", "writing"],
                "success_rate": 0.75,
                "avg_duration": 45
            }
        }
    
    def create_plan(self, request: str, analysis: Dict[str, Any], context: Any) -> Plan:
        """
        Crea un plan para resolver una solicitud
        
        Args:
            request: Solicitud del usuario
            analysis: Análisis de la solicitud
            context: Contexto del agente
            
        Returns:
            Plan de ejecución
        """
        try:
            # Determinar tipo de planificación
            plan_type = self._determine_plan_type(analysis)
            
            # Crear contexto de decisión
            decision_context = DecisionContext(
                user_type=context.user_type if context else "estudiante",
                task_complexity=analysis.get("complexity", "simple"),
                available_tools=analysis.get("tools_needed", []),
                memory_context={},
                constraints={},
                preferences={}
            )
            
            # Generar plan usando LLM
            plan_steps = self._generate_plan_steps(request, analysis, decision_context)
            
            # Crear plan
            plan = Plan(
                id=f"plan_{datetime.now().timestamp()}",
                name=f"Plan para: {request[:50]}...",
                description=request,
                steps=plan_steps,
                status=PlanStatus.CREATED,
                created_at=datetime.now(),
                total_estimated_duration=sum(step.estimated_duration for step in plan_steps)
            )
            
            # Almacenar plan
            self.plans[plan.id] = plan
            
            logger.info(f"Plan creado: {plan.id} con {len(plan_steps)} pasos")
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creando plan: {str(e)}")
            raise
    
    def _determine_plan_type(self, analysis: Dict[str, Any]) -> str:
        """Determina el tipo de planificación necesario"""
        complexity = analysis.get("complexity", "simple")
        tools_needed = analysis.get("tools_needed", [])
        
        if complexity == "simple" and len(tools_needed) == 1:
            return "sequential"
        elif complexity == "complex" and len(tools_needed) > 1:
            return "hierarchical"
        elif "iterative" in analysis.get("intent", ""):
            return "iterative"
        else:
            return "adaptive"
    
    def _generate_plan_steps(self, request: str, analysis: Dict[str, Any], context: DecisionContext) -> List[PlanStep]:
        """Genera pasos del plan usando LLM"""
        try:
            # Crear prompt para generación de plan
            prompt = self._create_planning_prompt(request, analysis, context)
            
            # Generar respuesta del LLM
            response = self.llm.predict(prompt)
            
            # Parsear respuesta en pasos
            steps = self._parse_plan_response(response, analysis)
            
            return steps
            
        except Exception as e:
            logger.error(f"Error generando pasos del plan: {str(e)}")
            # Fallback a plan simple
            return self._create_fallback_plan(analysis)
    
    def _create_planning_prompt(self, request: str, analysis: Dict[str, Any], context: DecisionContext) -> str:
        """Crea prompt para planificación"""
        tools_info = "\n".join([f"- {tool}: {self._get_tool_description(tool)}" for tool in analysis.get("tools_needed", [])])
        
        return f"""
Eres un experto en planificación de tareas para un agente inteligente escolar.

SOLICITUD: {request}

ANÁLISIS:
- Complejidad: {analysis.get('complexity', 'simple')}
- Intención: {analysis.get('intent', 'unknown')}
- Herramientas necesarias: {', '.join(analysis.get('tools_needed', []))}

CONTEXTO:
- Tipo de usuario: {context.user_type}
- Complejidad de tarea: {context.task_complexity}

HERRAMIENTAS DISPONIBLES:
{tools_info}

INSTRUCCIONES:
Crea un plan paso a paso para resolver la solicitud. Cada paso debe incluir:
1. Descripción clara de la acción
2. Herramienta a utilizar
3. Parámetros necesarios
4. Dependencias con otros pasos
5. Duración estimada en segundos
6. Prioridad (1-5)

FORMATO DE RESPUESTA:
Paso 1: [Descripción]
- Herramienta: [nombre_herramienta]
- Acción: [acción_específica]
- Parámetros: [parámetros_json]
- Dependencias: [lista_dependencias]
- Duración: [segundos]
- Prioridad: [1-5]

Paso 2: [Descripción]
...

RESPUESTA:
"""
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Obtiene descripción de una herramienta"""
        descriptions = {
            "query": "Buscar información en documentos escolares",
            "writing": "Generar documentos, reportes y comunicados",
            "reasoning": "Analizar información y tomar decisiones"
        }
        return descriptions.get(tool_name, "Herramienta desconocida")
    
    def _parse_plan_response(self, response: str, analysis: Dict[str, Any]) -> List[PlanStep]:
        """Parsea la respuesta del LLM en pasos del plan"""
        steps = []
        step_id = 1
        
        try:
            lines = response.split('\n')
            current_step = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('Paso'):
                    # Finalizar paso anterior
                    if current_step:
                        steps.append(current_step)
                    
                    # Iniciar nuevo paso
                    description = line.split(':', 1)[1].strip() if ':' in line else line
                    current_step = PlanStep(
                        id=f"step_{step_id}",
                        description=description,
                        tool="",
                        action="",
                        parameters={},
                        dependencies=[],
                        estimated_duration=10,
                        priority=3
                    )
                    step_id += 1
                
                elif current_step and line.startswith('-'):
                    # Parsear atributos del paso
                    if line.startswith('- Herramienta:'):
                        current_step.tool = line.split(':', 1)[1].strip()
                    elif line.startswith('- Acción:'):
                        current_step.action = line.split(':', 1)[1].strip()
                    elif line.startswith('- Parámetros:'):
                        try:
                            params_str = line.split(':', 1)[1].strip()
                            current_step.parameters = json.loads(params_str) if params_str != '{}' else {}
                        except:
                            current_step.parameters = {}
                    elif line.startswith('- Dependencias:'):
                        deps_str = line.split(':', 1)[1].strip()
                        current_step.dependencies = [d.strip() for d in deps_str.split(',') if d.strip()]
                    elif line.startswith('- Duración:'):
                        try:
                            current_step.estimated_duration = int(line.split(':', 1)[1].strip())
                        except:
                            current_step.estimated_duration = 10
                    elif line.startswith('- Prioridad:'):
                        try:
                            current_step.priority = int(line.split(':', 1)[1].strip())
                        except:
                            current_step.priority = 3
            
            # Agregar último paso
            if current_step:
                steps.append(current_step)
            
            # Validar y ajustar pasos
            steps = self._validate_and_adjust_steps(steps, analysis)
            
            return steps
            
        except Exception as e:
            logger.error(f"Error parseando respuesta del plan: {str(e)}")
            return self._create_fallback_plan(analysis)
    
    def _validate_and_adjust_steps(self, steps: List[PlanStep], analysis: Dict[str, Any]) -> List[PlanStep]:
        """Valida y ajusta los pasos del plan"""
        try:
            # Asegurar que cada paso tenga una herramienta válida
            available_tools = analysis.get("tools_needed", [])
            
            for step in steps:
                if step.tool not in available_tools and available_tools:
                    step.tool = available_tools[0]  # Usar primera herramienta disponible
                
                # Asegurar parámetros básicos
                if not step.parameters:
                    step.parameters = {}
                
                # Ajustar duración si es muy alta o muy baja
                if step.estimated_duration < 1:
                    step.estimated_duration = 5
                elif step.estimated_duration > 300:
                    step.estimated_duration = 60
            
            return steps
            
        except Exception as e:
            logger.error(f"Error validando pasos: {str(e)}")
            return steps
    
    def _create_fallback_plan(self, analysis: Dict[str, Any]) -> List[PlanStep]:
        """Crea un plan de respaldo simple"""
        tools_needed = analysis.get("tools_needed", ["query"])
        
        steps = []
        for i, tool in enumerate(tools_needed):
            step = PlanStep(
                id=f"fallback_step_{i+1}",
                description=f"Ejecutar {tool}",
                tool=tool,
                action="execute",
                parameters={},
                dependencies=[],
                estimated_duration=10,
                priority=3
            )
            steps.append(step)
        
        return steps
    
    def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Ejecuta un plan
        
        Args:
            plan_id: ID del plan a ejecutar
            
        Returns:
            Resultado de la ejecución
        """
        try:
            if plan_id not in self.plans:
                raise ValueError(f"Plan {plan_id} no encontrado")
            
            plan = self.plans[plan_id]
            plan.status = PlanStatus.EXECUTING
            
            results = []
            start_time = datetime.now()
            
            # Ejecutar pasos en orden
            for step in plan.steps:
                try:
                    step.status = "executing"
                    result = self._execute_step(step)
                    step.result = result
                    step.status = "completed"
                    results.append(result)
                    
                except Exception as e:
                    step.status = "failed"
                    step.error = str(e)
                    logger.error(f"Error ejecutando paso {step.id}: {str(e)}")
                    results.append(f"Error: {str(e)}")
            
            # Finalizar plan
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.now()
            plan.actual_duration = (plan.completed_at - start_time).total_seconds()
            
            # Calcular tasa de éxito
            successful_steps = sum(1 for step in plan.steps if step.status == "completed")
            plan.success_rate = successful_steps / len(plan.steps) if plan.steps else 0.0
            
            # Actualizar métricas
            self._update_performance_metrics(plan)
            
            logger.info(f"Plan {plan_id} ejecutado. Tasa de éxito: {plan.success_rate:.2f}")
            
            return {
                "plan_id": plan_id,
                "status": plan.status.value,
                "results": results,
                "success_rate": plan.success_rate,
                "duration": plan.actual_duration
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando plan: {str(e)}")
            if plan_id in self.plans:
                self.plans[plan_id].status = PlanStatus.FAILED
            raise
    
    def _execute_step(self, step: PlanStep) -> Any:
        """Ejecuta un paso individual del plan"""
        # Esta función sería implementada por el orquestador del agente
        # que tiene acceso a las herramientas reales
        return f"Ejecutado: {step.description}"
    
    def make_decision(self, context: DecisionContext, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Toma una decisión basada en contexto y opciones
        
        Args:
            context: Contexto de decisión
            options: Opciones disponibles
            
        Returns:
            Decisión tomada
        """
        try:
            # Analizar contexto
            context_analysis = self._analyze_decision_context(context)
            
            # Evaluar opciones
            evaluated_options = self._evaluate_options(options, context_analysis)
            
            # Seleccionar mejor opción
            decision = self._select_best_option(evaluated_options, context_analysis)
            
            # Registrar decisión
            self._record_decision(context, options, decision)
            
            logger.info(f"Decisión tomada: {decision['choice']}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error tomando decisión: {str(e)}")
            raise
    
    def _analyze_decision_context(self, context: DecisionContext) -> Dict[str, Any]:
        """Analiza el contexto de decisión"""
        return {
            "user_type": context.user_type,
            "complexity": context.task_complexity,
            "available_resources": len(context.available_tools),
            "constraints": context.constraints,
            "preferences": context.preferences
        }
    
    def _evaluate_options(self, options: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evalúa las opciones disponibles"""
        evaluated = []
        
        for option in options:
            score = self._calculate_option_score(option, context)
            option["score"] = score
            evaluated.append(option)
        
        return sorted(evaluated, key=lambda x: x["score"], reverse=True)
    
    def _calculate_option_score(self, option: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calcula puntuación de una opción"""
        score = 0.5  # Base
        
        # Factor de complejidad
        if option.get("complexity") == context.get("complexity"):
            score += 0.2
        
        # Factor de recursos disponibles
        if option.get("required_tools", []) and all(tool in context.get("available_resources", []) for tool in option["required_tools"]):
            score += 0.2
        
        # Factor de preferencias del usuario
        if option.get("type") in context.get("preferences", {}).get("preferred_types", []):
            score += 0.1
        
        return min(1.0, score)
    
    def _select_best_option(self, evaluated_options: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Selecciona la mejor opción"""
        if not evaluated_options:
            return {"choice": "none", "reason": "No hay opciones disponibles"}
        
        best_option = evaluated_options[0]
        
        return {
            "choice": best_option.get("id", "unknown"),
            "reason": f"Mejor puntuación: {best_option['score']:.2f}",
            "option": best_option,
            "alternatives": evaluated_options[1:3]  # Top 3 alternativas
        }
    
    def _record_decision(self, context: DecisionContext, options: List[Dict[str, Any]], decision: Dict[str, Any]):
        """Registra la decisión tomada"""
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "context": asdict(context),
            "options": options,
            "decision": decision
        }
        
        self.decision_history.append(decision_record)
        
        # Mantener solo los últimos 100 registros
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
    
    def _update_performance_metrics(self, plan: Plan):
        """Actualiza métricas de rendimiento"""
        plan_type = self._get_plan_type(plan)
        
        if plan_type not in self.performance_metrics:
            self.performance_metrics[plan_type] = {
                "total_plans": 0,
                "successful_plans": 0,
                "avg_duration": 0.0,
                "avg_success_rate": 0.0
            }
        
        metrics = self.performance_metrics[plan_type]
        metrics["total_plans"] += 1
        
        if plan.success_rate > 0.8:
            metrics["successful_plans"] += 1
        
        # Actualizar promedios
        total = metrics["total_plans"]
        metrics["avg_duration"] = (
            (metrics["avg_duration"] * (total - 1) + plan.actual_duration) / total
        )
        metrics["avg_success_rate"] = (
            (metrics["avg_success_rate"] * (total - 1) + plan.success_rate) / total
        )
    
    def _get_plan_type(self, plan: Plan) -> str:
        """Determina el tipo de plan"""
        tools_used = [step.tool for step in plan.steps]
        
        if len(tools_used) == 1:
            return f"single_{tools_used[0]}"
        elif len(tools_used) == 2:
            return f"dual_{'_'.join(sorted(tools_used))}"
        else:
            return "multi_tool"
    
    def update_strategies(self, feedback: Dict[str, Any]):
        """Actualiza estrategias basadas en feedback"""
        try:
            strategy_type = feedback.get("strategy_type")
            success = feedback.get("success", False)
            duration = feedback.get("duration", 0)
            
            if strategy_type and strategy_type in self.strategies:
                strategy = self.strategies[strategy_type]
                
                # Actualizar tasa de éxito
                current_success_rate = strategy["success_rate"]
                strategy["success_rate"] = (current_success_rate + (1.0 if success else 0.0)) / 2
                
                # Actualizar duración promedio
                current_avg_duration = strategy["avg_duration"]
                strategy["avg_duration"] = (current_avg_duration + duration) / 2
                
                logger.info(f"Estrategia {strategy_type} actualizada")
            
        except Exception as e:
            logger.error(f"Error actualizando estrategias: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del motor de planificación"""
        return {
            "total_plans": len(self.plans),
            "active_plans": sum(1 for plan in self.plans.values() if plan.status == PlanStatus.EXECUTING),
            "completed_plans": sum(1 for plan in self.plans.values() if plan.status == PlanStatus.COMPLETED),
            "performance_metrics": self.performance_metrics,
            "strategies": self.strategies,
            "decision_history_count": len(self.decision_history)
        }
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Obtiene un plan por ID"""
        return self.plans.get(plan_id)
    
    def get_plans_by_status(self, status: PlanStatus) -> List[Plan]:
        """Obtiene planes por estado"""
        return [plan for plan in self.plans.values() if plan.status == status]
    
    def cancel_plan(self, plan_id: str) -> bool:
        """Cancela un plan"""
        try:
            if plan_id in self.plans:
                self.plans[plan_id].status = PlanStatus.CANCELLED
                logger.info(f"Plan {plan_id} cancelado")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelando plan: {str(e)}")
            return False

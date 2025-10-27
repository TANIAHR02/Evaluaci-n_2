"""
SchoolBot Agent - Tools Module
Herramientas de Consulta, Escritura y Razonamiento

Autor: Tania Herrera
Fecha: Diciembre 2024
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

# LangChain imports
from langchain.tools import BaseTool
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

# Local imports
from ..retriever.retriever import SemanticRetriever
from ..prompts.main_prompts import MainPrompts

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Resultado de ejecución de herramienta"""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseAgentTool(ABC):
    """Clase base para herramientas del agente"""
    
    def __init__(self, config: Dict[str, Any], memory_manager=None):
        self.config = config
        self.memory_manager = memory_manager
        self.name = self.__class__.__name__.lower().replace("tool", "")
        self.description = self._get_description()
    
    @abstractmethod
    def _get_description(self) -> str:
        """Obtiene descripción de la herramienta"""
        pass
    
    @abstractmethod
    def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Ejecuta la herramienta"""
        pass
    
    def _log_execution(self, action: str, parameters: Dict[str, Any], result: ToolResult):
        """Registra la ejecución de la herramienta"""
        logger.info(f"Herramienta {self.name} ejecutada: {action}")
        if not result.success:
            logger.error(f"Error en {self.name}: {result.error}")

class QueryTool(BaseAgentTool):
    """
    Herramienta de consulta para buscar información en documentos escolares
    
    Capacidades:
    - Búsqueda semántica en documentos
    - Recuperación de contexto relevante
    - Filtrado por tipo de usuario
    - Sugerencias de búsqueda
    """
    
    def __init__(self, retriever_config: Dict[str, Any], memory_manager=None):
        super().__init__(retriever_config, memory_manager)
        self.retriever = None
        self._initialize_retriever()
    
    def _get_description(self) -> str:
        return "Buscar información en documentos escolares del Colegio San Ignacio Digital"
    
    def _initialize_retriever(self):
        """Inicializa el retriever semántico"""
        try:
            self.retriever = SemanticRetriever()
            self.retriever.initialize_models()
            self.retriever.initialize_vector_db()
            logger.info("QueryTool: Retriever inicializado")
        except Exception as e:
            logger.error(f"Error inicializando retriever: {str(e)}")
            self.retriever = None
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Ejecuta acciones de consulta
        
        Acciones disponibles:
        - search: Búsqueda semántica
        - suggest: Sugerencias de búsqueda
        - filter: Filtrar resultados
        - context: Obtener contexto adicional
        """
        try:
            if action == "search":
                return self._search_documents(parameters)
            elif action == "suggest":
                return self._get_suggestions(parameters)
            elif action == "filter":
                return self._filter_results(parameters)
            elif action == "context":
                return self._get_context(parameters)
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Acción '{action}' no soportada por QueryTool"
                )
        
        except Exception as e:
            logger.error(f"Error ejecutando QueryTool: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _search_documents(self, parameters: Dict[str, Any]) -> ToolResult:
        """Busca documentos relevantes"""
        try:
            query = parameters.get("query", "")
            user_type = parameters.get("user_type", "estudiante")
            top_k = parameters.get("top_k", 5)
            
            if not self.retriever:
                return ToolResult(
                    success=False,
                    result=None,
                    error="Retriever no inicializado"
                )
            
            # Realizar búsqueda
            results = self.retriever.search(
                query=query,
                user_type=user_type,
                top_k=top_k,
                use_reranking=True
            )
            
            # Buscar en memoria si hay resultados limitados
            if len(results) < 3 and self.memory_manager:
                memory_results = self.memory_manager.retrieve_memory(
                    query=query,
                    limit=3
                )
                
                # Convertir resultados de memoria al formato esperado
                for mem_result in memory_results:
                    results.append({
                        "text": mem_result.content,
                        "metadata": {
                            "file_name": f"memoria_{mem_result.id}",
                            "source": "memory",
                            "timestamp": mem_result.timestamp.isoformat()
                        },
                        "similarity_score": 0.7
                    })
            
            return ToolResult(
                success=True,
                result=results,
                metadata={
                    "query": query,
                    "user_type": user_type,
                    "results_count": len(results)
                }
            )
            
        except Exception as e:
            logger.error(f"Error en búsqueda de documentos: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _get_suggestions(self, parameters: Dict[str, Any]) -> ToolResult:
        """Obtiene sugerencias de búsqueda"""
        try:
            partial_query = parameters.get("query", "")
            
            if not self.retriever:
                return ToolResult(
                    success=False,
                    result=[],
                    error="Retriever no inicializado"
                )
            
            suggestions = self.retriever.get_search_suggestions(partial_query)
            
            return ToolResult(
                success=True,
                result=suggestions,
                metadata={"partial_query": partial_query}
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo sugerencias: {str(e)}")
            return ToolResult(
                success=False,
                result=[],
                error=str(e)
            )
    
    def _filter_results(self, parameters: Dict[str, Any]) -> ToolResult:
        """Filtra resultados de búsqueda"""
        try:
            results = parameters.get("results", [])
            filters = parameters.get("filters", {})
            
            filtered_results = results.copy()
            
            # Filtrar por tipo de documento
            if "document_type" in filters:
                doc_type = filters["document_type"]
                filtered_results = [
                    r for r in filtered_results
                    if r.get("metadata", {}).get("document_type") == doc_type
                ]
            
            # Filtrar por fecha
            if "date_range" in filters:
                start_date = filters["date_range"].get("start")
                end_date = filters["date_range"].get("end")
                # Implementar filtrado por fecha si es necesario
            
            # Filtrar por relevancia mínima
            if "min_relevance" in filters:
                min_score = filters["min_relevance"]
                filtered_results = [
                    r for r in filtered_results
                    if r.get("similarity_score", 0) >= min_score
                ]
            
            return ToolResult(
                success=True,
                result=filtered_results,
                metadata={
                    "original_count": len(results),
                    "filtered_count": len(filtered_results),
                    "filters_applied": list(filters.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"Error filtrando resultados: {str(e)}")
            return ToolResult(
                success=False,
                result=[],
                error=str(e)
            )
    
    def _get_context(self, parameters: Dict[str, Any]) -> ToolResult:
        """Obtiene contexto adicional"""
        try:
            topic = parameters.get("topic", "")
            
            # Buscar contexto en memoria
            context_results = []
            if self.memory_manager:
                context_results = self.memory_manager.retrieve_memory(
                    query=topic,
                    memory_type="semantic",
                    limit=3
                )
            
            return ToolResult(
                success=True,
                result=context_results,
                metadata={"topic": topic}
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {str(e)}")
            return ToolResult(
                success=False,
                result=[],
                error=str(e)
            )

class WritingTool(BaseAgentTool):
    """
    Herramienta de escritura para generar documentos escolares
    
    Capacidades:
    - Generación de reportes
    - Creación de comunicados
    - Redacción de documentos administrativos
    - Formateo automático
    """
    
    def __init__(self, templates_config: Dict[str, Any], memory_manager=None):
        super().__init__(templates_config, memory_manager)
        self.llm = None
        self.templates = {}
        self._initialize_llm()
        self._load_templates()
    
    def _get_description(self) -> str:
        return "Generar documentos, reportes y comunicados escolares"
    
    def _initialize_llm(self):
        """Inicializa el modelo de lenguaje"""
        try:
            self.llm = ChatOpenAI(
                temperature=0.3,
                model_name="gpt-3.5-turbo",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("WritingTool: LLM inicializado")
        except Exception as e:
            logger.error(f"Error inicializando LLM: {str(e)}")
    
    def _load_templates(self):
        """Carga plantillas de documentos"""
        self.templates = {
            "reporte_academico": {
                "template": """
REPORTE ACADÉMICO - COLEGIO SAN IGNACIO DIGITAL

Fecha: {fecha}
Estudiante: {estudiante}
Curso: {curso}
Período: {periodo}

RESUMEN ACADÉMICO:
{resumen_academico}

ÁREAS DE FORTALEZA:
{fortalezas}

ÁREAS DE MEJORA:
{mejoras}

RECOMENDACIONES:
{recomendaciones}

Observaciones adicionales:
{observaciones}

Profesor(a): {profesor}
""",
                "required_fields": ["estudiante", "curso", "periodo", "resumen_academico"]
            },
            "comunicado_apoderados": {
                "template": """
COMUNICADO A APODERADOS
COLEGIO SAN IGNACIO DIGITAL

Estimados Apoderados:

{contenido}

Fecha: {fecha}
Horario: {horario}
Lugar: {lugar}

Informaciones adicionales:
{informaciones_adicionales}

Atentamente,
{remitente}
Colegio San Ignacio Digital
""",
                "required_fields": ["contenido", "fecha"]
            },
            "acta_reunion": {
                "template": """
ACTA DE REUNIÓN
COLEGIO SAN IGNACIO DIGITAL

Fecha: {fecha}
Hora: {hora}
Lugar: {lugar}
Tipo de reunión: {tipo_reunion}

ASISTENTES:
{asistentes}

AGENDA:
{agenda}

DESARROLLO:
{desarrollo}

ACUERDOS:
{acuerdos}

PRÓXIMA REUNIÓN:
{proxima_reunion}

Secretario(a): {secretario}
""",
                "required_fields": ["fecha", "tipo_reunion", "asistentes", "agenda"]
            }
        }
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Ejecuta acciones de escritura
        
        Acciones disponibles:
        - generate: Generar documento
        - format: Formatear texto
        - summarize: Resumir información
        - translate: Traducir texto
        """
        try:
            if action == "generate":
                return self._generate_document(parameters)
            elif action == "format":
                return self._format_text(parameters)
            elif action == "summarize":
                return self._summarize_text(parameters)
            elif action == "translate":
                return self._translate_text(parameters)
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Acción '{action}' no soportada por WritingTool"
                )
        
        except Exception as e:
            logger.error(f"Error ejecutando WritingTool: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _generate_document(self, parameters: Dict[str, Any]) -> ToolResult:
        """Genera un documento usando plantillas"""
        try:
            document_type = parameters.get("document_type", "")
            content_data = parameters.get("content", {})
            
            if document_type not in self.templates:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Tipo de documento '{document_type}' no soportado"
                )
            
            template = self.templates[document_type]
            required_fields = template["required_fields"]
            
            # Verificar campos requeridos
            missing_fields = [field for field in required_fields if field not in content_data]
            if missing_fields:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Campos requeridos faltantes: {missing_fields}"
                )
            
            # Agregar fecha actual si no está presente
            if "fecha" not in content_data:
                content_data["fecha"] = datetime.now().strftime("%d/%m/%Y")
            
            # Generar documento
            document = template["template"].format(**content_data)
            
            return ToolResult(
                success=True,
                result=document,
                metadata={
                    "document_type": document_type,
                    "template_used": document_type,
                    "fields_provided": list(content_data.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"Error generando documento: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _format_text(self, parameters: Dict[str, Any]) -> ToolResult:
        """Formatea texto según especificaciones"""
        try:
            text = parameters.get("text", "")
            format_type = parameters.get("format_type", "standard")
            
            if format_type == "academic":
                formatted_text = self._format_academic_text(text)
            elif format_type == "formal":
                formatted_text = self._format_formal_text(text)
            elif format_type == "bullet_points":
                formatted_text = self._format_bullet_points(text)
            else:
                formatted_text = text
            
            return ToolResult(
                success=True,
                result=formatted_text,
                metadata={"format_type": format_type}
            )
            
        except Exception as e:
            logger.error(f"Error formateando texto: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _format_academic_text(self, text: str) -> str:
        """Formatea texto para uso académico"""
        # Implementar formateo académico
        return text
    
    def _format_formal_text(self, text: str) -> str:
        """Formatea texto para uso formal"""
        # Implementar formateo formal
        return text
    
    def _format_bullet_points(self, text: str) -> str:
        """Convierte texto a puntos de lista"""
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line:
                bullet_points.append(f"• {line}")
        
        return '\n'.join(bullet_points)
    
    def _summarize_text(self, parameters: Dict[str, Any]) -> ToolResult:
        """Resume texto usando LLM"""
        try:
            text = parameters.get("text", "")
            max_length = parameters.get("max_length", 200)
            
            if not self.llm:
                return ToolResult(
                    success=False,
                    result=None,
                    error="LLM no inicializado"
                )
            
            prompt = f"""
Resume el siguiente texto en máximo {max_length} palabras, manteniendo la información más importante:

{text}

RESUMEN:
"""
            
            summary = self.llm.predict(prompt)
            
            return ToolResult(
                success=True,
                result=summary,
                metadata={
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "max_length": max_length
                }
            )
            
        except Exception as e:
            logger.error(f"Error resumiendo texto: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _translate_text(self, parameters: Dict[str, Any]) -> ToolResult:
        """Traduce texto usando LLM"""
        try:
            text = parameters.get("text", "")
            target_language = parameters.get("target_language", "español")
            
            if not self.llm:
                return ToolResult(
                    success=False,
                    result=None,
                    error="LLM no inicializado"
                )
            
            prompt = f"""
Traduce el siguiente texto al {target_language}, manteniendo el contexto educativo:

{text}

TRADUCCIÓN:
"""
            
            translation = self.llm.predict(prompt)
            
            return ToolResult(
                success=True,
                result=translation,
                metadata={
                    "target_language": target_language,
                    "original_text": text
                }
            )
            
        except Exception as e:
            logger.error(f"Error traduciendo texto: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

class ReasoningTool(BaseAgentTool):
    """
    Herramienta de razonamiento para análisis y toma de decisiones
    
    Capacidades:
    - Análisis de información
    - Evaluación de opciones
    - Toma de decisiones
    - Razonamiento lógico
    """
    
    def __init__(self, llm_config: Dict[str, Any], memory_manager=None):
        super().__init__(llm_config, memory_manager)
        self.llm = None
        self._initialize_llm()
    
    def _get_description(self) -> str:
        return "Analizar información, evaluar opciones y tomar decisiones"
    
    def _initialize_llm(self):
        """Inicializa el modelo de lenguaje"""
        try:
            self.llm = ChatOpenAI(
                temperature=0.2,
                model_name="gpt-3.5-turbo",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("ReasoningTool: LLM inicializado")
        except Exception as e:
            logger.error(f"Error inicializando LLM: {str(e)}")
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Ejecuta acciones de razonamiento
        
        Acciones disponibles:
        - analyze: Analizar información
        - evaluate: Evaluar opciones
        - decide: Tomar decisión
        - synthesize: Sintetizar resultados
        """
        try:
            if action == "analyze":
                return self._analyze_information(parameters)
            elif action == "evaluate":
                return self._evaluate_options(parameters)
            elif action == "decide":
                return self._make_decision(parameters)
            elif action == "synthesize":
                return self._synthesize_results(parameters)
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Acción '{action}' no soportada por ReasoningTool"
                )
        
        except Exception as e:
            logger.error(f"Error ejecutando ReasoningTool: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _analyze_information(self, parameters: Dict[str, Any]) -> ToolResult:
        """Analiza información proporcionada"""
        try:
            information = parameters.get("information", "")
            analysis_type = parameters.get("analysis_type", "general")
            
            if not self.llm:
                return ToolResult(
                    success=False,
                    result=None,
                    error="LLM no inicializado"
                )
            
            prompt = f"""
Analiza la siguiente información desde una perspectiva educativa escolar:

INFORMACIÓN:
{information}

TIPO DE ANÁLISIS: {analysis_type}

Proporciona un análisis estructurado que incluya:
1. Puntos clave identificados
2. Implicaciones para el contexto escolar
3. Recomendaciones basadas en la información
4. Posibles áreas de mejora

ANÁLISIS:
"""
            
            analysis = self.llm.predict(prompt)
            
            return ToolResult(
                success=True,
                result=analysis,
                metadata={
                    "analysis_type": analysis_type,
                    "information_length": len(information)
                }
            )
            
        except Exception as e:
            logger.error(f"Error analizando información: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _evaluate_options(self, parameters: Dict[str, Any]) -> ToolResult:
        """Evalúa opciones disponibles"""
        try:
            options = parameters.get("options", [])
            criteria = parameters.get("criteria", [])
            context = parameters.get("context", "")
            
            if not self.llm:
                return ToolResult(
                    success=False,
                    result=None,
                    error="LLM no inicializado"
                )
            
            options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
            criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
            
            prompt = f"""
Evalúa las siguientes opciones considerando el contexto educativo escolar:

OPCIONES:
{options_text}

CRITERIOS DE EVALUACIÓN:
{criteria_text}

CONTEXTO:
{context}

Proporciona una evaluación estructurada que incluya:
1. Análisis de cada opción
2. Pros y contras
3. Recomendación final
4. Justificación de la decisión

EVALUACIÓN:
"""
            
            evaluation = self.llm.predict(prompt)
            
            return ToolResult(
                success=True,
                result=evaluation,
                metadata={
                    "options_count": len(options),
                    "criteria_count": len(criteria)
                }
            )
            
        except Exception as e:
            logger.error(f"Error evaluando opciones: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _make_decision(self, parameters: Dict[str, Any]) -> ToolResult:
        """Toma una decisión basada en información"""
        try:
            situation = parameters.get("situation", "")
            options = parameters.get("options", [])
            constraints = parameters.get("constraints", [])
            
            if not self.llm:
                return ToolResult(
                    success=False,
                    result=None,
                    error="LLM no inicializado"
                )
            
            options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
            constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
            
            prompt = f"""
Toma una decisión informada considerando el contexto educativo:

SITUACIÓN:
{situation}

OPCIONES DISPONIBLES:
{options_text}

RESTRICCIONES:
{constraints_text}

Proporciona una decisión estructurada que incluya:
1. Decisión recomendada
2. Razones principales
3. Consideraciones adicionales
4. Plan de implementación

DECISIÓN:
"""
            
            decision = self.llm.predict(prompt)
            
            return ToolResult(
                success=True,
                result=decision,
                metadata={
                    "situation": situation,
                    "options_count": len(options),
                    "constraints_count": len(constraints)
                }
            )
            
        except Exception as e:
            logger.error(f"Error tomando decisión: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def _synthesize_results(self, parameters: Dict[str, Any]) -> ToolResult:
        """Sintetiza múltiples resultados"""
        try:
            results = parameters.get("results", [])
            original_request = parameters.get("original_request", "")
            
            if not self.llm:
                return ToolResult(
                    success=False,
                    result=None,
                    error="LLM no inicializado"
                )
            
            results_text = "\n\n".join([f"Resultado {i+1}:\n{result}" for i, result in enumerate(results)])
            
            prompt = f"""
Sintetiza los siguientes resultados en una respuesta coherente y completa:

SOLICITUD ORIGINAL:
{original_request}

RESULTADOS OBTENIDOS:
{results_text}

Proporciona una síntesis que incluya:
1. Resumen de los hallazgos principales
2. Información más relevante
3. Conclusiones clave
4. Recomendaciones finales

SÍNTESIS:
"""
            
            synthesis = self.llm.predict(prompt)
            
            return ToolResult(
                success=True,
                result=synthesis,
                metadata={
                    "results_count": len(results),
                    "original_request": original_request
                }
            )
            
        except Exception as e:
            logger.error(f"Error sintetizando resultados: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )
    
    def analyze_intent(self, request: str) -> Dict[str, Any]:
        """Analiza la intención de una solicitud"""
        try:
            if not self.llm:
                return {"intent": "unknown", "complexity": "simple"}
            
            prompt = f"""
Analiza la intención de la siguiente solicitud en el contexto educativo:

SOLICITUD: "{request}"

Determina:
1. Intención principal (consulta, solicitud, queja, sugerencia, etc.)
2. Complejidad (simple, moderada, compleja)
3. Tipo de respuesta esperada (informativa, procedimental, analítica)
4. Urgencia (baja, media, alta)

Responde en formato JSON:
{{
    "intent": "tipo_de_intencion",
    "complexity": "nivel_de_complejidad",
    "response_type": "tipo_de_respuesta",
    "urgency": "nivel_de_urgencia"
}}
"""
            
            response = self.llm.predict(prompt)
            
            try:
                # Intentar parsear JSON
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            
            # Fallback si no se puede parsear JSON
            return {
                "intent": "unknown",
                "complexity": "simple",
                "response_type": "informativa",
                "urgency": "media"
            }
            
        except Exception as e:
            logger.error(f"Error analizando intención: {str(e)}")
            return {
                "intent": "unknown",
                "complexity": "simple",
                "response_type": "informativa",
                "urgency": "media"
            }

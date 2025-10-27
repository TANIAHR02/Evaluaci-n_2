"""
SchoolBot Agent - Demo y Ejemplos de Uso
Demostración del Agente Inteligente Escolar

Autor: Tania Herrera
Fecha: Diciembre 2024
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Importar componentes del agente
from .orchestrator import AgentOrchestrator, create_agent_orchestrator
from .config import get_complete_config

class SchoolBotAgentDemo:
    """
    Demostración del agente SchoolBot con ejemplos prácticos
    """
    
    def __init__(self):
        self.orchestrator = None
        self.demo_sessions = {}
        
    def initialize(self, user_type: str = "estudiante", environment: str = "development"):
        """Inicializa el agente para la demostración"""
        try:
            # Obtener configuración
            config = get_complete_config(user_type, environment)
            
            # Crear orquestador
            self.orchestrator = create_agent_orchestrator()
            
            print("🤖 Agente SchoolBot inicializado correctamente")
            print(f"👤 Tipo de usuario: {user_type}")
            print(f"🌍 Entorno: {environment}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando agente: {str(e)}")
            return False
    
    def create_demo_session(self, user_id: str, user_type: str) -> str:
        """Crea una sesión de demostración"""
        try:
            session_id = self.orchestrator.create_session(
                user_id=user_id,
                user_type=user_type,
                context={"demo": True}
            )
            
            self.demo_sessions[session_id] = {
                "user_id": user_id,
                "user_type": user_type,
                "created_at": datetime.now()
            }
            
            print(f"✅ Sesión de demostración creada: {session_id}")
            return session_id
            
        except Exception as e:
            print(f"❌ Error creando sesión: {str(e)}")
            return None
    
    def demo_simple_query(self, session_id: str):
        """Demuestra consulta simple"""
        print("\n" + "="*60)
        print("🔍 DEMO: CONSULTA SIMPLE")
        print("="*60)
        
        request = "¿Cuáles son los horarios de clases del colegio?"
        
        print(f"📝 Solicitud: {request}")
        print("⏳ Procesando...")
        
        try:
            response = self.orchestrator.process_request(session_id, request)
            
            if response.get("error"):
                print(f"❌ Error: {response['error']}")
            else:
                print(f"✅ Respuesta: {response['response']}")
                print(f"📊 Análisis: {response.get('analysis', {}).get('complexity', 'N/A')}")
                print(f"🛠️ Herramientas usadas: {response.get('analysis', {}).get('tools_needed', [])}")
        
        except Exception as e:
            print(f"❌ Error en demo: {str(e)}")
    
    def demo_complex_task(self, session_id: str):
        """Demuestra tarea compleja con planificación"""
        print("\n" + "="*60)
        print("🧠 DEMO: TAREA COMPLEJA CON PLANIFICACIÓN")
        print("="*60)
        
        request = "Necesito generar un reporte académico completo para el estudiante Juan Pérez del curso 3°A, incluyendo análisis de rendimiento y recomendaciones de mejora"
        
        print(f"📝 Solicitud: {request}")
        print("⏳ Procesando con planificación...")
        
        try:
            response = self.orchestrator.process_request(session_id, request)
            
            if response.get("error"):
                print(f"❌ Error: {response['error']}")
            else:
                print(f"✅ Respuesta: {response['response']}")
                
                plan = response.get("plan")
                if plan:
                    print(f"📋 Plan creado: {plan.get('name', 'Sin nombre')}")
                    print(f"📊 Pasos del plan: {len(plan.get('steps', []))}")
                    
                    for i, step in enumerate(plan.get("steps", []), 1):
                        print(f"   {i}. {step.get('description', 'Sin descripción')}")
                        print(f"      Herramienta: {step.get('tool', 'N/A')}")
                        print(f"      Duración estimada: {step.get('estimated_duration', 0)}s")
        
        except Exception as e:
            print(f"❌ Error en demo: {str(e)}")
    
    def demo_memory_usage(self, session_id: str):
        """Demuestra uso de memoria"""
        print("\n" + "="*60)
        print("🧠 DEMO: USO DE MEMORIA")
        print("="*60)
        
        # Primera consulta
        request1 = "¿Cuándo son las vacaciones de invierno?"
        print(f"📝 Primera consulta: {request1}")
        
        try:
            response1 = self.orchestrator.process_request(session_id, request1)
            print(f"✅ Respuesta: {response1.get('response', 'Sin respuesta')}")
            
            # Segunda consulta que debería usar memoria
            request2 = "¿Y las vacaciones de verano?"
            print(f"\n📝 Segunda consulta: {request2}")
            
            response2 = self.orchestrator.process_request(session_id, request2)
            print(f"✅ Respuesta: {response2.get('response', 'Sin respuesta')}")
            
            # Mostrar estado de memoria
            agent_status = self.orchestrator.get_agent_status()
            memory_status = agent_status.get("agent_status", {}).get("memory_status")
            
            if memory_status:
                print(f"\n📊 Estado de memoria:")
                print(f"   - Entradas totales: {memory_status.get('stats', {}).get('total_entries', 0)}")
                print(f"   - Memoria de corto plazo: {memory_status.get('stats', {}).get('short_term_entries', 0)}")
                print(f"   - Memoria de largo plazo: {memory_status.get('stats', {}).get('long_term_entries', 0)}")
        
        except Exception as e:
            print(f"❌ Error en demo: {str(e)}")
    
    def demo_writing_tool(self, session_id: str):
        """Demuestra herramienta de escritura"""
        print("\n" + "="*60)
        print("✍️ DEMO: HERRAMIENTA DE ESCRITURA")
        print("="*60)
        
        request = "Genera un comunicado para los apoderados informando sobre la próxima reunión de padres del 15 de diciembre a las 19:00 horas en el auditorio principal"
        
        print(f"📝 Solicitud: {request}")
        print("⏳ Generando documento...")
        
        try:
            response = self.orchestrator.process_request(session_id, request)
            
            if response.get("error"):
                print(f"❌ Error: {response['error']}")
            else:
                print(f"✅ Documento generado:")
                print("-" * 40)
                print(response.get('response', 'Sin respuesta'))
                print("-" * 40)
        
        except Exception as e:
            print(f"❌ Error en demo: {str(e)}")
    
    def demo_reasoning_tool(self, session_id: str):
        """Demuestra herramienta de razonamiento"""
        print("\n" + "="*60)
        print("🤔 DEMO: HERRAMIENTA DE RAZONAMIENTO")
        print("="*60)
        
        request = "Analiza las siguientes opciones para mejorar el rendimiento académico: 1) Implementar tutorías personalizadas, 2) Crear grupos de estudio, 3) Usar tecnología educativa. Considera costos, tiempo y efectividad."
        
        print(f"📝 Solicitud: {request}")
        print("⏳ Analizando opciones...")
        
        try:
            response = self.orchestrator.process_request(session_id, request)
            
            if response.get("error"):
                print(f"❌ Error: {response['error']}")
            else:
                print(f"✅ Análisis completado:")
                print("-" * 40)
                print(response.get('response', 'Sin respuesta'))
                print("-" * 40)
        
        except Exception as e:
            print(f"❌ Error en demo: {str(e)}")
    
    def demo_adaptive_behavior(self, session_id: str):
        """Demuestra comportamiento adaptativo"""
        print("\n" + "="*60)
        print("🔄 DEMO: COMPORTAMIENTO ADAPTATIVO")
        print("="*60)
        
        # Simular diferentes tipos de solicitudes
        requests = [
            "¿Qué necesito para matricularme?",
            "Genera un reporte de asistencia",
            "Analiza las calificaciones del curso 2°B",
            "¿Cuándo es la próxima reunión de apoderados?"
        ]
        
        for i, request in enumerate(requests, 1):
            print(f"\n📝 Solicitud {i}: {request}")
            print("⏳ Procesando...")
            
            try:
                response = self.orchestrator.process_request(session_id, request)
                
                if response.get("error"):
                    print(f"❌ Error: {response['error']}")
                else:
                    analysis = response.get("analysis", {})
                    print(f"✅ Respuesta generada")
                    print(f"📊 Complejidad: {analysis.get('complexity', 'N/A')}")
                    print(f"🛠️ Herramientas: {analysis.get('tools_needed', [])}")
                    print(f"🎯 Intención: {analysis.get('intent', 'N/A')}")
            
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def demo_system_status(self):
        """Demuestra estado del sistema"""
        print("\n" + "="*60)
        print("📊 DEMO: ESTADO DEL SISTEMA")
        print("="*60)
        
        try:
            status = self.orchestrator.get_agent_status()
            
            print("🤖 Estado del Agente:")
            agent_status = status.get("agent_status", {})
            print(f"   - Estado: {agent_status.get('state', 'N/A')}")
            print(f"   - Herramientas disponibles: {agent_status.get('tools_available', [])}")
            
            print("\n📈 Métricas del Sistema:")
            metrics = status.get("system_metrics", {})
            print(f"   - Sesiones totales: {metrics.get('total_sessions', 0)}")
            print(f"   - Sesiones activas: {metrics.get('active_sessions', 0)}")
            print(f"   - Solicitudes totales: {metrics.get('total_requests', 0)}")
            print(f"   - Solicitudes exitosas: {metrics.get('successful_requests', 0)}")
            print(f"   - Tiempo promedio de respuesta: {metrics.get('average_response_time', 0):.2f}s")
            
            print("\n🧠 Estado de Memoria:")
            memory_status = agent_status.get("memory_status")
            if memory_status:
                stats = memory_status.get("stats", {})
                print(f"   - Entradas totales: {stats.get('total_entries', 0)}")
                print(f"   - Memoria de corto plazo: {stats.get('short_term_entries', 0)}")
                print(f"   - Memoria de largo plazo: {stats.get('long_term_entries', 0)}")
                print(f"   - Tasa de aciertos: {stats.get('hit_rate', 0):.2f}")
            
            print("\n🎯 Estado de Planificación:")
            planning_status = agent_status.get("planning_status")
            if planning_status:
                print(f"   - Planes totales: {planning_status.get('total_plans', 0)}")
                print(f"   - Planes activos: {planning_status.get('active_plans', 0)}")
                print(f"   - Planes completados: {planning_status.get('completed_plans', 0)}")
        
        except Exception as e:
            print(f"❌ Error obteniendo estado: {str(e)}")
    
    def run_complete_demo(self):
        """Ejecuta demostración completa"""
        print("🚀 INICIANDO DEMOSTRACIÓN COMPLETA DEL AGENTE SCHOOLBOT")
        print("="*80)
        
        # Inicializar agente
        if not self.initialize("profesor", "development"):
            return
        
        # Crear sesión de demostración
        session_id = self.create_demo_session("demo_profesor", "profesor")
        if not session_id:
            return
        
        try:
            # Ejecutar demos
            self.demo_simple_query(session_id)
            self.demo_complex_task(session_id)
            self.demo_memory_usage(session_id)
            self.demo_writing_tool(session_id)
            self.demo_reasoning_tool(session_id)
            self.demo_adaptive_behavior(session_id)
            self.demo_system_status()
            
            print("\n" + "="*80)
            print("✅ DEMOSTRACIÓN COMPLETA FINALIZADA")
            print("="*80)
            
        except Exception as e:
            print(f"❌ Error en demostración: {str(e)}")
        
        finally:
            # Limpiar
            if self.orchestrator:
                self.orchestrator.shutdown()

def main():
    """Función principal para ejecutar la demostración"""
    demo = SchoolBotAgentDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()

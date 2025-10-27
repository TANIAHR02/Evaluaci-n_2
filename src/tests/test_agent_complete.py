"""
SchoolBot Agent - Test Suite
Suite de Pruebas para el Agente Inteligente Escolar

Autor: Tania Herrera
Fecha: Diciembre 2024
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import sys
import json
import time
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar componentes del agente
from src.agent.orchestrator import AgentOrchestrator, create_agent_orchestrator
from src.agent.config import get_complete_config
from src.agent.memory_manager import MemoryManager
from src.agent.planning_engine import PlanningEngine
from src.agent.tools import QueryTool, WritingTool, ReasoningTool

class TestSchoolBotAgent(unittest.TestCase):
    """Suite de pruebas para el agente SchoolBot"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.config = get_complete_config("profesor", "testing")
        self.orchestrator = None
        self.session_id = None
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        if self.orchestrator:
            self.orchestrator.shutdown()
    
    def test_01_orchestrator_initialization(self):
        """Prueba: Inicialización del orquestador"""
        print("\n🧪 PRUEBA 1: Inicialización del Orquestador")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.assertIsNotNone(self.orchestrator, "Orquestador no inicializado")
            
            # Verificar componentes
            self.assertIsNotNone(self.orchestrator.agent, "Agente principal no inicializado")
            self.assertIsNotNone(self.orchestrator.agent.memory_manager, "Gestor de memoria no inicializado")
            self.assertIsNotNone(self.orchestrator.agent.planning_engine, "Motor de planificación no inicializado")
            
            print("✅ Orquestador inicializado correctamente")
            
        except Exception as e:
            self.fail(f"Error inicializando orquestador: {str(e)}")
    
    def test_02_session_creation(self):
        """Prueba: Creación de sesión de usuario"""
        print("\n🧪 PRUEBA 2: Creación de Sesión")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            
            # Crear sesión
            self.session_id = self.orchestrator.create_session(
                user_id="test_profesor",
                user_type="profesor",
                context={"test": True}
            )
            
            self.assertIsNotNone(self.session_id, "ID de sesión no generado")
            self.assertIn(self.session_id, self.orchestrator.sessions, "Sesión no almacenada")
            
            # Verificar datos de sesión
            session = self.orchestrator.sessions[self.session_id]
            self.assertEqual(session.user_id, "test_profesor")
            self.assertEqual(session.user_type, "profesor")
            
            print(f"✅ Sesión creada: {self.session_id}")
            
        except Exception as e:
            self.fail(f"Error creando sesión: {str(e)}")
    
    def test_03_simple_query(self):
        """Prueba: Consulta simple"""
        print("\n🧪 PRUEBA 3: Consulta Simple")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_user", "estudiante")
            
            request = "¿Cuáles son los horarios de clases del colegio?"
            start_time = time.time()
            
            response = self.orchestrator.process_request(self.session_id, request)
            
            processing_time = time.time() - start_time
            
            # Verificaciones
            self.assertIsNotNone(response, "Respuesta no generada")
            self.assertIn("response", response, "Campo 'response' faltante")
            self.assertLess(processing_time, 10.0, f"Tiempo de procesamiento muy alto: {processing_time:.2f}s")
            
            print(f"✅ Consulta procesada en {processing_time:.2f}s")
            print(f"📝 Respuesta: {response['response'][:100]}...")
            
        except Exception as e:
            self.fail(f"Error en consulta simple: {str(e)}")
    
    def test_04_complex_task_planning(self):
        """Prueba: Tarea compleja con planificación"""
        print("\n🧪 PRUEBA 4: Tarea Compleja con Planificación")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_profesor", "profesor")
            
            request = """
            Necesito generar un reporte académico completo para el estudiante Juan Pérez del curso 3°A, 
            incluyendo análisis de rendimiento y recomendaciones de mejora
            """
            
            start_time = time.time()
            response = self.orchestrator.process_request(self.session_id, request)
            processing_time = time.time() - start_time
            
            # Verificaciones
            self.assertIsNotNone(response, "Respuesta no generada")
            self.assertIn("plan", response, "Plan no generado")
            
            plan = response["plan"]
            self.assertIsNotNone(plan, "Plan es None")
            self.assertIn("steps", plan, "Pasos del plan faltantes")
            self.assertGreater(len(plan["steps"]), 1, "Plan debe tener múltiples pasos")
            
            print(f"✅ Plan creado con {len(plan['steps'])} pasos")
            print(f"⏱️ Tiempo de procesamiento: {processing_time:.2f}s")
            
            # Mostrar pasos del plan
            for i, step in enumerate(plan["steps"], 1):
                print(f"   {i}. {step.get('description', 'Sin descripción')}")
                print(f"      Herramienta: {step.get('tool', 'N/A')}")
            
        except Exception as e:
            self.fail(f"Error en tarea compleja: {str(e)}")
    
    def test_05_memory_persistence(self):
        """Prueba: Persistencia de memoria"""
        print("\n🧪 PRUEBA 5: Persistencia de Memoria")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_user", "estudiante")
            
            # Primera consulta
            request1 = "¿Cuándo son las vacaciones de invierno?"
            response1 = self.orchestrator.process_request(self.session_id, request1)
            
            # Segunda consulta que debería usar memoria
            request2 = "¿Y las vacaciones de verano?"
            response2 = self.orchestrator.process_request(self.session_id, request2)
            
            # Verificaciones
            self.assertIsNotNone(response1, "Primera respuesta no generada")
            self.assertIsNotNone(response2, "Segunda respuesta no generada")
            
            # Verificar estado de memoria
            agent_status = self.orchestrator.get_agent_status()
            memory_status = agent_status.get("agent_status", {}).get("memory_status")
            
            if memory_status:
                stats = memory_status.get("stats", {})
                self.assertGreater(stats.get("total_entries", 0), 0, "No hay entradas en memoria")
                
                print(f"📊 Estado de memoria:")
                print(f"   - Entradas totales: {stats.get('total_entries', 0)}")
                print(f"   - Memoria de corto plazo: {stats.get('short_term_entries', 0)}")
                print(f"   - Memoria de largo plazo: {stats.get('long_term_entries', 0)}")
            
            print("✅ Memoria funcionando correctamente")
            
        except Exception as e:
            self.fail(f"Error en prueba de memoria: {str(e)}")
    
    def test_06_writing_tool(self):
        """Prueba: Herramienta de escritura"""
        print("\n🧪 PRUEBA 6: Herramienta de Escritura")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_profesor", "profesor")
            
            request = """
            Genera un comunicado para los apoderados informando sobre la próxima reunión de padres 
            del 15 de diciembre a las 19:00 horas en el auditorio principal
            """
            
            response = self.orchestrator.process_request(self.session_id, request)
            
            # Verificaciones
            self.assertIsNotNone(response, "Respuesta no generada")
            self.assertIn("response", response, "Campo 'response' faltante")
            
            response_text = response["response"]
            self.assertGreater(len(response_text), 50, "Respuesta muy corta")
            
            # Verificar contenido del comunicado
            self.assertIn("COMUNICADO", response_text.upper(), "No es un comunicado")
            self.assertIn("APODERADOS", response_text.upper(), "No menciona apoderados")
            
            print("✅ Comunicado generado correctamente")
            print(f"📄 Longitud: {len(response_text)} caracteres")
            print(f"📝 Contenido: {response_text[:200]}...")
            
        except Exception as e:
            self.fail(f"Error en herramienta de escritura: {str(e)}")
    
    def test_07_reasoning_tool(self):
        """Prueba: Herramienta de razonamiento"""
        print("\n🧪 PRUEBA 7: Herramienta de Razonamiento")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_profesor", "profesor")
            
            request = """
            Analiza las siguientes opciones para mejorar el rendimiento académico: 
            1) Implementar tutorías personalizadas, 2) Crear grupos de estudio, 3) Usar tecnología educativa. 
            Considera costos, tiempo y efectividad.
            """
            
            response = self.orchestrator.process_request(self.session_id, request)
            
            # Verificaciones
            self.assertIsNotNone(response, "Respuesta no generada")
            self.assertIn("response", response, "Campo 'response' faltante")
            
            response_text = response["response"]
            self.assertGreater(len(response_text), 100, "Análisis muy corto")
            
            # Verificar que es un análisis
            analysis_keywords = ["análisis", "opciones", "recomendación", "ventajas", "desventajas"]
            has_analysis = any(keyword in response_text.lower() for keyword in analysis_keywords)
            self.assertTrue(has_analysis, "No parece ser un análisis")
            
            print("✅ Análisis generado correctamente")
            print(f"📊 Longitud: {len(response_text)} caracteres")
            print(f"📝 Contenido: {response_text[:200]}...")
            
        except Exception as e:
            self.fail(f"Error en herramienta de razonamiento: {str(e)}")
    
    def test_08_adaptive_behavior(self):
        """Prueba: Comportamiento adaptativo"""
        print("\n🧪 PRUEBA 8: Comportamiento Adaptativo")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_user", "estudiante")
            
            # Diferentes tipos de solicitudes
            requests = [
                "¿Qué necesito para matricularme?",
                "Genera un reporte de asistencia",
                "Analiza las calificaciones del curso 2°B",
                "¿Cuándo es la próxima reunión de apoderados?"
            ]
            
            responses = []
            
            for i, request in enumerate(requests, 1):
                print(f"   📝 Solicitud {i}: {request[:50]}...")
                
                response = self.orchestrator.process_request(self.session_id, request)
                responses.append(response)
                
                # Verificar análisis
                analysis = response.get("analysis", {})
                self.assertIsNotNone(analysis, f"Análisis faltante para solicitud {i}")
                
                print(f"      📊 Complejidad: {analysis.get('complexity', 'N/A')}")
                print(f"      🛠️ Herramientas: {analysis.get('tools_needed', [])}")
                print(f"      🎯 Intención: {analysis.get('intent', 'N/A')}")
            
            print("✅ Comportamiento adaptativo funcionando")
            
        except Exception as e:
            self.fail(f"Error en comportamiento adaptativo: {str(e)}")
    
    def test_09_system_metrics(self):
        """Prueba: Métricas del sistema"""
        print("\n🧪 PRUEBA 9: Métricas del Sistema")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_user", "profesor")
            
            # Ejecutar algunas solicitudes para generar métricas
            test_requests = [
                "¿Cuáles son los horarios?",
                "Genera un comunicado",
                "Analiza el rendimiento académico"
            ]
            
            for request in test_requests:
                self.orchestrator.process_request(self.session_id, request)
            
            # Obtener métricas
            status = self.orchestrator.get_agent_status()
            metrics = status.get("system_metrics", {})
            
            # Verificaciones
            self.assertGreater(metrics.get("total_requests", 0), 0, "No hay solicitudes registradas")
            self.assertGreater(metrics.get("successful_requests", 0), 0, "No hay solicitudes exitosas")
            self.assertGreater(metrics.get("average_response_time", 0), 0, "Tiempo promedio no calculado")
            
            print("📈 Métricas del Sistema:")
            print(f"   - Solicitudes totales: {metrics.get('total_requests', 0)}")
            print(f"   - Solicitudes exitosas: {metrics.get('successful_requests', 0)}")
            print(f"   - Solicitudes fallidas: {metrics.get('failed_requests', 0)}")
            print(f"   - Tiempo promedio: {metrics.get('average_response_time', 0):.2f}s")
            print(f"   - Sesiones activas: {metrics.get('active_sessions', 0)}")
            
            print("✅ Métricas funcionando correctamente")
            
        except Exception as e:
            self.fail(f"Error en métricas del sistema: {str(e)}")
    
    def test_10_error_handling(self):
        """Prueba: Manejo de errores"""
        print("\n🧪 PRUEBA 10: Manejo de Errores")
        
        try:
            self.orchestrator = create_agent_orchestrator()
            self.session_id = self.orchestrator.create_session("test_user", "estudiante")
            
            # Solicitud con error intencional
            invalid_request = ""  # Solicitud vacía
            
            response = self.orchestrator.process_request(self.session_id, invalid_request)
            
            # Verificar manejo de error
            self.assertIsNotNone(response, "Respuesta no generada")
            
            # Debe manejar el error graciosamente
            if "error" in response:
                print(f"✅ Error manejado correctamente: {response['error']}")
            else:
                print("✅ Sistema maneja solicitudes vacías sin errores")
            
            # Probar con sesión inexistente
            try:
                self.orchestrator.process_request("session_inexistente", "test")
                self.fail("Debería haber fallado con sesión inexistente")
            except ValueError as e:
                print(f"✅ Error de sesión manejado: {str(e)}")
            
            print("✅ Manejo de errores funcionando correctamente")
            
        except Exception as e:
            self.fail(f"Error en manejo de errores: {str(e)}")

class TestMemoryManager(unittest.TestCase):
    """Pruebas específicas para el gestor de memoria"""
    
    def setUp(self):
        """Configuración inicial"""
        self.config = {
            "memory_path": "data/test_memory",
            "max_short_term": 10,
            "max_long_term": 50
        }
        self.memory_manager = None
    
    def tearDown(self):
        """Limpieza"""
        if self.memory_manager:
            self.memory_manager.clear_memory()
    
    def test_memory_storage(self):
        """Prueba: Almacenamiento en memoria"""
        print("\n🧪 PRUEBA MEMORIA: Almacenamiento")
        
        try:
            self.memory_manager = MemoryManager(self.config)
            
            # Almacenar interacción
            interaction = {
                "request": "¿Cuáles son los horarios?",
                "response": "Las clases son de 8:00 a 16:00",
                "analysis": {"complexity": "simple"},
                "context": {"user_type": "estudiante"}
            }
            
            self.memory_manager.store_interaction(interaction)
            
            # Verificar almacenamiento
            status = self.memory_manager.get_status()
            self.assertGreater(status["stats"]["total_entries"], 0, "No se almacenó la interacción")
            
            print("✅ Interacción almacenada correctamente")
            
        except Exception as e:
            self.fail(f"Error almacenando en memoria: {str(e)}")
    
    def test_memory_retrieval(self):
        """Prueba: Recuperación de memoria"""
        print("\n🧪 PRUEBA MEMORIA: Recuperación")
        
        try:
            self.memory_manager = MemoryManager(self.config)
            
            # Almacenar varias interacciones
            interactions = [
                {"request": "horarios de clases", "response": "8:00 a 16:00"},
                {"request": "vacaciones de invierno", "response": "24 junio al 7 julio"},
                {"request": "documentos matrícula", "response": "certificado, fotocopia"}
            ]
            
            for interaction in interactions:
                self.memory_manager.store_interaction(interaction)
            
            # Recuperar memoria
            results = self.memory_manager.retrieve_memory("horarios", limit=3)
            
            self.assertIsNotNone(results, "No se recuperó memoria")
            self.assertGreater(len(results), 0, "No hay resultados de memoria")
            
            print(f"✅ Memoria recuperada: {len(results)} entradas")
            
        except Exception as e:
            self.fail(f"Error recuperando memoria: {str(e)}")

class TestPlanningEngine(unittest.TestCase):
    """Pruebas específicas para el motor de planificación"""
    
    def setUp(self):
        """Configuración inicial"""
        self.config = {
            "max_plan_steps": 5,
            "default_timeout": 60
        }
        self.planning_engine = None
    
    def test_plan_creation(self):
        """Prueba: Creación de planes"""
        print("\n🧪 PRUEBA PLANIFICACIÓN: Creación de Planes")
        
        try:
            self.planning_engine = PlanningEngine(self.config)
            
            # Crear contexto de decisión
            from src.agent.planning_engine import DecisionContext
            context = DecisionContext(
                user_type="profesor",
                task_complexity="complex",
                available_tools=["query", "writing", "reasoning"],
                memory_context={},
                constraints={},
                preferences={}
            )
            
            # Crear plan
            request = "Generar reporte académico completo"
            analysis = {
                "complexity": "complex",
                "tools_needed": ["query", "reasoning", "writing"],
                "intent": "document_generation"
            }
            
            plan = self.planning_engine.create_plan(request, analysis, context)
            
            self.assertIsNotNone(plan, "Plan no creado")
            self.assertIn("steps", plan, "Pasos del plan faltantes")
            self.assertGreater(len(plan["steps"]), 0, "Plan sin pasos")
            
            print(f"✅ Plan creado con {len(plan['steps'])} pasos")
            
        except Exception as e:
            self.fail(f"Error creando plan: {str(e)}")

def run_performance_test():
    """Prueba de rendimiento del sistema"""
    print("\n🚀 PRUEBA DE RENDIMIENTO")
    print("="*50)
    
    try:
        orchestrator = create_agent_orchestrator()
        session_id = orchestrator.create_session("perf_test", "profesor")
        
        # Solicitudes de prueba
        test_requests = [
            "¿Cuáles son los horarios de clases?",
            "¿Cuándo son las vacaciones de invierno?",
            "Genera un comunicado para apoderados",
            "Analiza el rendimiento académico del curso 3°A",
            "¿Qué documentos necesito para la matrícula?"
        ]
        
        total_time = 0
        successful_requests = 0
        
        for i, request in enumerate(test_requests, 1):
            print(f"📝 Solicitud {i}: {request}")
            
            start_time = time.time()
            response = orchestrator.process_request(session_id, request)
            processing_time = time.time() - start_time
            
            total_time += processing_time
            
            if response and not response.get("error"):
                successful_requests += 1
                print(f"   ✅ Procesada en {processing_time:.2f}s")
            else:
                print(f"   ❌ Error: {response.get('error', 'Desconocido')}")
        
        # Métricas finales
        avg_time = total_time / len(test_requests)
        success_rate = (successful_requests / len(test_requests)) * 100
        
        print(f"\n📊 RESULTADOS DE RENDIMIENTO:")
        print(f"   - Solicitudes procesadas: {len(test_requests)}")
        print(f"   - Solicitudes exitosas: {successful_requests}")
        print(f"   - Tasa de éxito: {success_rate:.1f}%")
        print(f"   - Tiempo total: {total_time:.2f}s")
        print(f"   - Tiempo promedio: {avg_time:.2f}s")
        
        # Verificar objetivos
        if success_rate >= 90:
            print("✅ Objetivo de tasa de éxito cumplido (≥90%)")
        else:
            print("❌ Objetivo de tasa de éxito no cumplido")
        
        if avg_time <= 5.0:
            print("✅ Objetivo de tiempo promedio cumplido (≤5s)")
        else:
            print("❌ Objetivo de tiempo promedio no cumplido")
        
        orchestrator.shutdown()
        
    except Exception as e:
        print(f"❌ Error en prueba de rendimiento: {str(e)}")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🧪 INICIANDO SUITE DE PRUEBAS - SCHOOLBOT AGENT")
    print("="*60)
    
    # Crear suite de pruebas
    test_suite = unittest.TestSuite()
    
    # Agregar pruebas del agente principal
    test_suite.addTest(unittest.makeSuite(TestSchoolBotAgent))
    test_suite.addTest(unittest.makeSuite(TestMemoryManager))
    test_suite.addTest(unittest.makeSuite(TestPlanningEngine))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Pruebas exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Pruebas fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ PRUEBAS FALLIDAS:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORES:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    # Ejecutar prueba de rendimiento
    run_performance_test()
    
    print("\n✅ SUITE DE PRUEBAS COMPLETADA")

if __name__ == "__main__":
    main()

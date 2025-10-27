"""
SchoolBot Agent - Demo Interactivo
Demostración Interactiva del Agente Inteligente Escolar

Autor: Tania Herrera
Fecha: Diciembre 2024
Evaluación: EP2 - Ingeniería de Soluciones con IA
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar componentes del agente
from src.agent.orchestrator import create_agent_orchestrator
from src.agent.config import get_complete_config

class InteractiveDemo:
    """Demostración interactiva del agente SchoolBot"""
    
    def __init__(self):
        self.orchestrator = None
        self.session_id = None
        self.user_type = "estudiante"
        self.user_id = "demo_user"
        
    def initialize(self):
        """Inicializa el agente"""
        print("🤖 Inicializando SchoolBot Agent...")
        
        try:
            # Obtener configuración
            config = get_complete_config(self.user_type, "development")
            
            # Crear orquestador
            self.orchestrator = create_agent_orchestrator()
            
            # Crear sesión
            self.session_id = self.orchestrator.create_session(
                user_id=self.user_id,
                user_type=self.user_type
            )
            
            print("✅ SchoolBot Agent inicializado correctamente")
            print(f"👤 Usuario: {self.user_id} ({self.user_type})")
            print(f"🆔 Sesión: {self.session_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando agente: {str(e)}")
            return False
    
    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*60)
        print("🎓 SCHOOLBOT AGENT - DEMO INTERACTIVO")
        print("="*60)
        print("1. 🔍 Consulta Simple")
        print("2. 🧠 Tarea Compleja con Planificación")
        print("3. ✍️ Generar Documento")
        print("4. 🤔 Análisis y Razonamiento")
        print("5. 🧠 Demostrar Memoria")
        print("6. 📊 Ver Estado del Sistema")
        print("7. 🔄 Cambiar Tipo de Usuario")
        print("8. 🎯 Modo Automático")
        print("9. ❓ Ayuda")
        print("0. 🚪 Salir")
        print("="*60)
    
    def handle_simple_query(self):
        """Maneja consultas simples"""
        print("\n🔍 CONSULTA SIMPLE")
        print("-" * 30)
        
        examples = [
            "¿Cuáles son los horarios de clases del colegio?",
            "¿Cuándo son las vacaciones de invierno?",
            "¿Qué documentos necesito para la matrícula?",
            "¿Cuál es el reglamento de asistencia?",
            "¿Dónde está ubicado el colegio?"
        ]
        
        print("Ejemplos de consultas:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        print("\nO escribe tu propia consulta:")
        query = input("📝 Tu consulta: ").strip()
        
        if not query:
            print("❌ Consulta vacía")
            return
        
        self.process_request(query)
    
    def handle_complex_task(self):
        """Maneja tareas complejas"""
        print("\n🧠 TAREA COMPLEJA CON PLANIFICACIÓN")
        print("-" * 40)
        
        examples = [
            "Genera un reporte académico completo para el estudiante Juan Pérez del curso 3°A",
            "Analiza el rendimiento académico del curso 2°B y genera recomendaciones",
            "Crea un plan de mejoras para el área de matemáticas del colegio",
            "Genera un informe de asistencia mensual con análisis de tendencias"
        ]
        
        print("Ejemplos de tareas complejas:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        print("\nO describe tu tarea compleja:")
        task = input("📝 Tu tarea: ").strip()
        
        if not task:
            print("❌ Tarea vacía")
            return
        
        self.process_request(task)
    
    def handle_document_generation(self):
        """Maneja generación de documentos"""
        print("\n✍️ GENERAR DOCUMENTO")
        print("-" * 25)
        
        print("Tipos de documentos disponibles:")
        print("   1. Comunicado para apoderados")
        print("   2. Reporte académico")
        print("   3. Acta de reunión")
        print("   4. Circular informativa")
        
        doc_type = input("\n📝 Tipo de documento (1-4): ").strip()
        
        if doc_type == "1":
            self.generate_apoderados_communication()
        elif doc_type == "2":
            self.generate_academic_report()
        elif doc_type == "3":
            self.generate_meeting_minutes()
        elif doc_type == "4":
            self.generate_informative_circular()
        else:
            print("❌ Tipo de documento inválido")
    
    def generate_apoderados_communication(self):
        """Genera comunicado para apoderados"""
        print("\n📢 COMUNICADO PARA APODERADOS")
        
        fecha = input("📅 Fecha del evento: ").strip() or "15 de diciembre"
        horario = input("🕐 Horario: ").strip() or "19:00 horas"
        lugar = input("📍 Lugar: ").strip() or "Auditorio principal"
        contenido = input("📝 Contenido del comunicado: ").strip() or "Reunión de apoderados"
        
        request = f"""
        Genera un comunicado para los apoderados informando sobre {contenido} 
        el {fecha} a las {horario} en {lugar}
        """
        
        self.process_request(request)
    
    def generate_academic_report(self):
        """Genera reporte académico"""
        print("\n📊 REPORTE ACADÉMICO")
        
        estudiante = input("👤 Nombre del estudiante: ").strip() or "Juan Pérez"
        curso = input("🎓 Curso: ").strip() or "3°A"
        periodo = input("📅 Período: ").strip() or "Segundo semestre 2024"
        
        request = f"""
        Genera un reporte académico completo para el estudiante {estudiante} 
        del curso {curso} para el período {periodo}, incluyendo análisis de rendimiento 
        y recomendaciones de mejora
        """
        
        self.process_request(request)
    
    def generate_meeting_minutes(self):
        """Genera acta de reunión"""
        print("\n📋 ACTA DE REUNIÓN")
        
        tipo = input("📝 Tipo de reunión: ").strip() or "Consejo de profesores"
        fecha = input("📅 Fecha: ").strip() or "10 de diciembre"
        hora = input("🕐 Hora: ").strip() or "15:00"
        lugar = input("📍 Lugar: ").strip() or "Sala de profesores"
        
        request = f"""
        Genera un acta de reunión para {tipo} realizada el {fecha} a las {hora} 
        en {lugar}, incluyendo agenda, desarrollo y acuerdos
        """
        
        self.process_request(request)
    
    def generate_informative_circular(self):
        """Genera circular informativa"""
        print("\n📢 CIRCULAR INFORMATIVA")
        
        tema = input("📝 Tema de la circular: ").strip() or "Cambios en el calendario académico"
        destinatarios = input("👥 Destinatarios: ").strip() or "toda la comunidad educativa"
        
        request = f"""
        Genera una circular informativa sobre {tema} dirigida a {destinatarios}, 
        incluyendo información relevante y próximos pasos
        """
        
        self.process_request(request)
    
    def handle_reasoning(self):
        """Maneja análisis y razonamiento"""
        print("\n🤔 ANÁLISIS Y RAZONAMIENTO")
        print("-" * 30)
        
        examples = [
            "Analiza las opciones para mejorar el rendimiento académico del colegio",
            "Evalúa la implementación de tecnología educativa en las aulas",
            "Compara diferentes métodos de evaluación estudiantil",
            "Analiza las causas del ausentismo escolar y propone soluciones"
        ]
        
        print("Ejemplos de análisis:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        print("\nO describe tu análisis:")
        analysis = input("📝 Tu análisis: ").strip()
        
        if not analysis:
            print("❌ Análisis vacío")
            return
        
        self.process_request(analysis)
    
    def handle_memory_demo(self):
        """Demuestra el funcionamiento de la memoria"""
        print("\n🧠 DEMOSTRACIÓN DE MEMORIA")
        print("-" * 30)
        
        print("Esta demostración muestra cómo el agente usa la memoria:")
        print("1. Primera consulta: Busca información")
        print("2. Segunda consulta: Usa contexto de memoria")
        
        # Primera consulta
        print("\n📝 Primera consulta:")
        query1 = input("Consulta inicial: ").strip() or "¿Cuáles son los horarios de clases?"
        print(f"🔍 Procesando: {query1}")
        
        response1 = self.process_request(query1, show_details=True)
        
        # Segunda consulta relacionada
        print("\n📝 Segunda consulta (relacionada):")
        query2 = input("Consulta relacionada: ").strip() or "¿Y los horarios de recreo?"
        print(f"🔍 Procesando: {query2}")
        
        response2 = self.process_request(query2, show_details=True)
        
        # Mostrar estado de memoria
        self.show_memory_status()
    
    def show_memory_status(self):
        """Muestra el estado de la memoria"""
        try:
            status = self.orchestrator.get_agent_status()
            memory_status = status.get("agent_status", {}).get("memory_status")
            
            if memory_status:
                stats = memory_status.get("stats", {})
                print(f"\n📊 ESTADO DE MEMORIA:")
                print(f"   - Entradas totales: {stats.get('total_entries', 0)}")
                print(f"   - Memoria de corto plazo: {stats.get('short_term_entries', 0)}")
                print(f"   - Memoria de largo plazo: {stats.get('long_term_entries', 0)}")
                print(f"   - Memoria episódica: {stats.get('episodic_entries', 0)}")
                print(f"   - Memoria semántica: {stats.get('semantic_entries', 0)}")
                print(f"   - Tasa de aciertos: {stats.get('hit_rate', 0):.2f}")
        except Exception as e:
            print(f"❌ Error obteniendo estado de memoria: {str(e)}")
    
    def show_system_status(self):
        """Muestra el estado del sistema"""
        print("\n📊 ESTADO DEL SISTEMA")
        print("-" * 25)
        
        try:
            status = self.orchestrator.get_agent_status()
            
            # Estado del agente
            agent_status = status.get("agent_status", {})
            print(f"🤖 Estado del Agente:")
            print(f"   - Estado: {agent_status.get('state', 'N/A')}")
            print(f"   - Herramientas: {', '.join(agent_status.get('tools_available', []))}")
            
            # Métricas del sistema
            metrics = status.get("system_metrics", {})
            print(f"\n📈 Métricas del Sistema:")
            print(f"   - Sesiones totales: {metrics.get('total_sessions', 0)}")
            print(f"   - Sesiones activas: {metrics.get('active_sessions', 0)}")
            print(f"   - Solicitudes totales: {metrics.get('total_requests', 0)}")
            print(f"   - Solicitudes exitosas: {metrics.get('successful_requests', 0)}")
            print(f"   - Tiempo promedio: {metrics.get('average_response_time', 0):.2f}s")
            
            # Estado de memoria
            memory_status = agent_status.get("memory_status")
            if memory_status:
                stats = memory_status.get("stats", {})
                print(f"\n🧠 Estado de Memoria:")
                print(f"   - Entradas totales: {stats.get('total_entries', 0)}")
                print(f"   - Memoria de corto plazo: {stats.get('short_term_entries', 0)}")
                print(f"   - Memoria de largo plazo: {stats.get('long_term_entries', 0)}")
                print(f"   - Tasa de aciertos: {stats.get('hit_rate', 0):.2f}")
            
            # Estado de planificación
            planning_status = agent_status.get("planning_status")
            if planning_status:
                print(f"\n🎯 Estado de Planificación:")
                print(f"   - Planes totales: {planning_status.get('total_plans', 0)}")
                print(f"   - Planes activos: {planning_status.get('active_plans', 0)}")
                print(f"   - Planes completados: {planning_status.get('completed_plans', 0)}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estado: {str(e)}")
    
    def change_user_type(self):
        """Cambia el tipo de usuario"""
        print("\n🔄 CAMBIAR TIPO DE USUARIO")
        print("-" * 30)
        
        print("Tipos de usuario disponibles:")
        print("   1. Estudiante")
        print("   2. Apoderado")
        print("   3. Profesor")
        print("   4. Administrador")
        
        choice = input("\n📝 Selecciona tipo de usuario (1-4): ").strip()
        
        user_types = {
            "1": "estudiante",
            "2": "apoderado", 
            "3": "profesor",
            "4": "admin"
        }
        
        if choice in user_types:
            self.user_type = user_types[choice]
            self.user_id = f"demo_{self.user_type}"
            
            # Recrear sesión con nuevo tipo de usuario
            if self.orchestrator:
                self.session_id = self.orchestrator.create_session(
                    user_id=self.user_id,
                    user_type=self.user_type
                )
            
            print(f"✅ Tipo de usuario cambiado a: {self.user_type}")
            print(f"🆔 Nueva sesión: {self.session_id}")
        else:
            print("❌ Opción inválida")
    
    def automatic_mode(self):
        """Modo automático con demostraciones predefinidas"""
        print("\n🎯 MODO AUTOMÁTICO")
        print("-" * 20)
        
        demos = [
            {
                "name": "Consulta Simple",
                "request": "¿Cuáles son los horarios de clases del colegio?",
                "description": "Demuestra búsqueda básica de información"
            },
            {
                "name": "Tarea Compleja",
                "request": "Genera un reporte académico completo para el estudiante María González del curso 2°B",
                "description": "Demuestra planificación automática y uso de múltiples herramientas"
            },
            {
                "name": "Generación de Documento",
                "request": "Crea un comunicado para apoderados sobre la próxima reunión del 20 de diciembre",
                "description": "Demuestra herramienta de escritura con plantillas"
            },
            {
                "name": "Análisis y Razonamiento",
                "request": "Analiza las opciones para mejorar el rendimiento académico: tutorías, grupos de estudio, tecnología educativa",
                "description": "Demuestra herramienta de razonamiento y análisis"
            },
            {
                "name": "Memoria Persistente",
                "request": "¿Cuándo son las vacaciones de verano?",
                "description": "Demuestra uso de memoria para contexto"
            }
        ]
        
        print("Demostraciones disponibles:")
        for i, demo in enumerate(demos, 1):
            print(f"   {i}. {demo['name']}: {demo['description']}")
        
        print("   0. Ejecutar todas las demostraciones")
        
        choice = input("\n📝 Selecciona demostración (0-5): ").strip()
        
        if choice == "0":
            # Ejecutar todas las demostraciones
            for i, demo in enumerate(demos, 1):
                print(f"\n🎬 DEMOSTRACIÓN {i}: {demo['name']}")
                print(f"📝 Descripción: {demo['description']}")
                print(f"🔍 Solicitud: {demo['request']}")
                print("-" * 50)
                
                self.process_request(demo['request'], show_details=True)
                
                if i < len(demos):
                    input("\n⏸️ Presiona Enter para continuar...")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            # Ejecutar demostración específica
            demo = demos[int(choice) - 1]
            print(f"\n🎬 DEMOSTRACIÓN: {demo['name']}")
            print(f"📝 Descripción: {demo['description']}")
            print(f"🔍 Solicitud: {demo['request']}")
            print("-" * 50)
            
            self.process_request(demo['request'], show_details=True)
        
        else:
            print("❌ Opción inválida")
    
    def show_help(self):
        """Muestra la ayuda"""
        print("\n❓ AYUDA - SCHOOLBOT AGENT")
        print("-" * 30)
        
        print("""
🤖 SCHOOLBOT AGENT es un agente inteligente desarrollado para el Colegio San Ignacio Digital.

🎯 CAPACIDADES:
   • Consulta de información escolar
   • Generación de documentos
   • Análisis y razonamiento
   • Planificación de tareas complejas
   • Memoria persistente

🛠️ HERRAMIENTAS:
   • Query Tool: Búsqueda en documentos escolares
   • Writing Tool: Generación de documentos
   • Reasoning Tool: Análisis y decisiones

🧠 MEMORIA:
   • Corto plazo: Conversaciones recientes
   • Largo plazo: Información importante
   • Episódica: Eventos específicos
   • Semántica: Conocimiento general

👥 TIPOS DE USUARIO:
   • Estudiante: Acceso básico
   • Apoderado: Acceso ampliado
   • Profesor: Acceso completo
   • Admin: Acceso máximo

💡 CONSEJOS:
   • Sé específico en tus consultas
   • Usa el modo automático para ver ejemplos
   • Cambia el tipo de usuario según tus necesidades
   • Revisa el estado del sistema para métricas
        """)
    
    def process_request(self, request: str, show_details: bool = False):
        """Procesa una solicitud del usuario"""
        if not request.strip():
            print("❌ Solicitud vacía")
            return None
        
        try:
            print(f"\n⏳ Procesando solicitud...")
            start_time = time.time()
            
            response = self.orchestrator.process_request(self.session_id, request)
            
            processing_time = time.time() - start_time
            
            if response.get("error"):
                print(f"❌ Error: {response['error']}")
                return None
            
            # Mostrar respuesta
            print(f"\n✅ RESPUESTA:")
            print("-" * 20)
            print(response.get("response", "Sin respuesta"))
            
            if show_details:
                # Mostrar detalles adicionales
                analysis = response.get("analysis", {})
                if analysis:
                    print(f"\n📊 ANÁLISIS:")
                    print(f"   - Complejidad: {analysis.get('complexity', 'N/A')}")
                    print(f"   - Intención: {analysis.get('intent', 'N/A')}")
                    print(f"   - Herramientas: {', '.join(analysis.get('tools_needed', []))}")
                
                plan = response.get("plan")
                if plan:
                    print(f"\n📋 PLAN GENERADO:")
                    print(f"   - Nombre: {plan.get('name', 'Sin nombre')}")
                    print(f"   - Pasos: {len(plan.get('steps', []))}")
                    
                    for i, step in enumerate(plan.get("steps", []), 1):
                        print(f"      {i}. {step.get('description', 'Sin descripción')}")
                        print(f"         Herramienta: {step.get('tool', 'N/A')}")
                        print(f"         Duración: {step.get('estimated_duration', 0)}s")
            
            print(f"\n⏱️ Tiempo de procesamiento: {processing_time:.2f}s")
            
            return response
            
        except Exception as e:
            print(f"❌ Error procesando solicitud: {str(e)}")
            return None
    
    def run(self):
        """Ejecuta la demostración interactiva"""
        print("🎓 BIENVENIDO A SCHOOLBOT AGENT")
        print("Demostración Interactiva - EP2")
        
        # Inicializar agente
        if not self.initialize():
            return
        
        # Bucle principal
        while True:
            try:
                self.show_menu()
                choice = input("\n📝 Selecciona una opción (0-9): ").strip()
                
                if choice == "0":
                    print("\n👋 ¡Gracias por usar SchoolBot Agent!")
                    break
                elif choice == "1":
                    self.handle_simple_query()
                elif choice == "2":
                    self.handle_complex_task()
                elif choice == "3":
                    self.handle_document_generation()
                elif choice == "4":
                    self.handle_reasoning()
                elif choice == "5":
                    self.handle_memory_demo()
                elif choice == "6":
                    self.show_system_status()
                elif choice == "7":
                    self.change_user_type()
                elif choice == "8":
                    self.automatic_mode()
                elif choice == "9":
                    self.show_help()
                else:
                    print("❌ Opción inválida")
                
                input("\n⏸️ Presiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                input("⏸️ Presiona Enter para continuar...")
        
        # Limpiar recursos
        if self.orchestrator:
            self.orchestrator.shutdown()

def main():
    """Función principal"""
    demo = InteractiveDemo()
    demo.run()

if __name__ == "__main__":
    main()

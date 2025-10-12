@echo off
echo ========================================
echo DEMOSTRACION DE PROMPTS - SCHOOLBOT
echo ========================================
echo.

echo Los 5 prompts principales del sistema SchoolBot han sido creados:
echo.

echo 1. PROMPT 1: SYSTEM PROMPT (BASE)
echo ----------------------------------------
echo Rol: Asistente institucional
echo Parametros: temperature=0.1, max_tokens=400
echo Funcion: Define la identidad y comportamiento base de SchoolBot
echo Archivo: src/prompts/main_prompts.py - prompt_1_system_base()
echo.

echo 2. PROMPT 2: SINTESIS RAG
echo ----------------------------------------
echo Rol: Agente de respuesta
echo Parametros: temperature=0.3, max_tokens=200
echo Funcion: Sintetiza informacion de documentos recuperados
echo Archivo: src/prompts/main_prompts.py - prompt_2_rag_synthesis()
echo.

echo 3. PROMPT 3: CLARIFICACION
echo ----------------------------------------
echo Rol: Agente de interpretacion
echo Parametros: temperature=0.2, max_tokens=150
echo Funcion: Solicita aclaraciones para preguntas ambiguas
echo Archivo: src/prompts/main_prompts.py - prompt_3_clarification()
echo.

echo 4. PROMPT 4: COMPROBACION DE COHERENCIA
echo ----------------------------------------
echo Rol: Validador de respuesta
echo Parametros: temperature=0.0, max_tokens=300
echo Funcion: Valida coherencia entre respuesta y fuentes
echo Archivo: src/prompts/main_prompts.py - prompt_4_coherence_check()
echo.

echo 5. PROMPT 5: AGENTE DE APRENDIZAJE
echo ----------------------------------------
echo Rol: Agente de mejora continua
echo Parametros: temperature=0.4, max_tokens=500
echo Funcion: Analiza consultas anteriores y propone mejoras
echo Archivo: src/prompts/main_prompts.py - prompt_5_learning_agent()
echo.

echo ========================================
echo ESTRUCTURA DE ARCHIVOS CREADOS
echo ========================================
echo.
echo src/prompts/
echo ├── main_prompts.py          # Los 5 prompts principales
echo ├── system_prompts.py        # Prompts completos del sistema
echo ├── prompt_examples.py       # Ejemplos de uso
echo ├── prompt_config.py         # Configuracion y parametros
echo └── README.md               # Documentacion completa
echo.

echo ========================================
echo CARACTERISTICAS PRINCIPALES
echo ========================================
echo.
echo ✅ Optimizados para el contexto educativo chileno
echo ✅ Especificos para el Colegio San Ignacio Digital
echo ✅ Diferentes tonos segun tipo de usuario
echo ✅ Manejo de errores y clarificaciones
echo ✅ Validacion de coherencia con fuentes
echo ✅ Sistema de aprendizaje continuo
echo ✅ Configuracion flexible por parametros
echo.

echo ========================================
echo EJEMPLO DE USO
echo ========================================
echo.
echo Para usar los prompts en Python:
echo.
echo from src.prompts.main_prompts import MainPrompts
echo.
echo # Prompt 1: System base
echo system_prompt = MainPrompts.prompt_1_system_base()
echo.
echo # Prompt 2: RAG con documentos
echo docs = [{"text": "Las clases son de 8:00 a 16:00", "metadata": {"file_name": "reglamento.txt"}}]
echo rag_prompt = MainPrompts.prompt_2_rag_synthesis(docs, "¿Cuáles son los horarios?")
echo.
echo # Prompt 3: Clarificación
echo clarification = MainPrompts.prompt_3_clarification("¿Qué necesito?")
echo.
echo # Prompt 4: Validación
echo validation = MainPrompts.prompt_4_coherence_check("Las clases son de 8:00 a 16:00", docs)
echo.
echo # Prompt 5: Aprendizaje
echo learning = MainPrompts.prompt_5_learning_agent(previous_queries)
echo.

echo ========================================
echo PROMPTS LISTOS PARA IMPLEMENTACION
echo ========================================
echo.
echo Los prompts estan completamente implementados y listos para ser
echo utilizados en el sistema SchoolBot. Cada prompt esta optimizado
echo para su funcion especifica y el contexto educativo del colegio.
echo.

pause


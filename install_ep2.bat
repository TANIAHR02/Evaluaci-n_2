@echo off
REM SchoolBot Agent - Script de Instalación y Configuración
REM EP2 - Ingeniería de Soluciones con IA
REM Autor: Tania Herrera

echo ========================================
echo   SCHOOLBOT AGENT - INSTALACION EP2
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

echo ✅ Python detectado
python --version

REM Crear directorios necesarios
echo.
echo 📁 Creando directorios...
if not exist "data" mkdir data
if not exist "data\memory" mkdir data\memory
if not exist "data\vector_db" mkdir data\vector_db
if not exist "data\templates" mkdir data\templates
if not exist "data\docs" mkdir data\docs
if not exist "logs" mkdir logs
if not exist "src\agent" mkdir src\agent

echo ✅ Directorios creados

REM Instalar dependencias
echo.
echo 📦 Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas

REM Configurar variables de entorno
echo.
echo ⚙️ Configurando variables de entorno...
if not exist ".env" (
    copy "env.ep2.example" ".env"
    echo ✅ Archivo .env creado
    echo ⚠️  IMPORTANTE: Edita .env con tu OpenAI API Key
) else (
    echo ✅ Archivo .env ya existe
)

REM Verificar configuración
echo.
echo 🔍 Verificando configuración...
if not exist ".env" (
    echo ERROR: Archivo .env no encontrado
    pause
    exit /b 1
)

echo ✅ Configuración verificada

REM Mostrar instrucciones
echo.
echo ========================================
echo   INSTALACION COMPLETADA
echo ========================================
echo.
echo 📋 SIGUIENTES PASOS:
echo.
echo 1. Edita el archivo .env con tu OpenAI API Key:
echo    OPENAI_API_KEY=tu_api_key_aqui
echo.
echo 2. Ejecuta la demostración:
echo    python demo_interactivo.py
echo.
echo 3. O ejecuta las pruebas:
echo    python src/tests/test_agent_complete.py
echo.
echo 4. Para desarrollo, ejecuta:
echo    python src/agent/demo.py
echo.
echo 📚 DOCUMENTACION:
echo    - README_EP2.md: Documentación principal
echo    - report/informe_tecnico_ep2.md: Informe técnico
echo    - report/diagrama_arquitectura_ep2.puml: Diagrama de arquitectura
echo.
echo 🎓 AUTORA: Tania Herrera Rodriguez
echo 📅 FECHA: Diciembre 2024
echo 🏫 INSTITUCION: Duoc UC
echo.
echo ¡Listo para usar SchoolBot Agent!
echo ========================================

pause

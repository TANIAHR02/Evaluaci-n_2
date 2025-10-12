@echo off
echo ========================================
echo SchoolBot - Asistente Inteligente Escolar
echo ========================================
echo.

echo Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Ejecuta primero: install_dependencies.bat
    pause
    exit /b 1
)

echo.
echo Verificando instalacion de dependencias...
python -c "import fastapi, sentence_transformers, chromadb" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Faltan dependencias. Ejecuta: install_dependencies.bat
    pause
    exit /b 1
)

echo.
echo Creando directorios necesarios...
if not exist "data\vector_db" mkdir "data\vector_db"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\temp" mkdir "data\temp"
if not exist "logs" mkdir "logs"

echo.
echo Iniciando SchoolBot...
echo.
echo El servidor estara disponible en: http://localhost:8000
echo La documentacion de la API estara en: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m src.api.app



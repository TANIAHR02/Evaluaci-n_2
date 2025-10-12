@echo off
echo ========================================
echo SchoolBot - Procesamiento de Documentos
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
echo Verificando documentos en data/docs...
if not exist "data\docs\*.txt" (
    echo ADVERTENCIA: No se encontraron documentos en data/docs
    echo Asegurate de tener archivos .txt en el directorio data/docs
)

echo.
echo Procesando documentos...
python -m src.ingest.ingest_data
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron procesar los documentos
    pause
    exit /b 1
)

echo.
echo Generando embeddings...
python -m src.embeddings.generate_embeddings
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron generar los embeddings
    pause
    exit /b 1
)

echo.
echo ========================================
echo Procesamiento completado exitosamente!
echo ========================================
echo.
echo Los documentos han sido procesados y los embeddings generados.
echo Ahora puedes ejecutar: run_schoolbot.bat
echo.
pause



@echo off
echo ========================================
echo SchoolBot - Instalacion de Dependencias
echo ========================================
echo.

echo Verificando instalacion de Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

echo.
echo Python encontrado! Continuando con la instalacion...
echo.

echo Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo.
echo Actualizando pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ERROR: No se pudo actualizar pip
    pause
    exit /b 1
)

echo.
echo Instalando dependencias principales...
pip install fastapi uvicorn python-multipart
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias principales
    pause
    exit /b 1
)

echo.
echo Instalando dependencias de procesamiento de documentos...
pip install PyPDF2 python-docx openpyxl pandas numpy
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias de documentos
    pause
    exit /b 1
)

echo.
echo Instalando dependencias de IA...
pip install sentence-transformers torch
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias de IA
    pause
    exit /b 1
)

echo.
echo Instalando dependencias de base de datos...
pip install chromadb sqlalchemy redis
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias de base de datos
    pause
    exit /b 1
)

echo.
echo Instalando dependencias de testing...
pip install pytest pytest-asyncio httpx
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias de testing
    pause
    exit /b 1
)

echo.
echo Instalando dependencias adicionales...
pip install python-dotenv nltk scikit-learn prometheus-client
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias adicionales
    pause
    exit /b 1
)

echo.
echo Descargando recursos de NLTK...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudieron descargar los recursos de NLTK
    echo Esto no es critico, se pueden descargar mas tarde
)

echo.
echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo Para activar el entorno virtual en el futuro, ejecuta:
echo   venv\Scripts\activate.bat
echo.
echo Para ejecutar el proyecto:
echo   1. Activa el entorno virtual: venv\Scripts\activate.bat
echo   2. Ejecuta: python -m src.api.app
echo.
pause



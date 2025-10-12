# Script para instalar Python y configurar SchoolBot
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SchoolBot - Configuracion de Python" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python ya está instalado
Write-Host "Verificando instalacion de Python..." -ForegroundColor Yellow
$pythonCmd = $null

# Buscar Python en ubicaciones comunes
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Python39\python.exe",
    "C:\Python38\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python312\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python311\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python310\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python39\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python38\python.exe"
)

foreach ($path in $pythonPaths) {
    try {
        $result = & $path --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $path
            Write-Host "Python encontrado en: $path" -ForegroundColor Green
            Write-Host "Version: $result" -ForegroundColor Green
            break
        }
    }
    catch {
        # Continuar buscando
    }
}

if (-not $pythonCmd) {
    Write-Host "Python no encontrado. Intentando instalar..." -ForegroundColor Yellow
    
    # Intentar instalar con winget
    try {
        Write-Host "Intentando instalar Python con winget..." -ForegroundColor Yellow
        winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python instalado exitosamente con winget!" -ForegroundColor Green
            $pythonCmd = "python"
        }
    }
    catch {
        Write-Host "winget no disponible. Intentando con Chocolatey..." -ForegroundColor Yellow
        try {
            choco install python -y
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Python instalado exitosamente con Chocolatey!" -ForegroundColor Green
                $pythonCmd = "python"
            }
        }
        catch {
            Write-Host "Chocolatey no disponible." -ForegroundColor Red
        }
    }
    
    # Si aún no se encuentra, mostrar instrucciones
    if (-not $pythonCmd) {
        Write-Host "No se pudo instalar Python automaticamente." -ForegroundColor Red
        Write-Host "Por favor instala Python manualmente:" -ForegroundColor Yellow
        Write-Host "1. Ve a https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Descarga Python 3.8 o superior" -ForegroundColor White
        Write-Host "3. Ejecuta el instalador" -ForegroundColor White
        Write-Host "4. IMPORTANTE: Marca 'Add Python to PATH'" -ForegroundColor White
        Write-Host "5. Reinicia la terminal y ejecuta este script nuevamente" -ForegroundColor White
        Read-Host "Presiona Enter para continuar"
        exit 1
    }
}

# Verificar que Python funciona
Write-Host "Verificando que Python funciona correctamente..." -ForegroundColor Yellow
try {
    $version = & $pythonCmd --version
    Write-Host "Python funcionando: $version" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python no funciona correctamente" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual
Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
& $pythonCmd -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: No se pudo crear el entorno virtual" -ForegroundColor Red
    exit 1
}

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Actualizar pip
Write-Host "Actualizando pip..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip

# Instalar dependencias básicas
Write-Host "Instalando dependencias basicas..." -ForegroundColor Yellow
$packages = @(
    "fastapi",
    "uvicorn",
    "python-multipart",
    "PyPDF2",
    "python-docx",
    "openpyxl",
    "pandas",
    "numpy",
    "sentence-transformers",
    "torch",
    "chromadb",
    "sqlalchemy",
    "redis",
    "pytest",
    "python-dotenv",
    "nltk",
    "scikit-learn",
    "prometheus-client"
)

foreach ($package in $packages) {
    Write-Host "Instalando $package..." -ForegroundColor Cyan
    & $pythonCmd -m pip install $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Advertencia: No se pudo instalar $package" -ForegroundColor Yellow
    }
}

# Descargar recursos de NLTK
Write-Host "Descargando recursos de NLTK..." -ForegroundColor Yellow
& $pythonCmd -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Configuracion completada exitosamente!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para ejecutar SchoolBot:" -ForegroundColor White
Write-Host "1. Ejecuta: .\run_schoolbot.bat" -ForegroundColor White
Write-Host "2. O ejecuta: .\process_documents.bat primero" -ForegroundColor White
Write-Host ""
Read-Host "Presiona Enter para continuar"



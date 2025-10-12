"""
SchoolBot - Asistente Inteligente Escolar
API REST Principal

Autor: [Nombre del Estudiante]
Fecha: [Fecha Actual]
Evaluación: EP1 - Ingeniería de Soluciones con Inteligencia Artificial
Institución: Universidad [Nombre]

Descripción:
Este módulo implementa la API REST principal del SchoolBot utilizando FastAPI.
Proporciona endpoints para consultas, autenticación, gestión de documentos
y monitoreo del sistema.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid

# Dependencias de FastAPI
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Dependencias para autenticación
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

# Dependencias para validación
from pydantic import BaseModel, Field, validator
from email_validator import validate_email, EmailNotValidError

# Dependencias para rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Dependencias para monitoreo
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Importar módulos del sistema
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retriever.retriever import SemanticRetriever
from embeddings.generate_embeddings import EmbeddingPipeline

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
app = FastAPI(
    title="SchoolBot API",
    description="API REST para el Asistente Inteligente Escolar",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de hosts confiables
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En producción, especificar hosts específicos
)

# Configuración de rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuración de autenticación
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Métricas de Prometheus
REQUEST_COUNT = Counter('schoolbot_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('schoolbot_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
QUERY_COUNT = Counter('schoolbot_queries_total', 'Total queries', ['user_type', 'status'])

# Inicializar componentes del sistema
retriever = None
embedding_pipeline = None

# Modelos Pydantic
class QueryRequest(BaseModel):
    """Modelo para solicitudes de consulta"""
    question: str = Field(..., min_length=1, max_length=1000, description="Pregunta del usuario")
    user_type: str = Field(..., description="Tipo de usuario")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    
    @validator('user_type')
    def validate_user_type(cls, v):
        allowed_types = ['estudiante', 'apoderado', 'profesor', 'admin']
        if v not in allowed_types:
            raise ValueError(f'user_type debe ser uno de: {allowed_types}')
        return v

class QueryResponse(BaseModel):
    """Modelo para respuestas de consulta"""
    answer: str = Field(..., description="Respuesta generada")
    sources: List[Dict[str, Any]] = Field(..., description="Fuentes utilizadas")
    confidence: float = Field(..., ge=0, le=1, description="Nivel de confianza")
    query_id: str = Field(..., description="ID único de la consulta")
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos")

class UserLogin(BaseModel):
    """Modelo para login de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class UserRegister(BaseModel):
    """Modelo para registro de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, max_length=100)
    user_type: str = Field(..., description="Tipo de usuario")
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @validator('email')
    def validate_email(cls, v):
        try:
            validate_email(v)
            return v
        except EmailNotValidError:
            raise ValueError('Email inválido')
    
    @validator('user_type')
    def validate_user_type(cls, v):
        allowed_types = ['estudiante', 'apoderado', 'profesor', 'admin']
        if v not in allowed_types:
            raise ValueError(f'user_type debe ser uno de: {allowed_types}')
        return v

class DocumentUpload(BaseModel):
    """Modelo para subida de documentos"""
    document_type: str = Field(..., description="Tipo de documento")
    description: Optional[str] = Field(None, description="Descripción del documento")
    
    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ['reglamento_escolar', 'calendario_academico', 'circular_apoderados', 
                        'menu_almuerzos', 'manual_procedimientos', 'documento_general']
        if v not in allowed_types:
            raise ValueError(f'document_type debe ser uno de: {allowed_types}')
        return v

class SystemStatus(BaseModel):
    """Modelo para estado del sistema"""
    status: str = Field(..., description="Estado del sistema")
    version: str = Field(..., description="Versión de la API")
    uptime: float = Field(..., description="Tiempo de funcionamiento en segundos")
    components: Dict[str, str] = Field(..., description="Estado de componentes")

# Base de datos en memoria (en producción usar una base de datos real)
users_db = {}
sessions_db = {}

# Funciones de autenticación
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return users_db[username]
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware para recopilar métricas de Prometheus"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Eventos de la aplicación
@app.on_event("startup")
async def startup_event():
    """Inicializa componentes del sistema al arrancar"""
    global retriever, embedding_pipeline
    
    try:
        # Inicializar retriever semántico
        retriever = SemanticRetriever()
        retriever.initialize_models()
        retriever.initialize_vector_db()
        
        # Inicializar pipeline de embeddings
        embedding_pipeline = EmbeddingPipeline()
        
        logger.info("Sistema SchoolBot inicializado correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando sistema: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación"""
    logger.info("Cerrando sistema SchoolBot")

# Endpoints principales
@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raíz con información básica"""
    return {
        "message": "SchoolBot API - Asistente Inteligente Escolar",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """Endpoint de verificación de salud del sistema"""
    try:
        # Verificar componentes
        components = {
            "retriever": "healthy" if retriever else "unhealthy",
            "embedding_pipeline": "healthy" if embedding_pipeline else "unhealthy",
            "database": "healthy"  # Simplificado para el ejemplo
        }
        
        return SystemStatus(
            status="healthy" if all(c == "healthy" for c in components.values()) else "degraded",
            version="1.0.0",
            uptime=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
            components=components
        )
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/v1/query", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query_endpoint(request: QueryRequest, current_user: dict = Depends(verify_token)):
    """
    Endpoint principal para realizar consultas al SchoolBot.
    
    Este endpoint procesa consultas en lenguaje natural y retorna
    respuestas basadas en los documentos del colegio.
    """
    start_time = time.time()
    query_id = str(uuid.uuid4())
    
    try:
        # Realizar búsqueda semántica
        search_results = retriever.search(
            query=request.question,
            user_type=request.user_type,
            top_k=5,
            use_reranking=True
        )
        
        # Generar respuesta (simplificado - en producción usar LLM)
        if search_results:
            answer = f"Basándome en la información disponible, {search_results[0]['text'][:200]}..."
            confidence = search_results[0].get('similarity_score', 0.8)
        else:
            answer = "No encontré información específica sobre tu consulta. Te recomiendo contactar directamente con la secretaría del colegio."
            confidence = 0.0
        
        processing_time = time.time() - start_time
        
        # Registrar métricas
        QUERY_COUNT.labels(
            user_type=request.user_type,
            status="success"
        ).inc()
        
        return QueryResponse(
            answer=answer,
            sources=search_results,
            confidence=confidence,
            query_id=query_id,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        
        # Registrar métricas de error
        QUERY_COUNT.labels(
            user_type=request.user_type,
            status="error"
        ).inc()
        
        raise HTTPException(status_code=500, detail="Error procesando consulta")

@app.post("/api/v1/auth/register")
async def register_user(user_data: UserRegister):
    """
    Registra un nuevo usuario en el sistema.
    """
    try:
        # Verificar si el usuario ya existe
        if user_data.username in users_db:
            raise HTTPException(status_code=400, detail="Usuario ya existe")
        
        # Crear usuario
        hashed_password = get_password_hash(user_data.password)
        user = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "user_type": user_data.user_type,
            "full_name": user_data.full_name,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        users_db[user_data.username] = user
        
        logger.info(f"Usuario registrado: {user_data.username}")
        
        return {"message": "Usuario registrado exitosamente", "username": user_data.username}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/v1/auth/login")
async def login_user(user_credentials: UserLogin):
    """
    Autentica un usuario y retorna un token de acceso.
    """
    try:
        # Verificar usuario
        if user_credentials.username not in users_db:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        user = users_db[user_credentials.username]
        
        # Verificar contraseña
        if not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Verificar si el usuario está activo
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_credentials.username, "user_type": user["user_type"]},
            expires_delta=access_token_expires
        )
        
        # Registrar sesión
        session_id = str(uuid.uuid4())
        sessions_db[session_id] = {
            "username": user_credentials.username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + access_token_expires).isoformat()
        }
        
        logger.info(f"Usuario autenticado: {user_credentials.username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "session_id": session_id,
            "user_type": user["user_type"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/v1/documents/upload")
@limiter.limit("5/minute")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Sube un nuevo documento al sistema.
    """
    try:
        # Verificar permisos (solo admin puede subir documentos)
        if current_user["user_type"] != "admin":
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        # Verificar tipo de archivo
        allowed_extensions = ['.pdf', '.docx', '.xlsx']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no soportado. Permitidos: {allowed_extensions}"
            )
        
        # Guardar archivo temporalmente
        temp_path = f"data/temp/{file.filename}"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Procesar documento (simplificado)
        # En producción, usar el pipeline completo de ingesta
        
        logger.info(f"Documento subido: {file.filename}")
        
        return {
            "message": "Documento subido exitosamente",
            "filename": file.filename,
            "document_type": document_type,
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo documento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/v1/analytics/usage")
async def get_usage_analytics(current_user: dict = Depends(verify_token)):
    """
    Obtiene estadísticas de uso del sistema.
    """
    try:
        # Verificar permisos (solo admin)
        if current_user["user_type"] != "admin":
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        # Obtener analytics del retriever
        search_analytics = retriever.get_search_analytics()
        
        # Obtener métricas de Prometheus
        metrics = generate_latest()
        
        return {
            "search_analytics": search_analytics,
            "system_metrics": metrics.decode('utf-8'),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/v1/suggestions")
async def get_search_suggestions(
    q: str,
    current_user: dict = Depends(verify_token)
):
    """
    Obtiene sugerencias de búsqueda basadas en consulta parcial.
    """
    try:
        suggestions = retriever.get_search_suggestions(q)
        
        return {
            "suggestions": suggestions,
            "query": q
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/metrics")
async def metrics():
    """
    Endpoint para métricas de Prometheus.
    """
    return generate_latest()

# Manejo de errores personalizado
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint no encontrado"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

# Función principal para ejecutar la aplicación
def main():
    """
    Función principal para ejecutar el servidor FastAPI.
    """
    # Configurar tiempo de inicio
    app.state.start_time = time.time()
    
    # Ejecutar servidor
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()



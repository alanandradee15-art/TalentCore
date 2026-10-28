
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import inicializar_base_datos
from .empleados import router as empleados_router
from .vacaciones import router as vacaciones_router


# ==========================================
# INICIALIZAR BASE DE DATOS AL ARRANCAR
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_base_datos()
    yield


# ==========================================
# SISTEMA TALENTCORE
# ==========================================

app = FastAPI(
    title="TalentCore",
    description="Sistema de Gestion de Empleados y Vacaciones",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# RUTA PRINCIPAL
# ==========================================

@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a TalentCore",
        "estado": "Servidor funcionando correctamente",
        "version": "1.0.0"
    }


# ==========================================
# SALUD DEL SERVIDOR
# ==========================================

@app.get("/health")
def health():
    return {"status": "ok"}


# ==========================================
# RUTA DE SALUD ORIGINAL
# ==========================================

@app.get("/salud")
def verificar_salud():
    return {
        "estado": "OK",
        "sistema": "TalentCore"
    }


# ==========================================
# MODULO DE EMPLEADOS
# ==========================================

app.include_router(empleados_router)


# ==========================================
# MODULO DE VACACIONES
# ==========================================

app.include_router(vacaciones_router)

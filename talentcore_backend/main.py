
from fastapi import FastAPI

# Importar los modulos de TalentCore
from .empleados import router as empleados_router
from .vacaciones import router as vacaciones_router

# ==========================================
# SISTEMA TALENTCORE
# ==========================================

app = FastAPI(
    title="TalentCore",
    description="Sistema de Gestion de Empleados y Vacaciones",
    version="1.0.0"
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
# SALUD DEL SERVIDOR - REQUISITO DEL PROFESOR
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

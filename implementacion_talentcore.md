# TalentCore – Backend (FastAPI)

## 1. Estructura de carpetas

```
talentcore/
├─ app/
│   ├─ main.py
│   ├─ config/
│   │   └─ settings.py
│   ├─ api/
│   │   ├─ v1/
│   │   │   ├─ employees.py
│   │   │   ├─ vacations.py
│   │   │   └─ auth.py
│   ├─ core/
│   │   ├─ domain/
│   │   │   ├─ models.py
│   │   │   └─ services.py
│   │   ├─ application/
│   │   │   ├─ use_cases.py
│   │   │   └─ dtos.py
│   │   └─ infrastructure/
│   │       ├─ db.py
│   │       ├─ repositories.py
│   │       ├─ auth.py
│   │       ├─ notification.py
│   │       └─ audit.py
│   ├─ tests/
│   │   ├─ unit/
│   │   │   └─ test_services.py
│   │   └─ integration/
│   │       └─ test_api.py
│   └─ migrations/
├─ docker/
│   ├─ Dockerfile
│   └─ docker-compose.yml
├─ .env
└─ requirements.txt
```

## 2. Configuración

```python
# app/config/settings.py
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Kafka, Redis, email config omitted for brevity

settings = Settings()
```

## 3. Modelo de dominio

```python
# app/core/domain/models.py
from datetime import date
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Date, Enum as SAEnum,
    ForeignKey, JSON, TIMESTAMP, func
)
from sqlalchemy.orm import relationship
from .base import Base

class RoleEnum(str, Enum):
    EMPLOYEE = "Employee"
    SUPERVISOR = "Supervisor"
    HR = "HR"
    ADMIN = "Admin"

class VacationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

class VacationRequest(Base):
    __tablename__ = "vacation_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(SAEnum(VacationStatus), default=VacationStatus.PENDING)
    approver_id = Column(Integer, ForeignKey("employees.id"))
    comment = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approver_id])

class VacationBalance(Base):
    __tablename__ = "vacation_balances"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    total_days = Column(Integer, nullable=False)
    used_days = Column(Integer, default=0)
    pending_days = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
```

## 4. DTOs y validaciones

```python
# app/core/application/dtos.py
from datetime import date
from pydantic import BaseModel, Field, validator
from typing import Optional
from ..domain.models import VacationStatus, RoleEnum

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: RoleEnum
    department_id: Optional[int]

class EmployeeRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: RoleEnum
    department_id: Optional[int]

    class Config:
        orm_mode = True

class VacationRequestCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str

    @validator("end_date")
    def end_after_start(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

class VacationRequestUpdate(BaseModel):
    status: VacationStatus
    comment: Optional[str] = None
```

## 5. Repositorios (simplificado)

```python
# app/core/infrastructure/repositories.py
from sqlalchemy.ext.asyncio import AsyncSession
from ..domain.models import Employee, VacationRequest, VacationBalance
from typing import List

class EmployeeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, employee_id: int) -> Employee:
        return await self.db.get(Employee, employee_id)

    async def list(self) -> List[Employee]:
        result = await self.db.execute(select(Employee))
        return result.scalars().all()

    async def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

# Similar repos for VacationRequest and VacationBalance
```

## 6. Servicios de dominio

```python
# app/core/domain/services.py
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from ..infrastructure.repositories import EmployeeRepository, VacationRequestRepository
from ..domain.models import VacationStatus, VacationRequest
from ..application.dtos import VacationRequestCreate
from typing import List

class VacationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.v_repo = VacationRequestRepository(db)
        self.e_repo = EmployeeRepository(db)

    async def create_request(self, employee_id: int, data: VacationRequestCreate) -> VacationRequest:
        # 1. Validate no overlap with approved requests
        overlap = await self.v_repo.count_overlaps(
            employee_id, data.start_date, data.end_date
        )
        if overlap:
            raise ValueError("Requested period overlaps with an approved vacation")

        # 2. Validate balance (placeholder – rule pending)
        # 3. Persist
        req = VacationRequest(
            employee_id=employee_id,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
            status=VacationStatus.PENDING
        )
        return await self.v_repo.create(req)

    async def approve(self, request_id: int, approver_id: int, comment: str = None):
        req = await self.v_repo.get(request_id)
        if req.status != VacationStatus.PENDING:
            raise ValueError("Only pending requests can be approved")
        req.status = VacationStatus.APPROVED
        req.approver_id = approver_id
        req.comment = comment
        await self.v_repo.update(req)
        # TODO: update balance
```

## 7. Endpoints

```python
# app/api/v1/employees.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..core.application.dtos import EmployeeCreate, EmployeeRead
from ..core.infrastructure.repositories import EmployeeRepository
from ..core.infrastructure.auth import get_current_user, requires_role
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.infrastructure.db import get_db

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
@requires_role("Admin")
async def create_employee(
    payload: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    repo = EmployeeRepository(db)
    employee = Employee(**payload.dict())
    return await repo.create(employee)

@router.get("/", response_model=List[EmployeeRead])
@requires_role("Admin", "HR")
async def list_employees(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    repo = EmployeeRepository(db)
    return await repo.list()
```

```python
# app/api/v1/vacations.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..core.application.dtos import VacationRequestCreate, VacationRequestUpdate
from ..core.infrastructure.repositories import VacationRequestRepository
from ..core.infrastructure.auth import get_current_user, requires_role
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.infrastructure.db import get_db
from datetime import datetime

router = APIRouter(prefix="/vacations", tags=["vacations"])

@router.post("/", status_code=status.HTTP_201_CREATED)
@requires_role("Employee")
async def request_vacation(
    payload: VacationRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    service = VacationService(db)
    return await service.create_request(user["sub"], payload)

@router.patch("/{id}/approve", status_code=status.HTTP_200_OK)
@requires_role("Supervisor", "HR")
async def approve_vacation(
    id: int,
    payload: VacationRequestUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    service = VacationService(db)
    await service.approve(id, user["sub"], payload.comment)
    return {"detail": "Approved"}
```

## 8. Autenticación y autorización

```python
# app/core/infrastructure/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {"sub": payload.get("sub"), "role": payload.get("role")}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def requires_role(*roles):
    async def wrapper(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return Depends(wrapper)
```

## 9. Base de datos y migraciones

```bash
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: talent
      POSTGRES_PASSWORD: talent
      POSTGRES_DB: talentcore
    ports:
      - "5432:5432"
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql+asyncpg://talent:talent@db:5432/talentcore
      SECRET_KEY: supersecret
```

```bash
# Alembic
alembic init migrations
# edit env.py to use asyncpg
# generate migration: alembic revision --autogenerate -m "init schema"
# apply: alembic upgrade head
```

## 10. Pruebas básicas

```python
# app/tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.core.infrastructure.db import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_create_employee(client):
    payload = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "email": "ana@example.com",
        "role": "Admin"
    }
    # Assume we have a token for admin
    headers = {"Authorization": "Bearer <admin_token>"}
    r = await client.post("/api/employees/", json=payload, headers=headers)
    assert r.status_code == 201
    assert r.json()["email"] == "ana@example.com"
```

```python
# app/tests/unit/test_services.py
import pytest
from unittest.mock import AsyncMock
from app.core.domain.services import VacationService
from app.core.application.dtos import VacationRequestCreate

@pytest.mark.asyncio
async def test_create_request_overlap():
    db = AsyncMock()
    service = VacationService(db)
    db_repo = AsyncMock()
    db_repo.count_overlaps.return_value = 1
    service.v_repo = db_repo

    with pytest.raises(ValueError):
        await service.create_request(1, VacationRequestCreate(
            start_date="2024-12-01",
            end_date="2024-12-10",
            reason="Holiday"
        ))
```

## 11. Instrucciones de ejecución

```bash
# 1. Clonar repo
git clone <repo>
cd talentcore

# 2. Crear .env
cp .env.example .env
# Editar DATABASE_URL, SECRET_KEY

# 3. Construir y levantar contenedores
docker compose up --build

# 4. Ejecutar migraciones
docker compose exec api alembic upgrade head

# 5. Acceder a Swagger UI
http://localhost:8000/docs
```

## 12. Pendientes (reglas de negocio no confirmadas)

| Item | Acción pendiente |
|------|------------------|
| Límite anual de días | Definir número y lógica de acumulación |
| Política de acumulación | Límite de años anteriores y reglas de rollover |
| Periodo mínimo antes de la fecha de inicio | Configurar y validar |
| Aprobación jerárquica | Decidir si se necesita supervisor + HR |
| Intersección parcial de solicitudes | Permitir o bloquear |
| Días no laborables | Implementar tabla de festivos y cálculo de business days |
| Canales de notificación | Definir qué canales y destinatarios |
| Cancelación de solicitud | Condiciones y lógica de cancelación |
| Firma electrónica | Integrar o descartar |
| Nivel de detalle de reportes | Definir métricas y filtros |
| Integración externa | ERP, calendario, etc. |
| Auditoría | IP, timestamp, usuario, tabla de logs |

> **Nota**: Hasta la fecha, la lógica de saldo, acumulación y notificaciones están marcadas como TODO. Se deben confirmar las reglas antes de avanzar a producción.
# TalentCore – Arquitectura Técnica

## 1. Resumen de la arquitectura propuesta  
Aplicación monolítica desacoplada en capas, con **FastAPI** como API REST, **React** (Vite) para el SPA, y **PostgreSQL** como BD relacional. Se emplea **Docker** y **Docker‑Compose** para entornos de desarrollo y despliegue. La capa de negocio se divide en *Domain*, *Application* y *Infrastructure* siguiendo Clean Architecture. La comunicación entre servicios internos se realiza mediante eventos de **Kafka** (notificaciones, auditoría).  

## 2. Tecnologías recomendadas y justificación  

| Tecnología | Rol | Justificación |
|------------|-----|---------------|
| **FastAPI** | Backend | Rendimiento alto, soporte nativo de async, OpenAPI automático, validación Pydantic. |
| **PostgreSQL** | BD | ACID, soporte de tipos de datos (date, interval), extensiones (pg_trgm, hstore). |
| **SQLAlchemy 2.0** | ORM | Compatibilidad con async, mapeo declarativo, migraciones con Alembic. |
| **Alembic** | Migraciones | Control de versiones de esquema, rollback automático. |
| **React + Vite** | Frontend | Ecosistema moderno, hot‑reload, integración con TypeScript. |
| **JWT + OAuth2** | Autenticación | Stateless, soporte de scopes, revocación mediante blacklist. |
| **Redis** | Cache & Rate‑limit | Almacenamiento de tokens, sesiones temporales, colas de notificaciones. |
| **Kafka** | Event Bus | Escalabilidad, desacoplamiento de notificaciones y auditoría. |
| **Docker + Docker‑Compose** | Contenedores | Entorno reproducible, CI/CD. |
| **GitHub Actions** | CI/CD | Build, test, lint, deploy. |
| **Postman / Swagger UI** | API testing | Documentación interactiva. |
| **pytest + httpx** | Unit/Integration tests | Test de endpoints async. |
| **Sentry** | Error monitoring | Captura de excepciones en producción. |

## 3. Arquitectura frontend, backend y base de datos  

```
┌───────────────────────┐
│ 1. Frontend (React)   │
│    - SPA, TypeScript  │
│    - Consume API REST │
└─────────────┬─────────┘
              │
              ▼
┌───────────────────────┐
│ 2. Backend (FastAPI)  │
│    - Domain Layer     │
│    - Application Layer│
│    - Infrastructure   │
│    - API Endpoints    │
│    - Auth, Rate‑limit │
└─────────────┬─────────┘
              │
              ▼
┌───────────────────────┐
│ 3. Database (PostgreSQL)│
│    - Employees, Vacations, Roles, Permissions, Audit, Settings│
└───────────────────────┘
```

- **Event Bus (Kafka)** se conecta a la capa de infraestructura para publicar eventos de notificación y auditoría.  
- **Redis** se usa para cache de tokens y colas de notificaciones.  

## 4. Componentes y responsabilidades  

| Componente | Responsabilidad |
|------------|-----------------|
| **Auth Service** | Gestión de usuarios, JWT, OAuth2, revocación. |
| **Employee Service** | CRUD de empleados, asignación de roles. |
| **Vacation Service** | Creación, validación, aprobación, cálculo de saldo. |
| **Notification Service** | Envío de email/SMS/Push, consumo de eventos Kafka. |
| **Audit Service** | Registro de cambios, IP, timestamp, usuario. |
| **Reporting Service** | Generación de PDF/Excel, filtros avanzados. |
| **API Gateway** | Rate‑limit, CORS, logging. |
| **Database Layer** | Acceso a tablas, transacciones, índices. |

## 5. Modelo de datos con entidades y relaciones  

```
Employee
├─ id PK
├─ first_name
├─ last_name
├─ email UNIQUE
├─ role_id FK → Role.id
├─ department_id FK → Department.id
├─ created_at
├─ updated_at

Role
├─ id PK
├─ name (Employee, Supervisor, HR, Admin)
├─ permissions JSONB

Department
├─ id PK
├─ name

VacationRequest
├─ id PK
├─ employee_id FK → Employee.id
├─ start_date DATE
├─ end_date DATE
├─ reason TEXT
├─ status ENUM('PENDING','APPROVED','REJECTED','CANCELLED')
├─ approver_id FK → Employee.id (Supervisor/HR)
├─ comment TEXT
├─ created_at
├─ updated_at

VacationBalance
├─ id PK
├─ employee_id FK → Employee.id
├─ year INT
├─ total_days INT
├─ used_days INT
├─ pending_days INT
├─ created_at
├─ updated_at

AuditLog
├─ id PK
├─ user_id FK → Employee.id
├─ action TEXT
├─ entity_type TEXT
├─ entity_id INT
├─ old_value JSONB
├─ new_value JSONB
├─ ip_address TEXT
├─ timestamp TIMESTAMP

Notification
├─ id PK
├─ user_id FK → Employee.id
├─ type ENUM('EMAIL','SMS','INTERNAL')
├─ status ENUM('PENDING','SENT','FAILED')
├─ payload JSONB
├─ created_at
├─ sent_at
```

- Índices en `VacationRequest.start_date`, `VacationRequest.end_date`, `VacationBalance.year`.  
- `permissions` en `Role` permite granularidad sin tabla intermedia.

## 6. Endpoints REST para empleados y vacaciones  

| Método | Ruta | Descripción | Roles permitidos |
|--------|------|-------------|------------------|
| POST | `/api/employees/` | Crear empleado | Admin |
| GET | `/api/employees/` | Listar empleados | Admin, HR |
| GET | `/api/employees/{id}` | Detalle | Admin, HR, Supervisor (solo propios) |
| PUT | `/api/employees/{id}` | Actualizar | Admin |
| DELETE | `/api/employees/{id}` | Eliminar | Admin |
| POST | `/api/vacations/` | Solicitar vacaciones | Employee |
| GET | `/api/vacations/` | Listar solicitudes del usuario | Employee |
| GET | `/api/vacations/{id}` | Detalle solicitud | Employee, Supervisor, HR |
| PATCH | `/api/vacations/{id}/approve` | Aprobar | Supervisor, HR |
| PATCH | `/api/vacations/{id}/reject` | Rechazar | Supervisor, HR |
| PATCH | `/api/vacations/{id}/cancel` | Cancelar | Employee (pendiente) |
| GET | `/api/vacations/balance` | Saldo actual | Employee |
| GET | `/api/vacations/history` | Historial | Employee |
| GET | `/api/vacations/report` | Reporte | HR |
| POST | `/api/auth/login` | Login | Todos |
| POST | `/api/auth/logout` | Logout | Todos |

Todos los endpoints devuelven JSON, usan códigos HTTP estándar y validan con Pydantic.

## 7. Autenticación y permisos por roles  

- **JWT** con claims: `sub`, `role`, `exp`.  
- Middleware de FastAPI verifica token y carga `current_user`.  
- Decorador `@requires_role(*roles)` valida permiso.  
- Permisos almacenados en `Role.permissions` (JSONB) y evaluados en tiempo de ejecución.  

## 8. Flujo de solicitud, aprobación y rechazo  

1. **Empleado** crea `VacationRequest` → estado `PENDING`.  
2. Se publica evento `vacation.requested` en Kafka.  
3. **Notification Service** envía email/SMS al supervisor.  
4. Supervisor revisa → `approve` o `reject`.  
5. Se actualiza `status`, se publica evento `vacation.approved/rejected`.  
6. **Vacation Service** recalcula `VacationBalance` (solo en aprobación).  
7. **Notification Service** envía resultado al empleado.  
8. **Audit Service** registra cada cambio.  

## 9. Validaciones de fechas y saldo de vacaciones  

- **Rango de fechas**: `start_date <= end_date`.  
- **No superposición**: consulta `VacationRequest` con `status='APPROVED'` y rango intersectante.  
- **Días laborables**: función `business_days(start, end)` excluye sábados, domingos y festivos (tabla `Holiday`).  
- **Saldo**: `available = total_days - used_days - pending_days`. Se valida antes de crear solicitud.  
- **Periodo de solicitud**: regla configurable (`settings.request_window_days`).  
- **Cancelación**: solo si `status='PENDING'` y `days_from_start >= settings.min_days_before_start`.  

## 10. Auditoría y notificaciones  

- **Audit Log**: cada CRUD y cambio de estado se registra con `user_id`, `action`, `old_value`, `new_value`, `ip_address`.  
- **Event Bus**: eventos `vacation.*`, `employee.*` publicados en Kafka.  
- **Notification Service**: consume eventos, decide canal (email, SMS, internal), envía y actualiza estado.  
- **Retry**: Kafka consumer con back‑off y dead‑letter queue.  

## 11. Organización de carpetas del proyecto  

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
│   │   └─ integration/
│   └─ migrations/
├─ docker/
│   ├─ Dockerfile
│   └─ docker-compose.yml
├─ frontend/
│   ├─ src/
│   ├─ public/
│   └─ vite.config.ts
├─ scripts/
│   └─ seed.py
└─ .env
```

## 12. Estrategia de pruebas  

| Tipo | Herramienta | Alcance |
|------|-------------|---------|
| Unit | pytest + pytest‑asyncio | Lógica de dominio, validaciones. |
| Integration | httpx + TestClient | Endpoints, repositorios. |
| End‑to‑End | Cypress | Flujo completo (login → solicitud → aprobación). |
| Load | Locust | Rendimiento de API y Kafka. |
| Security | OWASP ZAP | Escaneo de vulnerabilidades. |

- Cobertura mínima 80 % en código crítico.  
- CI ejecuta pruebas en cada PR.  

## 13. Riesgos técnicos y recomendaciones  

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| **Latencia de Kafka** | Retraso en notificaciones | Configurar `linger.ms`, usar `async` consumer, monitorizar métricas. |
| **Consistencia de saldo** | Doble contabilización | Usar transacciones con `SELECT FOR UPDATE` al actualizar `VacationBalance`. |
| **Escalabilidad del backend** | Saturación de CPU | Habilitar `uvicorn` con workers, usar `asyncpg`. |
| **Gestión de roles** | Permisos insuficientes | Validar en middleware, pruebas de autorización. |
| **Datos sensibles** | Exposición de JWT | HTTPS obligatorio, rotate keys, blacklist revocación. |
| **Dependencia de terceros (SMS, Email)** | Fallos externos | Retry con back‑off, fallback a notificación interna. |
| **Migraciones en producción** | Downtime | Plan de rollback, pruebas en staging, `pg_dump` antes de migrar. |

## 14. Reglas de negocio pendientes de confirmar  

1. Límite anual de días por empleado.  
2. Política de acumulación y límite de años anteriores.  
3. Periodo mínimo antes de la fecha de inicio para solicitar.  
4. Necesidad de aprobación jerárquica (supervisor + HR) o única.  
5. Permitir o no superposición parcial de solicitudes aprobadas.  
6. Exclusión de fines de semana y festivos del conteo.  
7. Canales de notificación y destinatarios exactos.  
8. Condiciones de cancelación de solicitud pendiente.  
9. Integración con sistemas externos (ERP, calendario).  
10. Requisitos de firma electrónica.  
11. Nivel de detalle requerido en reportes (departamento, tipo de vacación).  
12. Mecanismo de auditoría (IP, timestamp, usuario).  

---
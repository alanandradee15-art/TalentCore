# Auditoria de Seguridad - TalentCore

Fecha: 2026-10-27 03:11

# Informe de Revisión Estática de Seguridad – TalentCore

## 1. Resumen ejecutivo  
TalentCore expone una API REST sin mecanismos de autenticación ni autorización. Los endpoints de empleados y vacaciones aceptan datos sin validación exhaustiva (p. ej., formato de correo, longitud de campos, unicidad). La base de datos SQLite se accede sin cifrado ni control de acceso. Se observan riesgos de exposición de datos, inyección de SQL en funciones internas y falta de protección de secretos.

## 2. Riesgos encontrados y evidencia  
- **Ausencia de autenticación/ autorización**: `main.py` incluye rutas públicas (`/`, `/salud`, `/empleados`, `/vacaciones`) sin middleware de seguridad.  
- **Validación insuficiente de entrada**: `EmpleadoCrear` no valida `correo` ni impide valores vacíos en `puesto` o `departamento`.  
- **Falta de unicidad en correo**: la tabla `empleados` no define `UNIQUE` sobre `correo`.  
- **SQL injection potencial en `database.py`**: `agregar_columna_si_falta` construye consultas con f‑strings usando nombres de tabla/columna.  
- **Exposición de datos sensibles**: la API devuelve directamente objetos `sqlite.Row` sin filtrado.  
- **Sin cifrado de datos en reposo**: SQLite se almacena en disco sin encriptación.  
- **Sin gestión de secretos**: no se usan variables de entorno ni archivos `.env` para claves o rutas.  
- **Sin protección de headers**: no se configuran `Strict-Transport-Security`, `X-Content-Type-Options`, etc.  
- **Sin control de acceso a recursos**: cualquier cliente puede crear, leer, actualizar o eliminar empleados y vacaciones.  
- **Sin auditoría**: no se registran cambios ni intentos fallidos.  
- **Sin rate‑limiting**: posible abuso de endpoints.  

## 3. Clasificación de severidad  
| Riesgo | Severidad | Impacto | Prioridad |
|--------|-----------|---------|-----------|
| Autenticación/ autorización | Alta | Acceso no autorizado | 1 |
| Validación de entrada | Media | Inyección de datos, XSS | 2 |
| SQL injection en funciones internas | Media | Modificación de esquema | 3 |
| Exposición de datos sensibles | Alta | Violación de privacidad | 1 |
| Cifrado de datos en reposo | Media | Robo de información | 3 |
| Gestión de secretos | Alta | Compromiso de credenciales | 1 |
| Protección de headers | Baja | Vulnerabilidad de seguridad web | 4 |
| Control de acceso a recursos | Alta | Manipulación de datos | 1 |
| Auditoría | Media | Dificultad de trazabilidad | 3 |
| Rate‑limiting | Baja | Denegación de servicio | 4 |

## 4. Autenticación y autorización  
No se implementa ningún esquema de autenticación (JWT, OAuth2, sesiones). Se recomienda integrar OAuth2 con scopes y roles (empleado, aprobador, administrador). Los endpoints deben protegerse con dependencias de FastAPI (`Depends`) y verificar el rol antes de permitir operaciones CRUD.

## 5. Validación de entradas y SQL  
- Añadir validación de correo con `EmailStr` de Pydantic.  
- Definir longitud máxima y patrones regex para `nombre`, `apellido`, `puesto`, `departamento`.  
- Añadir restricción `UNIQUE` en `correo`.  
- Evitar f‑strings en `database.py`; usar parámetros o `sqlalchemy` para alteraciones de esquema.  
- Implementar transacciones explícitas y manejo de errores con `try/except`.

## 6. Protección de datos y secretos  
- Cifrar la base de datos SQLite con `sqlcipher` o mover a PostgreSQL con cifrado en reposo.  
- Almacenar claves y rutas en variables de entorno (`dotenv`).  
- Configurar `HTTPS` y `HSTS`.  
- Añadir cabeceras de seguridad (`X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`).  
- Implementar auditoría de cambios y eventos de seguridad.

## 7. Recomendaciones priorizadas  
1. **Implementar autenticación y autorización** con OAuth2 y roles.  
2. **Añadir validación de correo y unicidad** en la tabla `empleados`.  
3. **Cifrar la base de datos** y protegerla con permisos de archivo.  
4. **Gestionar secretos** mediante variables de entorno y un gestor de secretos.  
5. **Agregar protección de headers** y forzar HTTPS.  
6. **Implementar rate‑limiting** (por IP y por usuario).  
7. **Registrar auditoría** de operaciones críticas.  
8. **Revisar funciones internas** que usan f‑strings y migrar a ORM o consultas parametrizadas.  
9. **Añadir pruebas de validación** de entrada y de autorización.  
10. **Documentar y revisar** la política de gestión de datos y retención.

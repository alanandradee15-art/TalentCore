# TalentCore

## Sistema de Gestión de Empleados y Solicitudes de Vacaciones

**Proyecto académico de desarrollo de software con agentes de inteligencia artificial**

### 1. Descripción del proyecto

TalentCore es un sistema de gestión de recursos humanos desarrollado con Python y FastAPI. Su objetivo es facilitar la administración de empleados y la gestión de solicitudes de vacaciones mediante una API REST.

El proyecto se desarrolló aplicando las etapas del ciclo de vida del desarrollo de software (SDLC), con apoyo de agentes de inteligencia artificial especializados en análisis, arquitectura, desarrollo, calidad, seguridad y DevOps.

El sistema cuenta con documentación interactiva mediante Swagger UI y una API desplegada en internet que puede utilizarse desde una computadora o teléfono celular.

### 2. Objetivo general

Diseñar e implementar un sistema que permita registrar, consultar, actualizar y eliminar empleados, gestionar solicitudes de vacaciones, aprobarlas o rechazarlas y consultar los días disponibles según la antigüedad del trabajador.

### 3. Enlaces del proyecto

**Perfil de GitHub:**

https://github.com/alanandradee15-art

**Repositorio del proyecto:**

https://github.com/alanandradee15-art/TalentCore

**API web desplegada en Render:**

https://talentcore-api-z4fd.onrender.com

**Documentación interactiva Swagger UI:**

https://talentcore-api-z4fd.onrender.com/docs

La documentación Swagger permite consultar y probar los servicios del sistema directamente desde el navegador, incluyendo dispositivos móviles.

### 4. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python | Lenguaje de programación |
| FastAPI | Desarrollo de la API REST |
| SQLite | Almacenamiento de datos |
| Pydantic | Validación de información |
| Pytest | Pruebas automatizadas |
| Git y GitHub | Control de versiones |
| GitHub Actions | Integración continua |
| Render | Despliegue web |
| Swagger UI | Documentación y pruebas de la API |
| Visual Studio Code | Entorno de desarrollo |
| Groq e inteligencia artificial | Apoyo al desarrollo mediante agentes |

### 5. Funcionalidades del sistema

**Gestión de empleados**

- Registrar empleados.
- Consultar todos los empleados.
- Buscar empleados mediante su identificador.
- Actualizar información de empleados.
- Eliminar empleados cuando no tengan solicitudes de vacaciones asociadas.
- Registrar los años de antigüedad.

**Gestión de vacaciones**

- Registrar solicitudes de vacaciones.
- Consultar solicitudes existentes.
- Consultar el historial de vacaciones.
- Aprobar o rechazar solicitudes.
- Calcular los días de vacaciones según la antigüedad.
- Consultar el saldo disponible de vacaciones.

**Base de datos**

El sistema utiliza SQLite para almacenar información de empleados, solicitudes de vacaciones y registros de auditoría.

La base de datos se inicializa automáticamente al arrancar el backend del repositorio.

### 6. Cómo funciona TalentCore

El sistema funciona mediante una API REST que recibe solicitudes HTTP y devuelve respuestas en formato JSON.

El usuario puede realizar operaciones desde Swagger UI:

1. Selecciona una operación disponible.
2. Introduce los datos solicitados.
3. Ejecuta la petición.
4. El backend procesa la información.
5. El sistema consulta o modifica la base de datos.
6. La API devuelve el resultado y un código HTTP.

Entre las operaciones disponibles se encuentran el registro de empleados, la consulta de información y la administración de vacaciones.

### 7. Cómo utilizar TalentCore desde un teléfono

1. Abrir Google Chrome, Safari u otro navegador.
2. Ingresar a https://talentcore-api-z4fd.onrender.com/docs
3. Esperar a que cargue Swagger UI.
4. Seleccionar el endpoint que se desea probar.
5. Presionar **Try it out**.
6. Introducir los datos requeridos.
7. Presionar **Execute**.
8. Revisar **Server response**, el código HTTP y **Response body**.

Por ejemplo, una respuesta `200` indica que la petición se procesó correctamente. Otros códigos pueden indicar errores de validación, permisos o recursos no encontrados.

### 8. Flujo de prueba solicitado por el profesor

La demostración de la API web contempla las siguientes operaciones:

**Paso 1. Registrar al administrador inicial**

`POST /api/v1/empleados`

**Paso 2. Registrar un Manager y un Empleado**

`POST /api/v1/empleados`

Utilizar el encabezado `X-User-Id` cuando la operación lo requiera.

**Paso 3. Solicitar vacaciones**

`POST /api/v1/vacaciones/solicitar`

**Paso 4. Revisar y aprobar una solicitud**

`POST /api/v1/vacaciones/{solicitud_id}/revisar`

**Paso 5. Consultar el saldo de vacaciones**

`GET /api/v1/vacaciones/saldo/{empleado_id}`

Este flujo corresponde a la API web utilizada durante la demostración. Las rutas, los campos requeridos y las restricciones de acceso deben verificarse en Swagger antes de ejecutar las solicitudes.

**Importante:** La API publicada en Render y el backend almacenado en este repositorio pueden presentar diferencias de implementación. No debe asumirse que ambas versiones contienen exactamente las mismas rutas.

### 9. Ejemplos de consultas

**Consultar empleados registrados:**

`GET /api/v1/empleados`

**Buscar un empleado por ID:**

`GET /api/v1/empleados/{empleado_id}`

Por ejemplo:

`GET /api/v1/empleados/2`

**Consultar el estado del servidor:**

`GET /health`

Estos ejemplos permiten verificar las operaciones básicas de la API.

### 10. Instalación y ejecución local

**Requisitos:**

- Python 3.11 o compatible.
- Git.
- Acceso a una terminal.

**1. Clonar el repositorio**

```bash
git clone https://github.com/alanandradee15-art/TalentCore.git
```

**2. Entrar a la carpeta del proyecto**

```bash
cd TalentCore
```

**3. Crear un entorno virtual**

```bash
python -m venv venv
```

**4. Activar el entorno virtual en Windows**

```powershell
.\venv\Scripts\Activate.ps1
```

**5. Instalar las dependencias principales**

```bash
python -m pip install fastapi uvicorn pydantic pytest httpx
```

**6. Ejecutar el servidor**

```bash
python -m uvicorn talentcore_backend.main:app --reload
```

**7. Abrir Swagger UI**

http://127.0.0.1:8000/docs

### 11. Pruebas automatizadas

TalentCore utiliza Pytest para verificar el funcionamiento de diferentes componentes.

Durante la ejecución local del proyecto se obtuvo el siguiente resultado:

**20 pruebas aprobadas.**

Las pruebas incluyen verificaciones relacionadas con:

- Funcionamiento de endpoints.
- Registro y consulta de empleados.
- Solicitudes de vacaciones.
- Validación de información.
- Cálculo de días de vacaciones.

**Comando para ejecutar las pruebas:**

```bash
python -m pytest tests/test_talentcore.py -v
```

El repositorio también contiene una configuración de GitHub Actions para realizar verificaciones automáticas del código.

### 12. Arquitectura del proyecto

La estructura principal del repositorio es:

```text
TalentCore/
├── .github/
│   └── workflows/
├── talentcore_backend/
│   ├── database.py
│   ├── empleados.py
│   ├── main.py
│   └── vacaciones.py
├── tests/
│   └── test_talentcore.py
├── .gitignore
├── README.md
├── AUDIT_REPORT.md
├── arquitectura_talentcore.md
├── implementacion_talentcore.md
├── reporte_devops_talentcore.md
├── reporte_qa_talentcore.md
└── requisitos_talentcore.md
```

**Descripción de los archivos principales:**

- `main.py`: configuración de la aplicación FastAPI y registro de rutas.
- `database.py`: conexión e inicialización de la base de datos SQLite.
- `empleados.py`: operaciones relacionadas con empleados.
- `vacaciones.py`: gestión de solicitudes y saldos de vacaciones.
- `tests/test_talentcore.py`: pruebas automatizadas.
- `README.md`: documentación principal del proyecto.

### 13. Agentes de inteligencia artificial

Durante el desarrollo se trabajó con agentes especializados en diferentes etapas del SDLC:

1. **Product Owner:** análisis y documentación de requisitos.
2. **Arquitecto:** diseño de la arquitectura del sistema.
3. **Desarrollador:** apoyo en la implementación del backend.
4. **QA:** pruebas y revisión de calidad.
5. **Seguridad:** análisis de riesgos y vulnerabilidades.
6. **DevOps:** documentación y preparación del despliegue.

### 14. Documentación adicional

El repositorio incluye documentación relacionada con:

- Requisitos del sistema.
- Arquitectura de software.
- Implementación.
- Calidad y pruebas.
- Auditoría y seguridad.
- DevOps y despliegue.

Estos documentos complementan la información presentada en el README.

### 15. Estado actual del proyecto

TalentCore cuenta con un backend implementado, base de datos SQLite, endpoints para gestionar empleados y vacaciones, pruebas automatizadas y una API accesible desde internet mediante Render.

Se realizaron pruebas locales y demostraciones desde un navegador móvil utilizando Swagger UI.

Como mejoras pendientes se consideran:

- Verificar la correspondencia completa entre la versión del repositorio y la API desplegada.
- Fortalecer la autenticación y autorización.
- Ampliar las pruebas de integración.
- Revisar el comportamiento del almacenamiento de datos en producción.

### 16. Autor

**Alan Mauricio Andrade Silva**

Proyecto académico de desarrollo de software con agentes de inteligencia artificial.

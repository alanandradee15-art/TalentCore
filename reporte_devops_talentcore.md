# Reporte DevOps – TalentCore

## 1. Objetivo del despliegue  
- **Entrega continua** de la API FastAPI en contenedores Docker.  
- **Pruebas automatizadas** con `pytest` en cada push a `main`.  
- **Seguridad** de credenciales y variables de entorno.  
- **Escalabilidad mínima** (solo un servicio backend + base de datos SQLite en contenedor).  

## 2. Estructura recomendada de Dockerfile  
```dockerfile
# 1️⃣ Imagen base ligera
FROM python:3.12-slim

# 2️⃣ Variables de entorno de compilación
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3️⃣ Directorio de trabajo
WORKDIR /app

# 4️⃣ Copiar dependencias primero para cache
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# 5️⃣ Copiar el código fuente
COPY . .

# 6️⃣ Exponer puerto
EXPOSE 8000

# 7️⃣ Comando de inicio
CMD ["uvicorn", "generated_project.talentcore_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- **Ventajas**: caché de capas, sin virtualenv, imagen mínima.  
- **Nota**: Si se usan dependencias de C, agregar `build-essential` antes de `pip install`.

## 3. Configuración recomendada de docker‑compose.yml  
```yaml
version: "3.9"

services:
  backend:
    build: .
    container_name: talentcore_backend
    restart: unless-stopped
    env_file: .env
    environment:
      - DATABASE_URL=sqlite:///./db.sqlite3
    volumes:
      - ./app:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: nouchka/sqlite3
    container_name: talentcore_db
    volumes:
      - db_data:/var/lib/sqlite
    command: ["sqlite3", "/var/lib/sqlite/db.sqlite3"]

volumes:
  db_data:
```
- **Persistencia**: volumen `db_data` mantiene la base SQLite entre reinicios.  
- **Separación**: `backend` y `db` son servicios independientes, facilitando pruebas y despliegue.

## 4. Pipeline de GitHub Actions para ejecutar pytest  
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      db:
        image: nouchka/sqlite3
        ports:
          - 5432:5432
        options: >-
          --health-cmd "sqlite3 /var/lib/sqlite/db.sqlite3 .schema"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: 3.12

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/poetry.lock') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install --no-dev

      - name: Run tests
        env:
          DATABASE_URL: sqlite:///./tests/test_db.sqlite3
        run: python -m pytest tests/test_talentcore.py -v
```
- **Servicios**: se levanta un contenedor SQLite para pruebas.  
- **Variables**: `DATABASE_URL` se sobreescribe en el job.  
- **Cache**: acelera la instalación de dependencias.

## 5. Manejo seguro de variables de entorno  
1. **Archivo `.env`**: solo en local, no se commitea.  
2. **Secrets de GitHub**:  
   - `DATABASE_URL`  
   - `SECRET_KEY` (si se usa JWT)  
   - `API_TOKEN` (para integraciones externas)  
3. **Acceso**: en `docker-compose.yml` usar `env_file: .env` y `environment:` para variables que deben sobrescribirse.  
4. **Rotación**: usar GitHub Actions `secrets` con expiración y rotación manual.  
5. **Auditoría**: revisar logs de GitHub Actions para asegurar que no se expongan secretos.

## 6. Pasos para validar el despliegue  
1. **Build local**  
   ```bash
   docker compose build
   docker compose up -d
   ```
2. **Health check**  
   - `curl http://localhost:8000/health` → debe devolver 200.  
3. **Pruebas de integración**  
   - Ejecutar `pytest tests/test_talentcore.py` contra el contenedor.  
4. **Verificar persistencia**  
   - Insertar un registro, reiniciar contenedor, comprobar que persiste.  
5. **Logs**  
   - `docker logs talentcore_backend` → sin errores críticos.  
6. **Seguridad**  
   - Revisar que no haya variables de entorno expuestas en logs.  

## 7. Riesgos y tareas pendientes  
| Riesgo | Impacto | Mitigación | Pendiente |
|--------|---------|------------|-----------|
| SQLite no es multi‑usuario | Concurrencia limitada | Migrar a PostgreSQL en producción | Plan de migración |
| Exposición accidental de secretos | Brecha de seguridad | Revisar `secrets` y `.env` | Auditoría de repositorio |
| Falta de pruebas de carga | Rendimiento desconocido | Añadir pruebas con Locust | Implementar |
| Dependencias de C no cubiertas | Build fallido | Añadir `build-essential` en Dockerfile | Verificar |
| Falta de monitoreo | Detección tardía de fallos | Integrar Prometheus + Grafana | Configurar |
| No se gestiona la base de datos en contenedor | Pérdida de datos | Volumen persistente configurado | Confirmar |
| Pipeline no notifica a Slack/Teams | Falta de visibilidad | Añadir acción de notificación | Implementar |

---
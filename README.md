# Dockerizar una API FastAPI

## 0. Cambios necesarios en main.py

Antes de dockerizar, hay dos ajustes que se deben hacer al código.

### 1. Leer la URL de la base de datos desde una variable de entorno

Un contenedor no sabe nada de tu máquina local. La conexión a la base de datos debe llegar desde afuera, no estar escrita en el código.

```python
# antes
DATABASE_URL = "postgresql://neondb_owner:abc123@host-remoto/neondb"

# después
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/neondb")
```

---

## Prerrequisitos

- Docker Desktop instalado y corriendo

---

## 1. Dockerfile

```dockerfile
FROM python:3.13-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 2. Construir la imagen

```bash
docker build -t fastapi-iot .
```

```bash
docker images fastapi-iot
```

---

## 3. Build multiplataforma

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t fastapi-iot \
  .
```

---

# 4. Red manual entre contenedores

## Crear red

```bash
docker network create iot-network
```

## Crear DB

```bash
docker run -d \
  --name db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iotdb \
  postgres:17
```

## Crear API

```bash
docker run -d \
  --name api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/iotdb \
  fastapi-iot
```

## Conectar a red

```bash
docker network connect iot-network db
docker network connect iot-network api
```

## Verificar

```bash
docker network inspect iot-network
```

## Test

```bash
docker exec -it api sh
ping db
```

---

# 5. Docker Compose

```mermaid
graph LR
    subgraph docker_network
        api["API"]
        db["Postgres"]
    end

    api --> db
```

```yaml
version: "3.9"

services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: iotdb

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/iotdb
    depends_on:
      - db
```

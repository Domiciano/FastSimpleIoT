# Dockerizar una API FastAPI

## Cambios necesarios en main.py

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


## Prerrequisitos

- Docker Desktop instalado y corriendo



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

`--host 0.0.0.0` es obligatorio. Sin esto uvicorn solo escucha dentro del contenedor > y no es accesible desde el host.

## 2. Construir la imagen
Ejecutar desde la **raíz del proyecto** (donde están Dockerfile y main.py)
```bash
docker build -t fastapi-iot .
```

```bash
docker images ls
```



## 3. Build multiplataforma
Por defecto docker build construye para la arquitectura de tu máquina (ej. arm64 en Apple Silicon). Para publicar una imagen que funcione en amd64 (servidores Linux) y arm64 simultáneamente
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t fastapi-iot \
  .
```



# 4. Red manual entre contenedores

## Crear red

```bash
docker network create iot-network
```

## Ejercutar contenedor de DB

```bash
docker run -d \
  --name db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iotdb \
  postgres:17
```

## Conectar a red

```bash
docker network connect iot-network db
```



```bash
docker run -d \
  --name api \
  -p 8000:8000 \
  --network iot-network \
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/iotdb \
  fastapiiot
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





## 5. Docker Compose: dos servicios

El archivo `docker-compose.yml` define dos servicios en la misma red:

```
┌─────────────────────────────────────┐
│          red: docker_default        │
│                                     │
│  ┌──────────┐      ┌─────────────┐  │
│  │   api    │─────▶│     db      │  │
│  │ :8000    │      │ postgres:17 │  │
│  └──────────┘      └─────────────┘  │
└─────────────────────────────────────┘
```

El servicio `api` se conecta a `db` usando el hostname `db` — Docker Compose registra
cada servicio como hostname en la red interna:

```yaml
environment:
  - DATABASE_URL=postgresql://postgres:postgres@db:5432/iotdb
#                                              ^^^
#                                    hostname del servicio postgres
```

`depends_on` hace que `api` arranque después de que el contenedor `db` esté corriendo:

```yaml
depends_on:
  - db
```

### Levantar los servicios

Desde la **raíz del proyecto**:

```bash
docker compose up --build
```

`--build` fuerza reconstruir la imagen de `api`. Para correr en background:

```bash
docker compose up --build -d
```

Para detener y eliminar los contenedores:

```bash
docker compose down
```

---

## 6. Inspeccionar la red

Docker Compose crea automáticamente una red llamada `<carpeta>_default`.

### Listar todas las redes

```bash
docker network ls
```

Salida esperada (entre otras):

```
NETWORK ID     NAME             DRIVER    SCOPE
83d8498846d8   docker_default   bridge    local
```

### Ver contenedores conectados y sus IPs

```bash
docker network inspect docker_default
```

En la sección `Containers` verán los dos contenedores con sus IPs asignadas dentro
de la red interna (ej. `172.18.0.2`, `172.18.0.3`).

### Ver la red de un contenedor específico

```bash
docker inspect docker-api-1
```

Buscar `NetworkSettings.Networks` para ver la IP, gateway y redes a las que pertenece.

### Probar conectividad entre contenedores

```bash
# Entrar al contenedor api
docker exec -it docker-api-1 sh

# Dentro del contenedor, resolver el hostname "db"
cat /etc/hosts
```

---

## 7. Verificar que todo funciona

```bash
# Health check
curl http://localhost:8000/

# Guardar una lectura (persiste en PostgreSQL)
curl -X POST http://localhost:8000/readings \
  -H "Content-Type: application/json" \
  -d '{"value":100,"timestamp":1234,"deviceName":"Sensor01","unit":"celsius"}'

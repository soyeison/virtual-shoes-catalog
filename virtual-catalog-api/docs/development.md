# Desarrollo local

Cómo ejecutar la API en tu máquina, con RustFS en Docker. Para levantar todo el stack (RustFS + API + web) en contenedores, consulta el README de la raíz del monorepo.

## Requisitos

- Python **3.12**
- Docker con Docker Compose, para RustFS
- Opcional: el CLI `sqlite3`, para inspeccionar la base de datos

## 1. Entorno virtual y dependencias

```bash
cd virtual-catalog-api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Dependencias principales (`requirements.txt`):

| Paquete | Uso |
| --- | --- |
| `fastapi`, `uvicorn` | Framework web y servidor ASGI |
| `pydantic`, `pydantic-settings` | Validación de datos y configuración |
| `python-dotenv` | Lectura del `.env` (la usa pydantic-settings) |
| `python-multipart` | Formularios y subida de archivos (`POST /articles`) |
| `bcrypt`, `PyJWT` | Hash de contraseñas y tokens |
| `boto3` | Cliente S3 para RustFS |
| `stripe` | Pasarela de pago |
| `pytest`, `pytest-cov` | Tests y cobertura |

## 2. Variables de entorno

```bash
cp .env.example .env
```

Completa los valores (ver [configuration.md](configuration.md)). Para desarrollo local:

```dotenv
DATABASE_PATH=data/catalogo.db
CORS_ORIGINS=["http://localhost:4321"]
S3_ENDPOINT=http://localhost:9000
S3_PUBLIC_URL=http://localhost:9000
S3_ACCESS_KEY=admin
S3_SECRET_KEY=password123
S3_BUCKET=catalogo-images
PAYMENT_GATEWAY_PROVIDER=mock
STRIPE_SECRET_KEY=
```

## 3. Levantar RustFS

Desde la **raíz del monorepo**:

```bash
docker compose up -d storage storage-setup
```

`storage-setup` crea el bucket y termina; es normal que quede en estado `Exited (0)`. Ver [storage.md](storage.md).

## 4. Ejecutar la API

Desde `virtual-catalog-api/`:

```bash
uvicorn app.infrastructure.api.main:app --reload
```

- API: http://localhost:8000/api/v1
- Swagger: http://localhost:8000/docs

`--reload` reinicia el servidor cuando cambias el código. Las tablas se crean solas en la primera petición (ver [database.md](database.md)).

## 5. Cargar datos de prueba

```bash
python seed.py
```

Ver [seed.md](seed.md).

## 6. Tests

```bash
pytest -v
```

Ver [testing.md](testing.md).

## Imagen Docker

`Dockerfile`:

- Base `python:3.12-slim`, con dependencias instaladas desde `requirements.txt` en una capa propia, para aprovechar la caché.
- Copia el código, incluidas `static/` (las usa el seed); `.dockerignore` excluye `.env`, `data/`, `.venv/` y cachés.
- Ejecuta `uvicorn app.infrastructure.api.main:app --host 0.0.0.0 --port 8000`, sin `--reload`.

Normalmente se construye desde la raíz con `docker compose up -d --build`. También se puede construir aislada:

```bash
docker build -t virtual-catalog-api .
```

## Problemas comunes

| Síntoma | Causa y solución |
| --- | --- |
| `ValidationError ... Field required` al arrancar | Falta una variable en el `.env`. El mensaje dice cuál. |
| `ValidationError` en `cors_origins` | `CORS_ORIGINS` no es una lista JSON válida. Usa `["http://localhost:4321"]`. |
| `ModuleNotFoundError: No module named 'bcrypt'` (u otro) | Las dependencias no están instaladas en el Python activo. Activa el `.venv` y ejecuta `pip install -r requirements.txt`. |
| `500` al crear artículos o en el seed: `Error al subir la imagen al almacenamiento S3` | RustFS no está levantado, o el bucket o las credenciales no coinciden. |
| Las imágenes no cargan en el navegador | `S3_PUBLIC_URL` no es accesible desde el navegador, o las URLs guardadas son de otra configuración: vuelve a ejecutar el seed. |
| Error de CORS en el navegador | El origen del frontend no está en `CORS_ORIGINS`. |
| `Address already in use` en el puerto 8000 | Ya hay otra instancia de la API corriendo (por ejemplo, el contenedor `api`). Detenla con `docker compose stop api`. |

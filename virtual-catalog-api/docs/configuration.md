# Configuración

La configuración está centralizada en la clase `Settings` de `app/infrastructure/config.py`, construida con **pydantic-settings**.

## Cómo funciona

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_ignore_empty=True,
        extra="ignore",
        hide_input_in_errors=True,
    )
    database_path: str
    cors_origins: List[str]
    ...

settings = Settings()
```

- **Sin valores por defecto**: todas las variables son obligatorias, salvo `STRIPE_SECRET_KEY`. Si falta alguna, la aplicación **no arranca** y pydantic indica cuál falta:
  ```
  pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
  s3_bucket
    Field required [type=missing]
  ```
- **Origen de los valores**, de mayor a menor prioridad:
  1. Variables de entorno del proceso (en Docker, las del `environment:` y `env_file:` del compose).
  2. El archivo `virtual-catalog-api/.env`.
- **El `.env` se encuentra siempre**: se busca con una ruta absoluta (`BASE_DIR / ".env"`), así que funciona aunque ejecutes la API desde otra carpeta.
- **Variables vacías** (`VAR=`) se tratan como no definidas (`env_ignore_empty`), así que un `.env` copiado de `.env.example` sin completar falla de forma clara.
- **Nombres**: no distinguen mayúsculas; `DATABASE_PATH` en el entorno corresponde a `database_path` en la clase.
- **Secretos ocultos**: `hide_input_in_errors=True` evita que los errores de validación muestren los valores leídos.
- `settings` se crea **al importar** el módulo. `main.py` y `seed.py` lo importan; los tests no.

`BASE_DIR` es la carpeta raíz de la API: `virtual-catalog-api/` en local y `/app` en el contenedor.

## Variables

Plantilla: [`.env.example`](../.env.example).

| Variable | Descripción | Ejemplo local |
| --- | --- | --- |
| `DATABASE_PATH` | Archivo SQLite. Si es relativo, se resuelve desde `BASE_DIR` y se crea la carpeta | `data/catalogo.db` |
| `CORS_ORIGINS` | Orígenes permitidos por CORS, **como lista JSON** | `["http://localhost:4321"]` |
| `S3_ENDPOINT` | URL con la que la API se conecta a RustFS | `http://localhost:9000` |
| `S3_PUBLIC_URL` | URL base de las imágenes para el navegador | `http://localhost:9000` |
| `S3_ACCESS_KEY` | Usuario de RustFS | `admin` |
| `S3_SECRET_KEY` | Contraseña de RustFS | `password123` |
| `S3_BUCKET` | Bucket de imágenes | `catalogo-images` |
| `PAYMENT_GATEWAY_PROVIDER` | `mock` o `stripe` | `mock` |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe (opcional; solo si el proveedor es `stripe`) | `sk_test_...` |

`CORS_ORIGINS` debe ser JSON válido porque es una lista: `["http://localhost:4321","http://127.0.0.1:4321"]`.

> **Nombres antiguos.** Hasta el cambio de MinIO a RustFS estas variables se llamaban `MINIO_ENDPOINT`, `MINIO_PUBLIC_URL`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` y `MINIO_BUCKET`. Los nombres antiguos ya no se leen (`extra="ignore"`): si tu `.env` todavía los usa, la API no arranca y pydantic indica `s3_endpoint Field required`. Renómbralos con el prefijo `S3_`; los valores no cambian.

## Valores en Docker

El `docker-compose.yml` de la raíz carga `virtual-catalog-api/.env` (`env_file`) y **sobrescribe** solo lo que cambia dentro de la red de Docker:

| Variable | Valor en Docker | Por qué |
| --- | --- | --- |
| `S3_ENDPOINT` | `http://storage:9000` | Dentro del contenedor, `localhost` es el propio contenedor |
| `S3_PUBLIC_URL` | `http://localhost:9000` | El navegador accede por el puerto publicado en el host |
| `CORS_ORIGINS` | `["http://localhost:4321"]` | Origen del frontend publicado por el compose |

`DATABASE_PATH` no se sobrescribe: el mismo valor relativo (`data/catalogo.db`) apunta a `/app/data/catalogo.db`, donde se monta el volumen `api_data`.

El `.env` **no** se copia a la imagen (`.dockerignore`); llega al contenedor solo como variables de entorno.

## Agregar una variable

1. Declararla en `Settings` con su tipo; si es opcional, con un valor por defecto.
2. Agregarla, vacía y con un comentario, a `.env.example`.
3. Si cambia dentro de Docker, sobrescribirla en `environment:` del servicio `api` en el `docker-compose.yml`.
4. Usarla con `from app.infrastructure.config import settings`.

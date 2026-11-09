# Virtual Catalog API

API REST del catálogo virtual de zapatos: registro e inicio de sesión de usuarios, catálogo con búsqueda, carrito de compras, checkout y pagos.

**Stack:** Python 3.12 · FastAPI · SQLite · MinIO (S3, imágenes) · Stripe (pagos) · pytest

Arquitectura hexagonal (puertos y adaptadores) con dominio, aplicación e infraestructura separados.

## Inicio rápido (local)

```bash
cp .env.example .env                      # y completar los valores (ver docs/configuration.md)
pip install -r requirements.txt           # idealmente dentro de un .venv
docker compose up -d minio minio-setup    # desde la raíz del monorepo
uvicorn app.infrastructure.api.main:app --reload
python seed.py                            # 20 artículos de prueba
```

- API: http://localhost:8000/api/v1
- Documentación interactiva (Swagger): http://localhost:8000/docs
- Tests: `pytest -v`

Para levantar todo el stack (MinIO + API + web) con Docker, consulta el [README de la raíz](../README.md).

## Documentación

| Documento | Contenido |
| --- | --- |
| [Arquitectura](docs/architecture.md) | Capas, estructura de carpetas, puertos y adaptadores, inyección de dependencias y recorrido de una petición |
| [Modelo de dominio](docs/domain.md) | Agregados, value objects, reglas de negocio, estados de pedidos y pagos, casos de uso |
| [Referencia de la API](docs/api-reference.md) | Endpoints, cuerpos de petición y respuesta, ejemplos |
| [Base de datos](docs/database.md) | Esquema SQLite, repositorios y mappers, conexiones y transacciones |
| [Pagos](docs/payments.md) | Puerto `PaymentGateway`, adaptadores Mock y Stripe, flujo de cobro |
| [Almacenamiento (MinIO)](docs/storage.md) | Subida de imágenes, bucket, endpoint interno y URL pública |
| [Seguridad](docs/security.md) | bcrypt, JWT, estado de la autorización, middleware CORS |
| [Validación y errores](docs/errors-and-validation.md) | Validación con Pydantic y en el dominio, manejadores de excepciones, formatos de error |
| [Configuración](docs/configuration.md) | `Settings` con pydantic-settings, variables de entorno, valores en Docker |
| [Datos de prueba (seed)](docs/seed.md) | Qué carga `seed.py` y cómo ejecutarlo |
| [Tests](docs/testing.md) | Organización, cómo están construidos, cómo ejecutarlos, cobertura |
| [Desarrollo local](docs/development.md) | Instalación, ejecución, imagen Docker, problemas comunes |
| [Limitaciones conocidas](docs/known-issues.md) | Bugs y deudas técnicas identificadas en el código |

**Orden de lectura sugerido:** arquitectura → dominio → referencia de la API. El resto, según lo que necesites tocar.

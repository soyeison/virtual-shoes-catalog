# Proyecto de catalogo virtual de zapatos

Monorepo con:

- `virtual-catalog-api/`: API en FastAPI (SQLite + MinIO).
- `shoes-web-app/`: frontend en Astro + React (SSR con `@astrojs/node`).

## Ejecutar todo con Docker

1. Configurar las variables del backend:

   ```bash
   cp virtual-catalog-api/.env.example virtual-catalog-api/.env
   # completar los valores en virtual-catalog-api/.env
   ```

   El `docker-compose.yml` sobrescribe las variables que cambian dentro de la red de Docker
   (`CORS_ORIGINS`, `MINIO_ENDPOINT`, `MINIO_PUBLIC_URL`).

2. Levantar los servicios desde la raíz:

   ```bash
   docker compose up -d --build
   ```

3. Poblar la base de datos y MinIO con los primeros 20 artículos:

   ```bash
   docker compose exec api python seed.py
   ```

| Servicio      | URL                         |
| ------------- | --------------------------- |
| Web           | http://localhost:4321       |
| API (docs)    | http://localhost:8000/docs  |
| Consola MinIO | http://localhost:9001       |

Para detener todo: `docker compose down` (los datos se conservan en volúmenes).

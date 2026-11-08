Primero se deben configurar las variables de entorno: cp .env.example .env (y completar los valores)

Luego se levanta MinIO desde la raíz del monorepo: docker compose up -d minio minio-setup

Comando para ejecutar la API: uvicorn app.infrastructure.api.main:app --reload

Para ejecutar pruebas se usa: pytest -v

Para ejecutar la semilla con los primeros 20 articulos: python seed.py

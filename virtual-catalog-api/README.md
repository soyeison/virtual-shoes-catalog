Primero se debe ejecutar el comando: docker compose up -d

Comando para ejecutar la API: uvicorn app.infrastructure.api.main:app --reload

Para ejecutar pruebas se usa: pytest -v

Para ejecutar la semilla con los primeros 20 articulos: python seed.py

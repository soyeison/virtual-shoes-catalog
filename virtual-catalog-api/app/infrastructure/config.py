from pathlib import Path
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raíz del proyecto de la API (virtual-catalog-api/ en local, /app en el contenedor)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuración de la aplicación leída desde variables de entorno o el archivo .env.

    No hay valores por defecto: si falta una variable obligatoria, la aplicación
    falla al arrancar indicando cuál es. Ver .env.example.
    """

    # Las variables vacías (VAR=) se tratan como no definidas
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_ignore_empty=True,
        extra="ignore",
        hide_input_in_errors=True,  # Evita mostrar secretos en los errores
    )

    # Base de datos (las rutas relativas se resuelven desde BASE_DIR)
    database_path: str

    # CORS (lista JSON, ej: ["http://localhost:4321"])
    cors_origins: List[str]

    # MinIO
    minio_endpoint: str  # URL que usa la API para subir archivos
    minio_public_url: str  # URL base con la que el navegador descarga las imágenes
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str

    # Pagos
    payment_gateway_provider: str
    stripe_secret_key: Optional[str] = None  # Solo requerida si el proveedor es "stripe"

    @field_validator("database_path")
    @classmethod
    def resolve_database_path(cls, value: str) -> str:
        path = Path(value)
        if not path.is_absolute():
            path = BASE_DIR / path
        # SQLite crea el archivo pero no las carpetas intermedias
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)


settings = Settings()

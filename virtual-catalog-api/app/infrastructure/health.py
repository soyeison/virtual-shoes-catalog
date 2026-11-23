import logging
import sqlite3

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.infrastructure.repositories.sqlite_article_repository import (
    SqliteArticleRepository,
)

logger = logging.getLogger(__name__)

# Un health check debe responder rápido: sin esto boto3 espera hasta 60 s y reintenta
STORAGE_HEALTH_CONFIG = Config(
    connect_timeout=2,
    read_timeout=2,
    retries={"mode": "standard", "total_max_attempts": 1},
)


def build_storage_health_client(
    endpoint_url: str, access_key: str, secret_key: str, region_name: str
):
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
        config=STORAGE_HEALTH_CONFIG,
    )


def check_database(connection: sqlite3.Connection) -> bool:
    # sqlite3.connect crea el archivo si no existe, así que conectar no prueba nada:
    # se crea la tabla si falta (prueba escritura) y se lee de ella (prueba lectura)
    try:
        SqliteArticleRepository(connection)
        connection.execute("SELECT 1 FROM articles LIMIT 1").fetchall()
        return True
    except sqlite3.Error as e:
        logger.warning("Health: la base de datos no responde: %s", e)
        return False


def check_storage(s3_client, bucket_name: str) -> bool:
    # head_bucket valida conexión, credenciales y que el bucket exista
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except (BotoCoreError, ClientError) as e:
        logger.warning("Health: el almacenamiento no responde: %s", e)
        return False

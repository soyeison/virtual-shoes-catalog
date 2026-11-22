import sqlite3

from botocore.exceptions import ClientError, EndpointConnectionError

from app.infrastructure.health import (
    build_storage_health_client,
    check_database,
    check_storage,
)


class FakeS3Client:
    def __init__(self, error: Exception = None):
        self.error = error
        self.checked_buckets = []

    def head_bucket(self, Bucket: str):
        self.checked_buckets.append(Bucket)
        if self.error:
            raise self.error


def test_check_database_ok_on_fresh_database():
    # En una base nueva la tabla aún no existe: la comprobación debe crearla
    connection = sqlite3.connect(":memory:")

    assert check_database(connection) is True


def test_check_database_fails_when_connection_is_unusable():
    connection = sqlite3.connect(":memory:")
    connection.close()

    assert check_database(connection) is False


def test_check_storage_ok_when_bucket_exists():
    client = FakeS3Client()

    assert check_storage(client, "catalogo-images") is True
    assert client.checked_buckets == ["catalogo-images"]


def test_check_storage_fails_when_bucket_is_missing():
    error = ClientError({"Error": {"Code": "404"}}, "HeadBucket")

    assert check_storage(FakeS3Client(error), "catalogo-images") is False


def test_check_storage_fails_when_storage_is_unreachable():
    error = EndpointConnectionError(endpoint_url="http://storage:9000")

    assert check_storage(FakeS3Client(error), "catalogo-images") is False


def test_storage_health_client_fails_fast():
    client = build_storage_health_client(
        endpoint_url="http://storage:9000", access_key="key", secret_key="secret"
    )

    assert client.meta.config.connect_timeout == 2
    assert client.meta.config.read_timeout == 2
    assert client.meta.config.retries["total_max_attempts"] == 1

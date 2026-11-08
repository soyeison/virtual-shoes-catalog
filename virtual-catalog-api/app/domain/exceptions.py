class DomainException(Exception):
    """Clase base para todas las excepciones lógicas del negocio."""

    pass


class InvalidCredentialsException(DomainException):
    pass

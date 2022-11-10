class NotFoundError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseIntegrityError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

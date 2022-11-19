# -*- coding: utf-8 -*-
from __future__ import annotations

from common.errors import DatabaseIntegrityError, NotFoundError


class UserNotFoundByIdError(NotFoundError):
    def __init__(self, id: str) -> None:
        super().__init__(f"User(id={id!r}) not found")


class UserNotFoundByEmailError(NotFoundError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User({email=!r}) not found")


class CannotCreateUserError(DatabaseIntegrityError):
    def __init__(self, name: str, email: str) -> None:
        super().__init__(f"Cannot create User({name=!r}, {email=!r})")


class UserNotLoggedInError(DatabaseIntegrityError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User(id={user_id!r}) is not yet logged in")


class NotExistUserError(DatabaseIntegrityError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User(id={user_id!r}) is not exist")


class InvalidUserSessionError(DatabaseIntegrityError):
    def __init__(self, session_id: str) -> None:
        super().__init__(f"UserSession({session_id=!r}) is invalid value")


class SessionAlreadyExistError(DatabaseIntegrityError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User(id={user_id!r}) has already a session")

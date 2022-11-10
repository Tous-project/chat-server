# -*- coding: utf-8 -*-
from __future__ import annotations

from common.errors import DatabaseIntegrityError, NotFoundError


class UserNotFoundByIdError(NotFoundError):
    def __init__(self, id: str) -> None:
        super().__init__(f"User(id={id!r}) not found")


class CannotCreateUserError(DatabaseIntegrityError):
    def __init__(self, name: str, email: str) -> None:
        super().__init__(f"Cannot create User({name=!r}, {email=!r})")

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterator

from .errors import (
    InvalidUserSessionError,
    SessionAlreadyExistError,
    UserNotLoggedInError,
)
from .models import User, UserSession
from .repository import UserRepository, UserSessionRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository = user_repository

    def get_all(self) -> Iterator[User]:
        return self._repository.get_all()

    def get_by_id(self, id: int) -> User:
        return self._repository.get(id=id)

    def create(self, name: str, email: str, password: str) -> User:
        return self._repository.create(name=name, email=email, password=password)

    def delete_by_id(self, id: int) -> None:
        return self._repository.delete(id=id)


class UserSessionService:
    def __init__(self, user_session_repository: UserSessionRepository):
        self._repository = user_session_repository

    def get_by_user_id(self, user_id: int) -> UserSession:
        return self._repository.get_by_user_id(user_id=user_id)

    def get_by_session_id(self, session_id: str) -> UserSession:
        return self._repository.get_by_session_id(session_id=session_id)

    def create(self, user_id: int) -> UserSession:
        is_exist = self._repository.get_by_user_id(user_id=user_id)
        if is_exist:
            raise SessionAlreadyExistError(user_id)
        return self._repository.create(user_id=user_id)

    def delete_by_session_id(self, session_id: str) -> None:
        is_exist = self._repository.get_by_session_id(session_id=session_id)
        if not is_exist:
            raise InvalidUserSessionError(session_id)
        return self._repository.delete_by_session_id(session_id=session_id)

    def delete_all(self, user_id: int) -> None:
        is_exist = self._repository.get_all(user_id=user_id)
        if not is_exist:
            raise UserNotLoggedInError(user_id=user_id)
        return self._repository.delete_all(user_id=user_id)

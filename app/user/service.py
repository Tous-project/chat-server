# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterator

from user.models import User
from user.repository import UserRepository


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

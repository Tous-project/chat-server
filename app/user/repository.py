# -*- coding: utf-8 -*-
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from user.errors import CannotCreateUserError, UserNotFoundByIdError
from user.models import User


class UserRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def get_all(self) -> Iterator[User]:
        with self.session_factory() as session:
            return session.query(User).all()

    def get(self, id: int) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == id).first()
            if not user:
                raise UserNotFoundByIdError(id)
            return user

    def create(self, name: str, email: str, password: str) -> User:
        try:
            with self.session_factory() as session:
                user = User(name=name, email=email, password=password)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        except IntegrityError:
            raise CannotCreateUserError(name=name, email=email)

    def delete(self, id: int) -> None:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == id).first()
            if not user:
                raise UserNotFoundByIdError(id)
            session.delete(user)
            session.commit()

# -*- coding: utf-8 -*-
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from user.errors import (
    CannotCreateUserError,
    InvalidUserSessionError,
    NotExistUserError,
    UserNotFoundByEmailError,
    UserNotFoundByIdError,
)
from user.models import User, UserSession


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

    def get_by_email(self, email: str) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                raise UserNotFoundByEmailError(email)
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


class UserSessionRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def get_by_user_id(self, user_id: int) -> UserSession:
        with self.session_factory() as session:
            return (
                session.query(UserSession).filter(UserSession.user_id == user_id).first()
            )

    def get_by_session_id(self, session_id: str) -> UserSession:
        with self.session_factory() as session:
            return (
                session.query(UserSession)
                .filter(UserSession.session_id == session_id)
                .first()
            )

    def get_all(self, user_id: int) -> UserSession:
        with self.session_factory() as session:
            return session.query(UserSession).filter(UserSession.user_id == user_id).all()

    def create(self, user_id: int) -> UserSession:
        try:
            with self.session_factory() as session:
                new_user_session = UserSession(user_id=user_id)
                session.add(new_user_session)
                session.commit()
                session.refresh(new_user_session)
                return new_user_session
        except IntegrityError:
            raise NotExistUserError(user_id)

    def delete_by_session_id(self, session_id: str) -> None:
        with self.session_factory() as session:
            user_session = (
                session.query(UserSession)
                .filter(UserSession.session_id == session_id)
                .first()
            )
            if not user_session:
                raise InvalidUserSessionError(session_id)
            session.delete(user_session)
            session.commit()

    def delete_all(self, user_id) -> None:
        with self.session_factory() as session:
            all_user_sessions = self.get_all(user_id=user_id)
            for user_session in all_user_sessions:
                session.delete(user_session)
            session.commit()

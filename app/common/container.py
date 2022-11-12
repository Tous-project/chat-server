# -*- coding: utf-8 -*-
from __future__ import annotations

from common.conf import config
from common.database import PostgreSQL
from dependency_injector import containers, providers
from user.repository import UserRepository, UserSessionRepository
from user.service import UserService, UserSessionService


class DatabaseContainer(containers.DeclarativeContainer):
    cfg = config("db")

    postgres = providers.Singleton(
        PostgreSQL, host=cfg.host, id=cfg.id, name=cfg.name, password=cfg.password
    )


class RepositoryContainer(containers.DeclarativeContainer):
    db = providers.DependenciesContainer()

    user = providers.Factory(UserRepository, session_factory=db.postgres.provided.session)

    user_session = providers.Factory(
        UserSessionRepository, session_factory=db.postgres.provided.session
    )


class ServiceContainer(containers.DeclarativeContainer):
    repository = providers.DependenciesContainer()

    user = providers.Factory(UserService, user_repository=repository.user)

    user_session = providers.Factory(
        UserSessionService, user_session_repository=repository.user_session
    )


class ApplicationContainer(containers.DeclarativeContainer):
    cfg = config("db")

    db = providers.Container(DatabaseContainer)

    repository = providers.Container(RepositoryContainer, db=db)

    service = providers.Container(ServiceContainer, repository=repository)

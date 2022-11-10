# -*- coding: utf-8 -*-
from __future__ import annotations

from common.conf import config
from common.database import PostgreSQL
from dependency_injector import containers, providers
from user.repository import UserRepository
from user.service import UserService


class DatabaseContainer(containers.DeclarativeContainer):
    cfg = config("db")

    postgres = providers.Singleton(
        PostgreSQL, host=cfg.host, id=cfg.id, name=cfg.name, password=cfg.password
    )


class RepositoryContainer(containers.DeclarativeContainer):
    db = providers.DependenciesContainer()

    user = providers.Factory(UserRepository, session_factory=db.postgres.provided.session)


class ServiceContainer(containers.DeclarativeContainer):
    repository = providers.DependenciesContainer()

    user = providers.Factory(UserService, user_repository=repository.user)


class ApplicationContainer(containers.DeclarativeContainer):
    cfg = config("db")

    db = providers.Container(DatabaseContainer)

    repository = providers.Container(RepositoryContainer, db=db)

    service = providers.Container(ServiceContainer, repository=repository)

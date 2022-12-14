# -*- coding: utf-8 -*-
from __future__ import annotations

from chat.pubsub import ChatServer
from chat.repository import ChatRoomMemberRepository, ChatRoomRepository
from chat.service import ChatRoomMemberService, ChatRoomService
from common.conf import PostgreSQLConfig, RedisConfig
from common.database import PostgreSQL
from dependency_injector import containers, providers
from user.repository import UserRepository, UserSessionRepository
from user.service import UserService, UserSessionService


class RedisContainer(containers.DeclarativeContainer):
    cfg = RedisConfig()

    chat_server = providers.Factory(ChatServer, dsn=cfg.DSN)


class DatabaseContainer(containers.DeclarativeContainer):
    cfg = PostgreSQLConfig()

    postgres = providers.Singleton(PostgreSQL, dsn=cfg.DSN)


class RepositoryContainer(containers.DeclarativeContainer):
    db = providers.DependenciesContainer()

    user = providers.Factory(UserRepository, session_factory=db.postgres.provided.session)

    user_session = providers.Factory(
        UserSessionRepository, session_factory=db.postgres.provided.session
    )

    chat_room = providers.Factory(
        ChatRoomRepository, session_factory=db.postgres.provided.session
    )

    chat_room_member = providers.Factory(
        ChatRoomMemberRepository, session_factory=db.postgres.provided.session
    )


class ServiceContainer(containers.DeclarativeContainer):
    repository = providers.DependenciesContainer()

    user = providers.Factory(UserService, user_repository=repository.user)

    user_session = providers.Factory(
        UserSessionService, user_session_repository=repository.user_session
    )

    chat_room = providers.Factory(
        ChatRoomService,
        chat_room_repository=repository.chat_room,
        chat_room_member_repository=repository.chat_room_member,
    )

    chat_room_member = providers.Factory(
        ChatRoomMemberService,
        chat_room_member_repository=repository.chat_room_member,
        chat_room_repository=repository.chat_room,
    )


class ApplicationContainer(containers.DeclarativeContainer):
    db = providers.Container(DatabaseContainer)

    redis = providers.Container(RedisContainer)

    repository = providers.Container(RepositoryContainer, db=db)

    service = providers.Container(ServiceContainer, repository=repository)

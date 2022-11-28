# -*- coding: utf-8 -*-
from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from user.models import User

from .errors import (
    CannotCreateChatRoomError,
    CannotJoinChatRoomError,
    ChatRoomNotFoundByIdError,
    UserIsNotChatRoomMemberError,
)
from .models import ChatRoom, ChatRoomMember


class ChatRoomRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def get_all(self) -> Iterator[ChatRoom]:
        with self.session_factory() as session:
            return session.query(ChatRoom).all()

    def get_all_members(self, room_id: int) -> Iterator[User]:
        with self.session_factory() as session:
            room = session.query(ChatRoom).filter(ChatRoom.id == room_id).first()
            return iter([member.user for member in room.members])

    def get_all_joined_room(self, user_id: int) -> Iterator[ChatRoom]:
        with self.session_factory() as session:
            joined_rooms = (
                session.query(ChatRoomMember)
                .filter(ChatRoomMember.user_id == user_id)
                .all()
            )
            return iter([joined.room for joined in joined_rooms])

    def get_by_id(self, room_id: int) -> ChatRoom:
        with self.session_factory() as session:
            return session.query(ChatRoom).filter(ChatRoom.id == room_id).first()

    def get_by_name(self, name: str) -> ChatRoom:
        with self.session_factory() as session:
            return session.query(ChatRoom).filter(ChatRoom.name == name).first()

    def create(self, owner: int, name: str, description: str = None) -> ChatRoom:
        try:
            with self.session_factory() as session:
                new_room = ChatRoom(owner=owner, name=name, description=description)
                session.add(new_room)
                session.commit()
                session.refresh(new_room)
                return new_room
        except IntegrityError:
            raise CannotCreateChatRoomError(name=name)

    def delete_by_room_id(self, room_id: int) -> None:
        with self.session_factory() as session:
            room = session.query(ChatRoom).filter(ChatRoom.id == room_id).first()
            if not room:
                raise ChatRoomNotFoundByIdError(room_id=room_id)
            session.delete(room)
            session.commit()


class ChatRoomMemberRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def get_all_by_room_id(self, room_id: int) -> Iterator[ChatRoomMember]:
        with self.session_factory() as session:
            return (
                session.query(ChatRoomMember)
                .filter(ChatRoomMember.room_id == room_id)
                .all()
            )

    def get_all_by_user_id(self, user_id: int) -> Iterator[ChatRoomMember]:
        with self.session_factory() as session:
            return (
                session.query(ChatRoomMember)
                .filter(ChatRoomMember.user_id == user_id)
                .all()
            )

    def create(self, room_id: int, user_id: int) -> ChatRoomMember:
        try:
            with self.session_factory() as session:
                joined_new_member = ChatRoomMember(room_id=room_id, user_id=user_id)
                session.add(joined_new_member)
                session.commit()
                session.refresh(joined_new_member)
                return joined_new_member
        except IntegrityError:
            raise CannotJoinChatRoomError(room_id=room_id, user_id=user_id)

    def delete_by_user_id(self, room_id: int, user_id: int) -> None:
        with self.session_factory() as session:
            joined_member = (
                session.query(ChatRoomMember)
                .filter(
                    ChatRoomMember.room_id == room_id, ChatRoomMember.user_id == user_id
                )
                .first()
            )
            if not joined_member:
                raise UserIsNotChatRoomMemberError(room_id=room_id, user_id=user_id)
            session.delete(joined_member)
            session.commit()

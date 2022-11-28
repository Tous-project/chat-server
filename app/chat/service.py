# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from fastapi.encoders import jsonable_encoder
from rich import inspect
from user.models import User as UserModel
from user.response import User

from .const import MessageReceiverType, MessageType
from .errors import (
    AlreadyJoinedError,
    ChatRoomAlreadyExistError,
    ChatRoomNotFoundByIdError,
    UserIsNotChatRoomMemberError,
)
from .message import BaseMessage, SystemMessage
from .models import ChatRoom, ChatRoomMember
from .repository import ChatRoomMemberRepository, ChatRoomRepository
from .socket_handler import SocketHandler


class ChatRoomService:
    __instance: Optional[ChatRoomService] = None
    rooms: Dict[int, List[SocketHandler]] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> ChatRoomService:
        if not isinstance(cls.__instance, cls):
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(
        self,
        chat_room_repository: ChatRoomRepository,
        chat_room_member_repository: ChatRoomMemberRepository,
    ) -> None:
        self._repository = chat_room_repository
        self._member_repository = chat_room_member_repository
        self = self.update()

    def update(self) -> ChatRoomService:
        old_rooms = self.__instance.rooms
        new_rooms = self.get_all()
        self.__instance.rooms = dict.fromkeys([room.id for room in new_rooms], [])
        self.__instance.rooms.update(old_rooms)
        return self.__instance

    def get_all(self) -> Iterator[ChatRoom]:
        return self._repository.get_all()

    def get_by_id(self, room_id: int) -> ChatRoom:
        return self._repository.get_by_id(room_id=room_id)

    def get_by_name(self, name: str) -> ChatRoom:
        return self._repository.get_by_name(name=name)

    def create(self, owner: int, name: str, description: str) -> ChatRoom:
        is_exist = self.get_by_name(name=name)
        if is_exist:
            raise ChatRoomAlreadyExistError(name=name, description=description)
        return self._repository.create(owner=owner, name=name, description=description)

    def delete_by_id(self, room_id: int) -> None:
        is_exist = self.get_by_id(room_id=room_id)
        if not is_exist:
            raise ChatRoomNotFoundByIdError(room_id=room_id)
        return self._repository.delete_by_room_id(room_id=room_id)

    def get_all_joined_chat_rooms(self, user_id: int) -> Iterator[ChatRoom]:
        return self._repository.get_all_joined_room(user_id=user_id)

    def get_all_joined_members(self, room_id: int) -> Iterator[UserModel]:
        return self._repository.get_all_members(room_id=room_id)

    def join(self, room_id: int, user: User) -> None:
        if self.is_member(room_id=room_id, user=user):
            raise AlreadyJoinedError(room_id=room_id, user_id=user.id)
        self._member_repository.create(room_id=room_id, user_id=user.id)

    async def leave(self, room_id: int, user: SocketHandler) -> None:
        if self.is_member(room_id=room_id, user=user.user):
            raise UserIsNotChatRoomMemberError(room_id=room_id, user_id=user.user_id)
        self.exit(room_id=room_id, user=user)
        leave_msg = SystemMessage(
            text=f"{user.user_name!r}님이 퇴장하셨습니다.",
            type=MessageType.NOTIFICATION,
            receiver=MessageReceiverType.USER,
        )
        await self.broadcast(room_id=room_id, message=leave_msg)
        return self._member_repository.delete_by_user_id(
            room_id=room_id, user_id=user.user_id
        )

    def is_member(self, room_id: int, user: User) -> bool:
        members = self._repository.get_all_members(room_id=room_id)
        return any(member.id == user.id for member in members)

    async def enter(self, room_id: int, user: SocketHandler) -> None:
        await user.connect()
        self.__instance.rooms[room_id].append(user)
        welcome_msg = SystemMessage(
            text=f"{user.user_name!r}님이 입장하셨습니다.",
            type=MessageType.NOTIFICATION,
            receiver=MessageReceiverType.USER,
        )
        await self.broadcast(room_id=room_id, message=welcome_msg)

    def exit(self, room_id: int, user: SocketHandler) -> None:
        self.__instance.rooms[room_id].remove(user)

    async def broadcast(self, room_id: int, message: BaseMessage) -> None:
        for user in self.__instance.rooms[room_id]:
            await user.send(jsonable_encoder(message))

    async def send(
        self, room_id: int, sender: SocketHandler, message: BaseMessage
    ) -> None:
        for user in self.__instance.rooms[room_id]:
            if user == sender:
                continue
            await user.send(jsonable_encoder(message))


class ChatRoomMemberService:
    def __init__(
        self,
        chat_room_repository: ChatRoomRepository,
        chat_room_member_repository: ChatRoomMemberRepository,
    ) -> None:
        self._chat_room_repository = chat_room_repository
        self._repository = chat_room_member_repository

    def get_all_joined_chat_rooms(self, user_id: int) -> Iterator[ChatRoom]:
        joined_chat_rooms = self._repository.get_all_by_user_id(user_id)
        chat_room_ids = [chat_room.room_id for chat_room in joined_chat_rooms]
        return iter(
            [
                self._chat_room_repository.get_by_id(room_id=room_id)
                for room_id in chat_room_ids
            ]
        )

    def get_all_joined_members(self, room_id: int) -> Iterator[ChatRoomMember]:
        return self._repository.get_all_by_room_id(room_id=room_id)

    def join(self, room_id: int, user_id: int) -> ChatRoom:
        if self.is_member(room_id=room_id, user_id=user_id):
            raise AlreadyJoinedError(room_id=room_id, user_id=user_id)
        return self._repository.create(room_id=room_id, user_id=user_id)

    def leave(self, room_id: int, user_id: int) -> None:
        if not self.is_member(room_id=room_id, user_id=user_id):
            raise UserIsNotChatRoomMemberError(room_id=room_id, user_id=user_id)
        return self._repository.delete_by_user_id(room_id=room_id, user_id=user_id)

    def is_member(self, room_id: int, user_id: int) -> bool:
        joined_all_members = self.get_all_joined_members(room_id=room_id)
        is_joined = [member.user_id == user_id for member in joined_all_members]
        if any(is_joined):
            return True
        return False


if __name__ == "__main__":
    from common.database import PostgreSQL

    fake_db = PostgreSQL(dsn="postgresql://postgres:1q2w3e4r@localhost:8001/postgres")
    fake_room_repo = ChatRoomRepository(session_factory=fake_db.session)

    with fake_db.session() as session:
        user_id = 1
        joined_rooms = (
            session.query(ChatRoomMember).filter(ChatRoomMember.user_id == user_id).all()
        )
        inspect(joined_rooms)
        inspect([joined.room for joined in joined_rooms])

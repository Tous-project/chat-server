# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterator

from .errors import (
    AlreadyJoinedError,
    ChatRoomAlreadyExistError,
    ChatRoomNotFoundByIdError,
    UserIsNotChatRoomMemberError,
)
from .models import ChatRoom, ChatRoomMember
from .repository import ChatRoomMemberRepository, ChatRoomRepository


class ChatRoomService:
    def __init__(self, chat_room_repository: ChatRoomRepository) -> None:
        self._repository = chat_room_repository

    def get_all(self) -> Iterator[ChatRoom]:
        return self._repository.get_all()

    def get_by_id(self, room_id: int) -> ChatRoom:
        return self._repository.get_by_id(room_id=room_id)

    def get_by_name(self, name: str) -> ChatRoom:
        return self._repository.get_by_name(name=name)

    def create(self, name: str, description: str) -> ChatRoom:
        is_exist = self.get_by_name(name=name)
        if is_exist:
            raise ChatRoomAlreadyExistError(name=name, description=description)
        return self._repository.create(name=name, description=description)

    def delete_by_id(self, room_id: int) -> None:
        is_exist = self.get_by_id(room_id=room_id)
        if not is_exist:
            raise ChatRoomNotFoundByIdError(room_id=room_id)
        return self._repository.delete_by_room_id(room_id=room_id)


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

# -*- coding: utf-8 -*-

from common.errors import DatabaseIntegrityError


class CannotCreateChatRoomError(DatabaseIntegrityError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Can't create ChatRoom({name=!r})")


class ChatRoomNotFoundByIdError(DatabaseIntegrityError):
    def __init__(self, room_id: int) -> None:
        super().__init__(f"ChatRoom(id={room_id!r}) not found")


class CannotJoinChatRoomError(DatabaseIntegrityError):
    def __init__(self, room_id: int, user_id: int) -> None:
        super().__init__(f"User(id={user_id!r}) can't join the ChatRoom(id={room_id!r})")


class UserIsNotChatRoomMemberError(DatabaseIntegrityError):
    def __init__(self, room_id: int, user_id: int) -> None:
        super().__init__(
            f"User(id={user_id!r}) is not member in the ChatRoom(id={room_id!r})"
        )


class AlreadyJoinedError(DatabaseIntegrityError):
    def __init__(self, room_id: int, user_id: int) -> None:
        super().__init__(
            f"User(id={user_id!r}) is already joined the ChatRoom(id={room_id!r})"
        )


class ChatRoomAlreadyExistError(DatabaseIntegrityError):
    def __init__(self, name: str, description: str) -> None:
        super().__init__(f"ChatRoom({name=!r}, {description=!r}) is already exist")

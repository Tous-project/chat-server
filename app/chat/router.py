# -*- coding: utf-8 -*-

import logging
from typing import Union

from chat.socket_handler import SocketHandler
from common.container import ApplicationContainer
from common.response import ErrorResponse
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, Response, WebSocket, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from user.response import User

from .pubsub import ChatServer
from .request import CreateChatRoom
from .service import ChatRoomMemberService, ChatRoomService

from common.authenticate import Session  # isort:skip

logger = logging.getLogger(__name__)
router = APIRouter()
CHAT_ROOM_TAGS = "Chat Room"
CHAT_ROOM_MEMBER_TAGS = "Chat Room Members"


@router.get("/healthz")
async def healthz() -> Response:
    return Response(status_code=status.HTTP_200_OK)


@router.get("/rooms", tags=[CHAT_ROOM_TAGS])
@inject
async def get_all_chat_rooms(
    chat_room: ChatRoomService = Depends(Provide[ApplicationContainer.service.chat_room]),
    x_session_id: str = Header(...),
    current_user: User = Depends(Session.verify),
) -> JSONResponse:
    all_chat_rooms = chat_room.get_all()
    return JSONResponse(jsonable_encoder(all_chat_rooms), status_code=status.HTTP_200_OK)


@router.post("/rooms", tags=[CHAT_ROOM_TAGS])
@inject
async def create_chat_room(
    create_chat_room: CreateChatRoom,
    chat_room: ChatRoomService = Depends(Provide[ApplicationContainer.service.chat_room]),
    x_session_id: str = Header(...),
    current_user: User = Depends(Session.verify),
) -> JSONResponse:
    try:
        new_chat_room = chat_room.create(**create_chat_room.dict())
        chat_room.join(room_id=new_chat_room.id, user=current_user)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't create chat room",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(
        jsonable_encoder(new_chat_room), status_code=status.HTTP_201_CREATED
    )


@router.delete("/rooms/{room_id}", tags=[CHAT_ROOM_TAGS])
@inject
async def delete_chat_room_by_id(
    room_id: int,
    chat_room: ChatRoomService = Depends(Provide[ApplicationContainer.service.chat_room]),
    x_session_id: str = Header(...),
    current_user: User = Depends(Session.verify),
) -> Union[JSONResponse, Response]:
    try:
        chat_room.delete_by_id(room_id=room_id)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't delete chat room",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/rooms/{room_id}/members", tags=[CHAT_ROOM_MEMBER_TAGS])
@inject
async def join_chat_room(
    room_id: int,
    chat_room_member: ChatRoomMemberService = Depends(
        Provide[ApplicationContainer.service.chat_room_member]
    ),
    x_session_id: str = Header(...),
    current_user: User = Depends(Session.verify),
) -> JSONResponse:
    try:
        new_chat_room_member = chat_room_member.join(
            room_id=room_id, user_id=current_user.id
        )
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't join the chat room",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(
        jsonable_encoder(new_chat_room_member), status_code=status.HTTP_200_OK
    )


@router.get("/rooms/{room_id}/members", tags=[CHAT_ROOM_MEMBER_TAGS])
@inject
async def get_all_chat_room_members(
    room_id: int,
    chat_room_service: ChatRoomService = Depends(
        Provide[ApplicationContainer.service.chat_room]
    ),
    x_session_id: str = Header(...),
    current_user: User = Depends(Session.verify),
) -> JSONResponse:
    try:
        all_members = chat_room_service.get_all_joined_members(room_id=room_id)
        users = [User(**member.__dict__) for member in all_members]
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't inquire chat room member",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(jsonable_encoder(users), status_code=status.HTTP_200_OK)


@router.delete("/rooms/{room_id}/members", tags=[CHAT_ROOM_MEMBER_TAGS])
@inject
async def leave_chat_room(
    room_id: int,
    chat_room_member: ChatRoomMemberService = Depends(
        Provide[ApplicationContainer.service.chat_room_member]
    ),
    x_session_id: str = Header(...),
    current_user: Session = Depends(Session.verify),
) -> Union[Response, JSONResponse]:
    try:
        chat_room_member.leave(room_id=room_id, user_id=current_user.id)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't leave chat room",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return Response(status_code=status.HTTP_200_OK)


@router.get("/rooms/me", tags=[CHAT_ROOM_MEMBER_TAGS])
@inject
async def get_all_chat_rooms_i_joined(
    chat_room_service: ChatRoomService = Depends(
        Provide[ApplicationContainer.service.chat_room]
    ),
    x_session_id: str = Header(...),
    current_user: User = Depends(Session.verify),
) -> JSONResponse:
    try:
        joind_all_chat_rooms = chat_room_service.get_all_joined_chat_rooms(
            user_id=current_user.id
        )
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't inquire chat room the user joined",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(
        jsonable_encoder(list(joind_all_chat_rooms)), status_code=status.HTTP_200_OK
    )


@router.websocket("/ws/rooms/{room_id}")
@inject
async def chat_with_other_users(
    socket: WebSocket,
    room_id: int,
    x_session_id: str,
    chat_room_service: ChatRoomService = Depends(
        Provide[ApplicationContainer.service.chat_room],
    ),
    chat_server: ChatServer = Depends(
        Provide[ApplicationContainer.redis.chat_server],
    ),
) -> None:
    current_user = Session.verify_by_session_id(session_id=x_session_id)
    user = SocketHandler(socket=socket, user=current_user)
    channel_name = f"chat:{str(room_id)}"
    if not chat_room_service.is_member(room_id=room_id, user=current_user):
        raise
    await user.connect()

    await chat_server.init(name=channel_name, user_socket=user)
    await chat_server.connect(send_welcome_message=True)

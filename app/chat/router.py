# -*- coding: utf-8 -*-

from typing import Dict, Union

from chat.chatting_room import ChattingRoom
from chat.socket_handler import SocketHandler
from common.container import ApplicationContainer
from common.response import ErrorResponse
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, WebSocket, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from user.service import UserService

from .request import CreateChatRoom
from .service import ChatRoomMemberService, ChatRoomService

router = APIRouter()
CHAT_ROOM_TAGS = "Chat Room"
CHAT_ROOM_MEMBER_TAGS = "Chat Room Members"
chatting_rooms: Dict[str, ChattingRoom] = {}


@router.get("/healthz")
async def healthz() -> JSONResponse:
    return Response(status_code=status.HTTP_200_OK)


@router.get("/rooms", tags=[CHAT_ROOM_TAGS])
@inject
async def get_all_chat_rooms(
    chat_room: ChatRoomService = Depends(Provide[ApplicationContainer.service.chat_room]),
) -> JSONResponse:
    all_chat_rooms = chat_room.get_all()
    return JSONResponse(jsonable_encoder(all_chat_rooms), status_code=status.HTTP_200_OK)


@router.post("/rooms", tags=[CHAT_ROOM_TAGS])
@inject
async def create_chat_room(
    create_chat_room: CreateChatRoom,
    chat_room: ChatRoomService = Depends(Provide[ApplicationContainer.service.chat_room]),
) -> JSONResponse:
    try:
        new_chat_room = chat_room.create(**create_chat_room.dict())
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
    user_id: int,
    chat_room_member: ChatRoomMemberService = Depends(
        Provide[ApplicationContainer.service.chat_room_member]
    ),
) -> JSONResponse:
    try:
        new_chat_room_member = chat_room_member.join(room_id=room_id, user_id=user_id)
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
    chat_room_member: ChatRoomMemberService = Depends(
        Provide[ApplicationContainer.service.chat_room_member]
    ),
    user: UserService = Depends(Provide[ApplicationContainer.service.user]),
) -> JSONResponse:
    try:
        all_chat_room_members = chat_room_member.get_all_joined_members(room_id=room_id)
        user_ids = [user.user_id for user in all_chat_room_members]
        users = [user.get_by_id(id) for id in user_ids]
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't inquire chat room member",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(jsonable_encoder(users), status_code=status.HTTP_200_OK)


@router.get("/members/{user_id}/rooms", tags=[CHAT_ROOM_MEMBER_TAGS])
@inject
async def get_all_chat_rooms_the_user_joined(
    user_id: int,
    chat_room_member: ChatRoomMemberService = Depends(
        Provide[ApplicationContainer.service.chat_room_member]
    ),
) -> JSONResponse:
    try:
        joind_all_chat_rooms = chat_room_member.get_all_joined_chat_rooms(user_id=user_id)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't inquire chat room the user joined",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(
        jsonable_encoder(joind_all_chat_rooms), status_code=status.HTTP_200_OK
    )


@router.websocket("/ws/rooms/{room_id}")
async def enter_chatting_room(socket: WebSocket, room_id: str, username: str):
    if room_id not in chatting_rooms:
        chatting_rooms[room_id] = ChattingRoom()
    room = chatting_rooms[room_id]
    user = SocketHandler(socket, username)
    await room.enter(user)
    try:
        while True:
            recv_data = await user.receive()
            await room.send(sender=user, message=recv_data)
    except WebSocketDisconnect:
        await room.leave(user)

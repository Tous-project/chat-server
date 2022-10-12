# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Response, WebSocket, status, WebSocketDisconnect
from fastapi.responses import JSONResponse

from socket_handler import SocketHandler
from chatting_room import ChattingRoom

router = APIRouter()
chatting_rooms: Dict[str, ChattingRoom] = {}


@router.get("/healthz")
async def healthz() -> JSONResponse:
    return Response(status_code=status.HTTP_200_OK)


@router.websocket("/ws/{room_id}")
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

# -*- coding: utf-8 -*-

from __future__ import annotations

from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from socket_handler import Handler

router = APIRouter()


@router.get("/healthz")
async def healthz() -> JSONResponse:
    return Response(status_code=status.HTTP_200_OK)


@router.websocket("/ws")
async def connect_websocket(socket: WebSocket):
    socket_handler = Handler(socket)
    await socket_handler.connect()
    try:
        while True:
            data = await socket_handler.receive()
            await socket_handler.send(f"Receive: {data}")
    except WebSocketDisconnect:
        await socket_handler.disconnect()

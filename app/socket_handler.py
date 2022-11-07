# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import WebSocket


class SocketHandler:
    socket: WebSocket = None

    def __init__(self, socket: WebSocket, username: str) -> None:
        self.socket = socket
        self.__username = username

    @property
    def username(self) -> str:
        return self.__username

    async def connect(self) -> None:
        if self.socket is None:
            raise ValueError("socket is empty")
        await self.socket.accept()

    async def disconnect(self) -> None:
        await self.socket.close()
        self.socket = None

    async def send(self, text: str) -> None:
        if self.socket is None:
            raise ValueError("socket is empty")
        await self.socket.send_text(text)

    async def receive(self) -> str:
        received = await self.socket.receive_text()
        return received

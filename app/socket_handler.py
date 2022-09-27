# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import WebSocket


class Handler:
    socket: WebSocket = None

    def __init__(self, socket: WebSocket) -> None:
        self.socket = socket

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

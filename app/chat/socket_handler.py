# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional

from fastapi import WebSocket
from user.response import User


class SocketHandler:
    socket: Optional[WebSocket] = None

    def __init__(self, socket: WebSocket, user: User) -> None:
        self.socket = socket
        self.__user = user

    @property
    def user_id(self) -> int:
        return self.__user.id

    @property
    def user(self) -> User:
        return self.__user

    @property
    def user_name(self) -> str:
        return self.__user.name

    @property
    def user_email(self) -> str:
        return self.__user.email

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
        received = await self.socket.receive_json()
        return received

# -*- coding: utf-8 -*-
import asyncio
import json
import logging

import aioredis
from aioredis.client import PubSub, Redis
from fastapi.encoders import jsonable_encoder
from fastapi.websockets import WebSocketDisconnect

from .const import MessageReceiverType, MessageType
from .message import SystemMessage, UserMessage
from .socket_handler import SocketHandler

logger = logging.getLogger(__name__)


class ChatServer:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    async def get_connection_pool(self) -> Redis:
        connection = await aioredis.from_url(
            self.dsn, encoding="utf-8", decode_responses=True
        )
        return connection

    def get_pubsub(self, connection: Redis) -> PubSub:
        return connection.pubsub()

    async def init(self, name: str, user_socket: SocketHandler) -> None:
        self.connection = await self.get_connection_pool()
        self.pubsub = self.get_pubsub(self.connection)
        self.user_socket = user_socket
        self.name = name

    async def publish(self) -> None:
        try:
            while True:
                message = await self.user_socket.receive()
                if message:
                    new_message = UserMessage(**message)
                    await self.connection.publish(
                        self.name, json.dumps(jsonable_encoder(new_message))
                    )
        except WebSocketDisconnect as exc:
            logger.info(f"{self.user_socket.user_name!r} is disconnected")
            logger.debug(f"Disconnect {exc}")

    async def subscribe(self) -> None:
        await self.pubsub.subscribe(self.name)
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    await self.user_socket.send(message["data"])
        except Exception as exc:
            logger.exception(f"Unexpected Exception: {exc}")

    async def connect(self, send_welcome_message: bool) -> None:
        publish_task = self.publish()
        subscribe_task = self.subscribe()

        if send_welcome_message:
            welcome_message = SystemMessage(
                text=f"{self.user_socket.user_name!r}님이 입장하셨습니다.",
                type=MessageType.NOTIFICATION,
                receiver=MessageReceiverType.USER,
            )
            serialized_text = json.dumps(jsonable_encoder(welcome_message))
            await self.connection.publish(self.name, serialized_text)
            await self.user_socket.send(serialized_text)

        done, pending = await asyncio.wait(
            [publish_task, subscribe_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in done:
            logger.debug(f"done task: {task}")

        for task in pending:
            logger.debug(f"pending task: {task}")
            task.cancel()

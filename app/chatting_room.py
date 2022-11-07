import json
from typing import List

from socket_handler import SocketHandler

class ChattingRoom:
    entered_users: List[SocketHandler]

    def __init__(self) -> None:
        self.entered_users = []

    async def enter(self, user: SocketHandler) -> None:
        await user.connect()
        self.entered_users.append(user)
        msg = json.dumps({"action": "enter", "username": user.username})
        await self.broadcast(msg)

    async def leave(self, user: SocketHandler) -> None:
        self.entered_users.remove(user)
        msg = json.dumps({"action": "leave", "username": user.username})
        await self.broadcast(msg)

    async def broadcast(self, message: str, exclude: List[SocketHandler] = []):
        for user in filter(lambda x: x not in exclude, self.entered_users):
            await user.send(message)

    async def send(self, sender: SocketHandler, message: str) -> None:
        for user in filter(lambda x: x != sender, self.entered_users):
            await user.send(message)

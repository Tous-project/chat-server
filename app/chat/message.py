# -*- coding: utf-8 -*-
import time
from typing import Iterable, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from user.response import User

from .const import MessageReceiverType, MessageType


class MessageAction(BaseModel):
    text: str
    target_message_id: Optional[str] = None


class BaseMessage(MessageAction):
    type: MessageType
    sender: User
    receiver: MessageReceiverType
    reader: Iterable[int] = []
    timestamp: float = Field(default=time.time())
    id: str = Field(default=str(uuid4()))


class UserMessage(BaseMessage):
    receiver: MessageReceiverType = MessageReceiverType.USER


class SystemMessage(BaseMessage):
    type: MessageType = MessageType.SYSTEM
    receiver: MessageReceiverType = MessageReceiverType.USER
    sender: User = User(id=0, email="system", name="system")

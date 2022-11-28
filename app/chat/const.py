# -*- coding: utf-8 -*-
from enum import Enum


class MessageType(str, Enum):
    SEND = "send"
    READ = "read"
    NOTIFICATION = "notification"
    SYSTEM = "system"


class MessageReceiverType(str, Enum):
    USER = "user"
    SYSTEM = "system"

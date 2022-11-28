# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class CreateChatRoom(BaseModel):
    owner: int
    name: str
    description: Optional[str]

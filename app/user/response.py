# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class CreatedUser(BaseModel):
    id: int
    email: str
    name: str


class User(CreatedUser):
    pass


class AllUsers(BaseModel):
    users: List[User]

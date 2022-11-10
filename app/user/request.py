# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel


class CreateUser(BaseModel):
    email: str
    password: str
    name: str


class UpdateUser(BaseModel):
    id: str
    password: str
    name: str

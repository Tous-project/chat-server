# -*- coding: utf-8 -*-
from __future__ import annotations

import re

from pydantic import BaseModel, validator


class CreateUser(BaseModel):
    email: str
    password: str
    name: str

    @validator("email")
    def email_validator(cls, value: str) -> str:
        email_regex = r"^[\w\-\.]+@([\w-]+\.)+[\w-]{2,4}$"
        if re.match(email_regex, value):
            return value
        raise ValueError(f"email={value!r} is invalid format")


class UpdateUser(BaseModel):
    id: str
    password: str
    name: str


class LoginUser(BaseModel):
    email: str
    password: str

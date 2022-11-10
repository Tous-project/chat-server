# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error_message: str
    detail: str

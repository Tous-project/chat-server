# -*- coding: utf-8 -*-
from __future__ import annotations

from uuid import uuid4

from common.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(20), unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: uuid4().hex)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return f"UserSession(id={self.id!r}, session_id={self.session_id!r}, user_id={self.user_id!r})"

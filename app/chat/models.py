# -*- coding: utf-8 -*-

from common.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"ChatRoom(id={self.id!r}, name={self.name!r}, description={self.description!r})"


class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return f"ChatRoomMember(id={self.id!r}, room_id={self.room_id!r}, user_id={self.user_id!r})"

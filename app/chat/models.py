# -*- coding: utf-8 -*-

from common.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)

    members = relationship("ChatRoomMember", back_populates="room")

    def __repr__(self) -> str:
        return f"ChatRoom(id={self.id!r}, name={self.name!r}, description={self.description!r})"


class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    room = relationship("ChatRoom", back_populates="members", uselist=False)
    user = relationship("User", back_populates="room", uselist=False)

    def __repr__(self) -> str:
        return f"ChatRoomMember(id={self.id!r}, room_id={self.room_id!r}, user_id={self.user_id!r})"

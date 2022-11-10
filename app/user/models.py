from uuid import uuid4

from sqlalchemy import Column, Integer, String

from common.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(20), unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"

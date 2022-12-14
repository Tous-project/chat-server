# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from contextlib import AbstractContextManager, contextmanager
from typing import Callable, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    def __init__(self, url: str) -> None:
        self._engine = create_engine(url, echo=True)
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine, checkfirst=True)

    @contextmanager
    def session(self) -> Generator[AbstractContextManager[Session], None, None]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception as e:
            logger.exception(f"Session rollback because of {e}")
            session.rollback()
            raise
        finally:
            session.close()


class PostgreSQL(Database):
    def __init__(self, dsn: str) -> None:
        super().__init__(dsn)

# -*- coding: utf-8 -*-
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from starlette.requests import Request
from user.response import User
from user.service import UserService, UserSessionService

from .container import ApplicationContainer


class Session:
    @staticmethod
    @inject
    def verify(
        request: Request,
        user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
        user_session_service: UserSessionService = Depends(
            Provide[ApplicationContainer.service.user_session]
        ),
    ) -> User:
        session_id: str = request.headers.get("x-session-id")
        return Session.verify_by_session_id(
            session_id=session_id,
            user_service=user_service,
            user_session_service=user_session_service,
        )

    @staticmethod
    @inject
    def verify_by_session_id(
        session_id: str,
        user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
        user_session_service: UserSessionService = Depends(
            Provide[ApplicationContainer.service.user_session]
        ),
    ) -> User:
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Required Session id"
            )
        user_session = user_session_service.get_by_session_id(session_id=session_id)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        user = user_service.get_by_id(id=user_session.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in"
            )
        return User(**user.__dict__)

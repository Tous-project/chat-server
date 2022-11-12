# -*- coding: utf-8 -*-
import logging
from typing import Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .errors import CannotCreateUserError, UserNotFoundByIdError
from .request import CreateUser
from .response import AllUsers, CreatedUser, CreatedUserSession, User
from .service import UserService, UserSessionService

from common.container import ApplicationContainer  # isort:skip
from common.response import ErrorResponse  # isort:skip

logger = logging.getLogger(__name__)

router = APIRouter()
USER_TAGS = "User"
USER_SESSION_TAGS = "User Session"


@router.get("/users", response_model=AllUsers, tags=[USER_TAGS])
@inject
def get_user_list(
    user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
) -> JSONResponse:
    all_users = user_service.get_all()
    return JSONResponse(jsonable_encoder(all_users), status_code=status.HTTP_200_OK)


@router.get("/users/{id}", response_model=User, tags=[USER_TAGS])
@inject
def get_user_by_id(
    id: int,
    user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
) -> JSONResponse:
    try:
        user = user_service.get_by_id(id=id)
    except UserNotFoundByIdError:
        error = ErrorResponse(
            error_message="Can't found user",
            detail=f"Doesn't exist data User({id=!r})",
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_404_NOT_FOUND
        )
    return JSONResponse(jsonable_encoder(user), status_code=status.HTTP_200_OK)


@router.post("/users", response_model=CreatedUser, tags=[USER_TAGS])
@inject
def create_user(
    user: CreateUser,
    user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
) -> JSONResponse:
    try:
        new_user = user_service.create(
            name=user.name, email=user.email, password=user.password
        )
    except CannotCreateUserError:
        error = ErrorResponse(
            error_message="Can't create user",
            detail=f"Duplicated data {user.__repr__()}",
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(jsonable_encoder(new_user), status_code=status.HTTP_201_CREATED)


@router.delete("/users/{id}", tags=[USER_TAGS])
@inject
def delete_user_by_id(
    id: int,
    user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
) -> JSONResponse:
    try:
        user_service.delete_by_id(id=id)
    except UserNotFoundByIdError:
        error = ErrorResponse(
            error_message="Can't delete user",
            detail=f"Doesn't exist data User({id=!r})",
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_404_NOT_FOUND
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions", response_model=CreatedUserSession, tags=[USER_SESSION_TAGS])
@inject
def create_session(
    user_id: int,
    user_session: UserSessionService = Depends(
        Provide[ApplicationContainer.service.user_session]
    ),
) -> JSONResponse:
    try:
        new_session = user_session.create(user_id=user_id)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't create session",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(
        jsonable_encoder(new_session), status_code=status.HTTP_201_CREATED
    )


@router.delete("/sessions/{session_id}", tags=[USER_SESSION_TAGS])
@inject
def delete_session_by_session_id(
    session_id: str,
    user_session: UserSessionService = Depends(
        Provide[ApplicationContainer.service.user_session]
    ),
) -> Union[Response, JSONResponse]:
    try:
        user_session.delete_by_session_id(session_id=session_id)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't delete session",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/sessions", tags=[USER_SESSION_TAGS])
@inject
def delete_all_sessions(
    user_id: int,
    user_session: UserSessionService = Depends(
        Provide[ApplicationContainer.service.user_session]
    ),
) -> Union[Response, JSONResponse]:
    try:
        user_session.delete_all(user_id=user_id)
    except Exception as exception:
        error = ErrorResponse(
            error_message="Can't delete session",
            detail=exception.__repr__(),
        )
        return JSONResponse(
            jsonable_encoder(error), status_code=status.HTTP_400_BAD_REQUEST
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, Depends, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

from common.container import ApplicationContainer
from common.response import ErrorResponse
from user.service import UserService
from user.request import CreateUser
from user.response import AllUsers, CreatedUser, User
from user.errors import CannotCreateUserError, UserNotFoundByIdError

from rich import inspect
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users", response_model=AllUsers)
@inject
def get_user_list(
    user_service: UserService = Depends(Provide[ApplicationContainer.service.user]),
) -> JSONResponse:
    all_users = user_service.get_all()
    return JSONResponse(jsonable_encoder(all_users), status_code=status.HTTP_200_OK)


@router.get("/users/{id}", response_model=User)
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


@router.post("/users", response_model=CreatedUser)
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


@router.delete("/users/{id}")
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

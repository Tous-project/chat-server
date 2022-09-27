# -*- coding: utf-8 -*-

from __future__ import annotations

from fastapi import APIRouter, status, Response
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/healthz")
async def healthz() -> JSONResponse:
    return Response(status_code=status.HTTP_200_OK)

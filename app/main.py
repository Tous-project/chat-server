# -*- coding: utf-8 -*-

from __future__ import annotations

from os import environ

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.conf import config
from chat.router import router as chat_router

ALLOW_METHOD_LIST = ["GET", "POST", "PATCH", "DELETE"]
ENV = environ.get("ENV", "prod")
reload = ENV == "dev"
cfg = config("server")

app = FastAPI(title="Chat API Server", version="1.0.0")
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=reload)

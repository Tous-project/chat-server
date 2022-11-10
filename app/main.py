# -*- coding: utf-8 -*-

from __future__ import annotations

import uvicorn
from chat.router import router as chat_router
from common.conf import config
from common.container import ApplicationContainer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from user.router import router as user_router

cfg = config("app")


def create_app() -> FastAPI:
    container = ApplicationContainer()

    db = container.db.postgres()
    db.create_database()

    app = FastAPI(title="Chat API Server", version=cfg.version)
    app.container = container
    app.container.wire(modules=["user.router"])
    app.include_router(user_router)
    app.include_router(chat_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)

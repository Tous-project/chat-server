# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi.testclient import TestClient
from main import app


def test_websocket() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws") as socket:
        data = "Hello World"
        socket.send_text(data)
        received = socket.receive_text()
        assert received == f"Receive: {data}"

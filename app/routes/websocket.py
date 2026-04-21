import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def send_personal(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            await self.disconnect(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for ws in disconnected:
            await self.disconnect(ws)


manager = ConnectionManager()


async def notify_login(user_id: int, email: str, role: str):
    await manager.broadcast({
        "event": "LOGIN_SUCCESS",
        "user_id": user_id,
        "email": email,
        "role": role,
        "timestamp": datetime.utcnow().isoformat(),
    })


async def notify_otp_verified(email: str):
    await manager.broadcast({
        "event": "OTP_VERIFIED",
        "email": email,
        "timestamp": datetime.utcnow().isoformat(),
    })


async def notify_franchise_update(action: str, franchise_id: int, name: str):
    await manager.broadcast({
        "event": f"FRANCHISE_{action.upper()}",
        "franchise_id": franchise_id,
        "name": name,
        "timestamp": datetime.utcnow().isoformat(),
    })


@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.send_personal(
            {
                "event": "CONNECTED",
                "message": "Connected to Franchise Management System notifications",
                "timestamp": datetime.utcnow().isoformat(),
            },
            websocket,
        )
        while True:
            # Keep connection alive — receive any client messages (ping/pong)
            data = await websocket.receive_text()
            # Echo heartbeat
            if data == "ping":
                await manager.send_personal({"event": "PONG", "timestamp": datetime.utcnow().isoformat()}, websocket)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

import asyncio
import json
from fastapi import WebSocket
from typing import Dict, Set


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(coro)
    except RuntimeError:
        pass


class ConnectionManager:
    def __init__(self):
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(ws)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_to_user(self, user_id: int, data: dict):
        if user_id not in self.user_connections:
            return
        dead = set()
        for ws in self.user_connections[user_id]:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.user_connections[user_id].discard(ws)
        if user_id in self.user_connections and not self.user_connections[user_id]:
            del self.user_connections[user_id]

    async def broadcast_to_role(self, role_id: int, data: dict, db_session=None):
        if db_session:
            from app.models.user import User
            users = db_session.query(User).filter(User.role_id == role_id, User.is_active == True).all()
            for u in users:
                await self.send_to_user(u.id, data)


manager = ConnectionManager()

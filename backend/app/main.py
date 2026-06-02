from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, users, tickets, messages, evaluations, notifications, rooms, categories, stats, config, uploads, testimonials, faqs
from app.services.reminder_service import start_reminder_service
from app.services.ws_manager import manager
from app.dependencies import get_current_user_ws
from app.database import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_reminder_service()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(messages.router)
app.include_router(evaluations.router)
app.include_router(notifications.router)
app.include_router(rooms.router)
app.include_router(categories.router)
app.include_router(stats.router)
app.include_router(config.router)
app.include_router(uploads.router)
app.include_router(testimonials.router)
app.include_router(faqs.router)


@app.websocket("/api/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(...)):
    user = await get_current_user_ws(token)
    if not user:
        await ws.close(code=4001)
        return
    await manager.connect(user.id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user.id, ws)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

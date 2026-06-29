from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.ws.manager import manager

app = FastAPI(
    title="Optimus Price API",
    version="2.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.websocket("/ws/prices/{hotel_id}")
async def websocket_prices(ws: WebSocket, hotel_id: str):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.websocket("/ws/alerts/{hotel_id}")
async def websocket_alerts(ws: WebSocket, hotel_id: str):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

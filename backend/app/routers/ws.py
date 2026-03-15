from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from ..ws.market_stream import update_active_symbols, fetch_quotes, latest_quotes

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

async def quote_poller():
    """Periodically fetch quotes and broadcast to all clients."""
    while True:
        await fetch_quotes()
        # Broadcast the entire dictionary of quotes to all connected clients
        if latest_quotes:
            await manager.broadcast(json.dumps(latest_quotes))
        await asyncio.sleep(5)  # poll every 5 seconds to avoid rate limiting

@router.on_event("startup")
async def startup():
    # Kick off the two background sync tasks on startup
    asyncio.create_task(update_active_symbols())
    asyncio.create_task(quote_poller())

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Client connects and just listens; ignore incoming chatter
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from collections import defaultdict

from fastapi import WebSocket

from app.metrics.registry import active_websocket_connections


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, station_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[station_id].add(websocket)
        active_websocket_connections.inc()

    def disconnect(self, station_id: str, websocket: WebSocket) -> None:
        if websocket in self._connections[station_id]:
            self._connections[station_id].remove(websocket)
            active_websocket_connections.dec()
        if not self._connections[station_id]:
            self._connections.pop(station_id, None)

    async def broadcast(self, station_id: str, payload: dict) -> None:
        stale: list[WebSocket] = []
        for websocket in self._connections.get(station_id, set()):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(station_id, websocket)

    async def broadcast_many(self, station_ids: list[str], payload: dict) -> None:
        for station_id in station_ids:
            await self.broadcast(station_id, payload)


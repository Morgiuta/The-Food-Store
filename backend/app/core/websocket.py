import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("app.core.websocket")


class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = {}
        self.socket_rooms: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket, roles: list[str], user_id: int) -> None:
        await websocket.accept()

        normalized_roles = self._normalize_roles(roles)
        for role in normalized_roles:
            self._join_room(websocket, self._role_room(role))

        logger.info(
            "WebSocket conectado user_id=%s roles=%s rooms=%s",
            user_id,
            normalized_roles,
            len(self.rooms),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        rooms = self.socket_rooms.pop(websocket, set())
        for room in rooms:
            sockets = self.rooms.get(room)
            if sockets is None:
                continue

            sockets.discard(websocket)
            if not sockets:
                del self.rooms[room]

        logger.info("WebSocket desconectado rooms_liberadas=%s", rooms)

    def join_order_room(self, websocket: WebSocket, order_id: int) -> None:
        self._join_room(websocket, self._order_room(order_id))

    def leave_order_room(self, websocket: WebSocket, order_id: int) -> None:
        self._leave_room(websocket, self._order_room(order_id))

    async def broadcast_to_role(
        self,
        role: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        await self.broadcast_to_rooms([self._role_room(role)], event_type, data)

    async def broadcast_to_roles(
        self,
        roles: list[str],
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        rooms = [self._role_room(role) for role in roles]
        await self.broadcast_to_rooms(rooms, event_type, data)

    async def broadcast_to_order(
        self,
        order_id: int,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        await self.broadcast_to_rooms([self._order_room(order_id)], event_type, data)

    async def broadcast_to_order_and_roles(
        self,
        order_id: int,
        roles: list[str],
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        rooms = [self._order_room(order_id), *(self._role_room(role) for role in roles)]
        await self.broadcast_to_rooms(rooms, event_type, data)

    async def broadcast_to_rooms(
        self,
        rooms: list[str],
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        payload = {"event": event_type, "data": data}
        sent_to: set[WebSocket] = set()

        for room in rooms:
            for connection in list(self.rooms.get(room, set())):
                if connection in sent_to:
                    continue
                try:
                    await connection.send_json(payload)
                    sent_to.add(connection)
                except Exception as exc:
                    logger.warning("Error enviando WebSocket: %s", exc)
                    self.disconnect(connection)

    def get_active_connections_count(self) -> int:
        return len(self.socket_rooms)

    def get_rooms_info(self) -> dict[str, int]:
        return {room: len(sockets) for room, sockets in self.rooms.items()}

    def _join_room(self, websocket: WebSocket, room: str) -> None:
        self.rooms.setdefault(room, set()).add(websocket)
        self.socket_rooms.setdefault(websocket, set()).add(room)

    def _leave_room(self, websocket: WebSocket, room: str) -> None:
        sockets = self.rooms.get(room)
        if sockets is not None:
            sockets.discard(websocket)
            if not sockets:
                del self.rooms[room]

        socket_rooms = self.socket_rooms.get(websocket)
        if socket_rooms is not None:
            socket_rooms.discard(room)

    def _normalize_roles(self, roles: list[str]) -> list[str]:
        normalized = []
        for role in roles:
            role_code = role.strip().upper()
            if role_code and role_code not in normalized:
                normalized.append(role_code)
        return normalized or ["CLIENT"]

    def _role_room(self, role: str) -> str:
        return f"role:{role.strip().upper()}"

    def _order_room(self, order_id: int) -> str:
        return f"order:{order_id}"


manager = ConnectionManager()

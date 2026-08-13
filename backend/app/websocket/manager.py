import json
import logging
from typing import Dict, List, Set, Tuple
from fastapi import WebSocket

logger = logging.getLogger("websocket_manager")

class ConnectionManager:
    def __init__(self):
        # conversation_id -> list of (user_id, WebSocket)
        self.active_conversations: Dict[int, List[Tuple[int, WebSocket]]] = {}
        # user_id -> set of WebSocket connections
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: int, user_id: int):
        await websocket.accept()
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []
        self.active_conversations[conversation_id].append((user_id, websocket))

        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

        logger.info(f"User {user_id} connected to conversation {conversation_id}")

    def disconnect(self, websocket: WebSocket, conversation_id: int, user_id: int):
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id] = [
                (u, ws) for u, ws in self.active_conversations[conversation_id] if ws != websocket
            ]
            if not self.active_conversations[conversation_id]:
                del self.active_conversations[conversation_id]

        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"User {user_id} disconnected from conversation {conversation_id}")

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0

    async def broadcast_to_conversation(self, conversation_id: int, payload: dict, exclude_user_id: int = None):
        if conversation_id in self.active_conversations:
            data = json.dumps(payload)
            for user_id, ws in self.active_conversations[conversation_id]:
                if exclude_user_id is not None and user_id == exclude_user_id:
                    continue
                try:
                    await ws.send_text(data)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")

    async def send_to_user(self, user_id: int, payload: dict):
        if user_id in self.user_connections:
            data = json.dumps(payload)
            for ws in list(self.user_connections[user_id]):
                try:
                    await ws.send_text(data)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")

manager = ConnectionManager()

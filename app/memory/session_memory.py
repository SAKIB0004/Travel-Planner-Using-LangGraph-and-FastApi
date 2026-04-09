from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.config.settings import get_settings


class SessionMemoryStore:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._settings = get_settings()

    def get(self, session_id: str) -> dict[str, Any]:
        record = self._store.get(session_id, {})
        expires_at = record.get("expires_at")
        if expires_at and datetime.now(timezone.utc) > expires_at:
            self._store.pop(session_id, None)
            return {}
        return record.get("preferences", {})

    def upsert(self, session_id: str, preferences: dict[str, Any]) -> None:
        current = self.get(session_id)
        current.update({k: v for k, v in preferences.items() if v not in (None, [], "")})
        ttl = timedelta(minutes=self._settings.default_session_ttl_minutes)
        self._store[session_id] = {
            "preferences": current,
            "expires_at": datetime.now(timezone.utc) + ttl,
        }


session_memory = SessionMemoryStore()

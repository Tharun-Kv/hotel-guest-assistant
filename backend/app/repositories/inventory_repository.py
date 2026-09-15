"""Atomic JSON snapshots for one or more live hotel inventories."""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import DATA_DIR


class InventoryRepository:
    def __init__(self, file_path: str | Path = DATA_DIR / "live_inventory.json") -> None:
        self.file_path = Path(file_path)
        self._lock = Lock()

    def _read_registry(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {"hotels": {}}
        with self.file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if "hotels" in payload:
            return {"hotels": payload.get("hotels", {})}
        # Migrate the original single-hotel snapshot on first read.
        hotel_id = payload.get("hotel_id", "default")
        return {"hotels": {hotel_id: payload}}

    def load(self, hotel_id: str = "default") -> dict[str, Any]:
        snapshot = self._read_registry()["hotels"].get(hotel_id)
        if snapshot is None:
            return {"hotel_id": hotel_id, "last_synced_at": None, "rooms": [], "bookings": []}
        return {
            "hotel_id": snapshot.get("hotel_id", hotel_id),
            "last_synced_at": snapshot.get("last_synced_at"),
            "rooms": snapshot.get("rooms", []),
            "bookings": snapshot.get("bookings", []),
        }

    def replace(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        hotel_id = snapshot.get("hotel_id", "default")
        payload = {
            "hotel_id": hotel_id,
            "last_synced_at": snapshot.get("last_synced_at") or datetime.now(timezone.utc).isoformat(),
            "rooms": snapshot.get("rooms", []),
            "bookings": snapshot.get("bookings", []),
        }
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            registry = self._read_registry()
            registry["hotels"][hotel_id] = payload
            temporary_path: str | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.file_path.parent, delete=False, suffix=".tmp"
                ) as temporary:
                    json.dump(registry, temporary, ensure_ascii=False, indent=2)
                    temporary_path = temporary.name
                os.replace(temporary_path, self.file_path)
            finally:
                if temporary_path and os.path.exists(temporary_path):
                    os.unlink(temporary_path)
        return payload

    def get_rooms(self, hotel_id: str = "default") -> list[dict[str, Any]]:
        return self.load(hotel_id)["rooms"]

    def get_booking_records(self, hotel_id: str = "default") -> list[dict[str, Any]]:
        return self.load(hotel_id)["bookings"]

    def get_last_synced_at(self, hotel_id: str = "default") -> str | None:
        return self.load(hotel_id).get("last_synced_at")

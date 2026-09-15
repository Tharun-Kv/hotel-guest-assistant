import json

from app.repositories.inventory_repository import InventoryRepository


def test_inventory_repository_replaces_snapshot_atomically(tmp_path):
    path = tmp_path / "live_inventory.json"
    repository = InventoryRepository(path)

    saved = repository.replace(
        {
            "hotel_id": "demo",
            "rooms": [{"room_id": "ROOM1", "status": "maintenance"}],
            "bookings": [],
        }
    )

    assert saved["hotel_id"] == "demo"
    assert repository.load("demo")["rooms"][0]["status"] == "maintenance"
    assert json.loads(path.read_text(encoding="utf-8"))["hotels"]["demo"]["hotel_id"] == "demo"

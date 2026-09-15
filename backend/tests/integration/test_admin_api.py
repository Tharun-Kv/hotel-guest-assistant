from fastapi.testclient import TestClient

from app.api.routes import admin
from app.core.config import settings
from app.main import app
from app.repositories.inventory_repository import InventoryRepository


client = TestClient(app)


def test_admin_inventory_update_is_used_by_the_operator_api(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(admin, "inventory_repository", InventoryRepository(tmp_path / "live.json"))

    response = client.put(
        "/api/admin/inventory",
        json={
            "hotel_id": "default",
            "rooms": [
                {"room_id": "DLX001", "status": "maintenance", "price_per_night": 270},
                {"room_id": "FAM001", "status": "available", "price_per_night": 410},
            ],
            "bookings": [],
        },
    )

    assert response.status_code == 200
    assert response.json()["rooms"][0]["status"] == "maintenance"

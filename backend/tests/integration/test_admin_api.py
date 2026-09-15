import base64

import pytest
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


def test_admin_basic_auth_accepts_configured_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_USERNAME", "hotel-admin")
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", "correct-password")
    monkeypatch.setattr(admin, "inventory_repository", InventoryRepository(tmp_path / "live.json"))
    credentials = base64.b64encode(b"hotel-admin:correct-password").decode("ascii")

    response = client.get("/api/admin/inventory", headers={"Authorization": f"Basic {credentials}"})

    assert response.status_code == 200


def test_admin_basic_auth_rejects_invalid_credentials(monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_USERNAME", "hotel-admin")
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", "correct-password")
    credentials = base64.b64encode(b"hotel-admin:wrong-password").decode("ascii")

    response = client.get("/api/admin/inventory", headers={"Authorization": f"Basic {credentials}"})

    assert response.status_code == 401


def test_admin_basic_auth_is_allowed_by_frontend_cors():
    response = client.options(
        "/api/admin/inventory",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 200
    assert "authorization" in response.headers["access-control-allow-headers"].lower()

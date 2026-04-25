import pytest


@pytest.mark.anyio
async def test_station_user_device_and_transaction_endpoints(async_client, auth_headers):
    stations_response = await async_client.get("/stations", headers=auth_headers)
    assert stations_response.status_code == 200
    assert len(stations_response.json()) == 1

    device_response = await async_client.get("/devices", headers=auth_headers)
    assert device_response.status_code == 200
    assert device_response.json()[0]["id"] == "DEV001"

    user_response = await async_client.post(
        "/users",
        headers=auth_headers,
        json={
            "company_id": "COMTST",
            "station_id": "STA001",
            "full_name": "Manager User",
            "email": "manager@example.com",
            "password": "Password123!",
            "role": "manager",
        },
    )
    assert user_response.status_code == 201
    assert user_response.json()["email"] == "manager@example.com"

    tx_response = await async_client.post(
        "/transactions",
        headers=auth_headers,
        json={
            "station_id": "STA001",
            "pump_id": "PUMP01",
            "nozzle_id": "NOZ01",
            "device_id": "DEV001",
            "attendant_id": "ATT001",
            "start_time": "2026-04-24T10:00:00Z",
            "end_time": "2026-04-24T10:00:55Z",
            "liters": 12.35,
            "price_per_liter": 972,
            "amount": 12000,
            "pulse_count": 1235,
            "duration_seconds": 55,
            "metadata_json": {},
        },
    )
    assert tx_response.status_code == 201
    assert tx_response.json()["pump_id"] == "PUMP01"

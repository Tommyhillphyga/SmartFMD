import pytest


@pytest.mark.anyio
async def test_reports_and_exports(async_client, auth_headers):
    await async_client.post(
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

    report_response = await async_client.get("/reports/overview", headers=auth_headers)
    assert report_response.status_code == 200
    assert "daily_revenue" in report_response.json()

    csv_response = await async_client.get("/reports/export/csv", headers=auth_headers)
    assert csv_response.status_code == 200
    assert "station_id" in csv_response.text

    pdf_response = await async_client.get("/reports/export/pdf", headers=auth_headers)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"].startswith("application/pdf")

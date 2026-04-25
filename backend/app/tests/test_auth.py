import pytest


@pytest.mark.anyio
async def test_login_and_refresh(async_client):
    login_response = await async_client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!"},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["user"]["email"] == "admin@example.com"
    assert payload["access_token"]
    assert payload["refresh_token"]

    refresh_response = await async_client.post(
        "/auth/refresh",
        json={"refresh_token": payload["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]


@pytest.mark.anyio
async def test_me_endpoint(async_client, access_token):
    response = await async_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == "USRADMIN"

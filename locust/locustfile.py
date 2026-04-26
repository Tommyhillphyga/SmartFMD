import json
import time
from uuid import uuid4

from locust import HttpUser, between, events, task
from websocket import create_connection


class SmartFMDUser(HttpUser):
    wait_time = between(1, 3)
    token: str | None = None

    def on_start(self) -> None:
        response = self.client.post(
            "/auth/login",
            json={"email": "admin@smartfmd.local", "password": "Admin123!"},
            name="/auth/login",
        )
        if response.ok:
            self.token = response.json().get("access_token")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(4)
    def dashboard_overview(self) -> None:
        self.client.get("/stations/dashboard/overview", headers=self._headers(), name="/stations/dashboard/overview")
        self.client.get("/reports/overview", headers=self._headers(), name="/reports/overview")
        self.client.get("/alerts?status=open", headers=self._headers(), name="/alerts?status=open")

    @task(3)
    def transactions_stress(self) -> None:
        self.client.get(
            "/transactions?limit=100",
            headers=self._headers(),
            name="/transactions?limit=100",
        )

    @task(2)
    def station_and_device_views(self) -> None:
        self.client.get("/stations/STA001", headers=self._headers(), name="/stations/{station_id}")
        self.client.get("/devices?station_id=STA001", headers=self._headers(), name="/devices?station_id")

    @task(1)
    def websocket_stream_probe(self) -> None:
        if not self.token:
            return
        started = time.perf_counter()
        try:
            ws = create_connection(
                f"ws://{self.host.replace('http://', '').replace('https://', '')}/ws/dashboard/STA001",
                timeout=1,
            )
            ws.send(json.dumps({"type": "probe", "id": str(uuid4())}))
            ws.close()
            events.request.fire(
                request_type="WS",
                name="/ws/dashboard/{station_id}",
                response_time=(time.perf_counter() - started) * 1000,
                response_length=0,
                exception=None,
            )
        except Exception as exc:  # pragma: no cover - exercised in load environment
            events.request.fire(
                request_type="WS",
                name="/ws/dashboard/{station_id}",
                response_time=(time.perf_counter() - started) * 1000,
                response_length=0,
                exception=exc,
            )

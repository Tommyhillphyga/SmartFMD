from fastapi import APIRouter

from app.api.routes import alerts, auth, devices, health, metrics, pumps, reports, stations, transactions, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stations.router, prefix="/stations", tags=["stations"])
api_router.include_router(pumps.router, prefix="/pumps", tags=["pumps"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(metrics.router, tags=["metrics"])

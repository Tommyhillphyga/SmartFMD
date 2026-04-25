from app.services.telemetry import TelemetryIngestionService
from app.services.websocket_manager import WebSocketManager

websocket_manager = WebSocketManager()
telemetry_service = TelemetryIngestionService(websocket_manager)


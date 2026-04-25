from prometheus_client import Counter, Gauge

telemetry_messages_total = Counter(
    "smartfmd_telemetry_messages_total",
    "Number of telemetry messages ingested",
)
transactions_total = Counter(
    "smartfmd_transactions_total",
    "Number of completed transactions ingested",
)
alerts_total = Counter(
    "smartfmd_alerts_total",
    "Number of fraud alerts generated",
    ["severity", "rule_name"],
)
active_websocket_connections = Gauge(
    "smartfmd_active_websocket_connections",
    "Number of active dashboard websocket connections",
)


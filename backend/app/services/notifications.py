from app.models import Alert
from app.workers.jobs import send_email_alert, send_sms_alert, send_whatsapp_alert
from app.workers.queue import notification_queue


def queue_alert_notifications(alert: Alert) -> None:
    summary = f"[{alert.severity.value.upper()}] {alert.rule_name}: {alert.message}"
    notification_queue.enqueue(send_email_alert, "ops@example.com", "SmartFMD Alert", summary)
    notification_queue.enqueue(send_sms_alert, "+2340000000000", summary)
    notification_queue.enqueue(send_whatsapp_alert, "ops-webhook", summary)

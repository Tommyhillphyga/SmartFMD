from app.core.logging import logger


def send_email_alert(recipient: str, subject: str, body: str) -> None:
    logger.info("EMAIL placeholder -> %s | %s | %s", recipient, subject, body)


def send_sms_alert(phone_number: str, message: str) -> None:
    logger.info("SMS placeholder -> %s | %s", phone_number, message)


def send_whatsapp_alert(destination: str, message: str) -> None:
    logger.info("WHATSAPP placeholder -> %s | %s", destination, message)


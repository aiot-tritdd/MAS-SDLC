import os
import requests

def send_notification(message: str) -> None:
    """Send a notification to the Telegram bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message}, timeout = 10)
    print("Send message to telegram succesfully: {message}")

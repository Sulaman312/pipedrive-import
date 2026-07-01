import os
import requests

def send_slack_message(text: str) -> None:
    """Send a message to the Slack channel specified in the environment variable."""
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_APPOINTMENTS_CHANNEL")

    if not token or not channel:
        raise RuntimeError("Slack bot token or channel not set in environment variables.")
    
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "channel": channel,
            "text": text
        },
        timeout=10  # Set a timeout for the request
    )

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Failed to send message to Slack: {data.get('error')}")
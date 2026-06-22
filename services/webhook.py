import requests

def send_webhook(webhook_url: str, document_id: str, status: str):
    payload = {
        "event": "document.processed",
        "document_id": document_id,
        "status": status
    }
    for attempt in range(3):
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"Webhook sent successfully")
                return
        except Exception as e:
            print(f"Webhook attempt {attempt + 1} failed: {e}")
    print("All webhook attempts failed")
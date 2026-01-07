import requests
import json
from config import DISCORD_WEBHOOK_URL

def send_discord_notification(product_name, old_price, new_price, lowest_price, url, status_type):
    if not DISCORD_WEBHOOK_URL or "your_discord_webhook_url_here" in DISCORD_WEBHOOK_URL:
        print(f"Discord notification skipped for {product_name} (URL not set).")
        return

    # Colors: Green for decrease/lowest, Red for increase, Blue for new
    colors = {
        "price_decrease": 0x2ecc71,
        "new_lowest": 0x1abc9c,
        "price_increase": 0xe74c3c,
        "new_item": 0x3498db
    }
    
    color = colors.get(status_type, 0x95a5a6)
    
    titles = {
        "price_decrease": f"Price Dropped on {product_name}!",
        "new_lowest": f"ALL-TIME LOW on {product_name}!",
        "price_increase": f"Price Increased on {product_name}",
        "new_item": f"New Item Added to Tracker: {product_name}"
    }
    
    title = titles.get(status_type, f"Price Alert: {product_name}")

    payload = {
        "embeds": [
            {
                "title": title,
                "url": url,
                "color": color,
                "fields": [
                    {"name": "Current Price", "value": f"₹{new_price:,.2f}", "inline": True},
                    {"name": "Previous Price", "value": f"₹{old_price:,.2f}" if old_price > 0 else "N/A", "inline": True},
                    {"name": "All-time Lowest", "value": f"₹{lowest_price:,.2f}", "inline": True}
                ],
                "footer": {"text": "Amazon watchlist Price Tracker"}
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        print(f"Notification sent for {product_name} ({status_type})")
    except Exception as e:
        print(f"Failed to send Discord notification for {product_name}: {e}")

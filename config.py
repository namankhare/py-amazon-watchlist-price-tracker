import os
from dotenv import load_dotenv

load_dotenv()

# Discord Webhook URL - Set this in .env file
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Amazon Watchlist URL
WISH_LIST_URL = "https://www.amazon.in/hz/wishlist/ls/148WXHTYKRXBH"

# Check interval in seconds (e.g., 3600 for 1 hour)
CHECK_INTERVAL_SECONDS = 3600

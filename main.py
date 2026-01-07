import asyncio
from scraper import scrape_amazon_watchlist
from database import init_db, upsert_product, get_all_products
from notifier import send_discord_notification
from config import WISH_LIST_URL, CHECK_INTERVAL_SECONDS
from datetime import datetime

async def main():
    print("--- Amazon Watchlist Price Tracker ---")
    
    # Ensure DB is initialized
    init_db()
    
    while True:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scraping cycle...")
        
        # Scrape the watchlist
        products = await scrape_amazon_watchlist(WISH_LIST_URL)
        
        if not products:
            print("No products found or error during scraping.")
        else:
            print(f"Scraped {len(products)} products. updating database...")
            
            # Update database and notify
            for product in products:
                update_result = upsert_product(product)
                
                # Notify if something interesting happened
                if update_result["status"] != "no_change":
                    send_discord_notification(
                        update_result["name"],
                        update_result["old_price"],
                        update_result["new_price"],
                        update_result["lowest_price"],
                        update_result["url"],
                        update_result["status"]
                    )
            
            print("\n--- Current Tracker Status ---")
            all_items = get_all_products()
            for item in all_items:
                print(f"ID: {item[0]} | Price: ₹{item[2]} | Lowest: ₹{item[4]} | Name: {item[1][:30]}... | URL: {item[6][:30]}...")

        print(f"\nCycle complete. Waiting {CHECK_INTERVAL_SECONDS} seconds for the next run...")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())

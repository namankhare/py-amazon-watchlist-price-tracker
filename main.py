import asyncio
from scraper import scrape_amazon_watchlist
from database import init_db, upsert_product, get_all_products
from config import WISH_LIST_URL

async def main():
    print("--- Amazon Watchlist Price Tracker ---")
    
    # Ensure DB is initialized
    init_db()
    
    # Scrape the watchlist
    print(f"Scraping watchlist...")
    products = await scrape_amazon_watchlist(WISH_LIST_URL)
    
    if not products:
        print("No products found or error during scraping.")
        return

    print(f"Scraped {len(products)} products. updating database...")
    
    # Update database
    for product in products:
        upsert_product(product)
        
    print("\n--- Current Tracker Status ---")
    all_items = get_all_products()
    for item in all_items:
        print(f"ID: {item[0]} | Price: ₹{item[2]} | Lowest: ₹{item[4]} | Name: {item[1][:30]}... | URL: {item[6][:30]}...")

if __name__ == "__main__":
    asyncio.run(main())

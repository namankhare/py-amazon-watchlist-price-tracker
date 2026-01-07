import asyncio
import re
from playwright.async_api import async_playwright
from config import WISH_LIST_URL

async def scrape_amazon_watchlist(url):
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print(f"Navigating to watchlist: {url}...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for any item to appear
            try:
                await page.wait_for_selector("li.g-item-sortable", timeout=15000)
            except:
                print("No items found or timeout waiting for elements.")
            
            # Scroll to load all items (Amazon wishlists often lazy load)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            # Check for CAPTCHA/Robot detection
            content = await page.content()
            if "api-services-support@amazon.com" in content:
                print("Bot detection triggered.")
                await browser.close()
                return []

            # Find all items in the list
            items = []
            product_elements = await page.query_selector_all("li.g-item-sortable")
            print(f"Found {len(product_elements)} potential items.")

            for element in product_elements:
                try:
                    # Extract Item ID and Price from data attributes
                    item_id = await element.get_attribute("data-itemid")
                    price_str = await element.get_attribute("data-price")
                    
                    # Extract name and URL from the nested <a> tag using title attribute or text
                    name = "Unknown"
                    url = "Unknown"
                    name_link = await element.query_selector("h2 a.a-link-normal")
                    if name_link:
                        name = await name_link.get_attribute("title")
                        if not name:
                            name = await name_link.inner_text()
                        name = name.strip()
                        
                        href = await name_link.get_attribute("href")
                        if href:
                            # Prepend amazon domain if it's a relative URL
                            if href.startswith('/'):
                                url = f"https://www.amazon.in{href}"
                            else:
                                url = href

                    # Handle missing item_id by looking for ASIN in the link if not already found
                    if not item_id or item_id == "null":
                        if url != "Unknown":
                            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
                            if asin_match:
                                item_id = asin_match.group(1)

                    # Clean price
                    price = 0.0
                    if price_str and price_str != "null":
                        price = float(price_str)
                    
                    if item_id:
                        items.append({
                            "item_id": item_id,
                            "name": name,
                            "price": price,
                            "url": url
                        })
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            await browser.close()
            return items
        except Exception as e:
            print(f"Error during scraping: {e}")
            await browser.close()
            return []

if __name__ == "__main__":
    # Ensure a valid URL is in config.py or use a test one
    test_url = WISH_LIST_URL
    if "your_list_id_here" in test_url:
        print("Please update WISH_LIST_URL in config.py with your actual Amazon wishlist URL.")
    else:
        results = asyncio.run(scrape_amazon_watchlist(test_url))
        print(f"\nScraped {len(results)} items:")
        for res in results:
            print(f"ID: {res['item_id']} | Price: ₹{res['price']} | Name: {res['name'][:30]}... | URL: {res['url'][:30]}...")

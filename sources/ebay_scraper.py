import asyncio
import csv
import random
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

def get_superstore_context():
    segments = ["Consumer", "Corporate", "Home Office"]
    regions = ["South", "West", "Central", "East"]
    return {
        "Order_Date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%d/%m/%Y"),
        "Segment": random.choice(segments),
        "Region": random.choice(regions),
        "Order_ID": f"CA-2026-{random.randint(100000, 999999)}"
    }

async def scrape_ebay_v3(search_term, pages_to_scrape=2):
    async with async_playwright() as p:
        # Launching with stealth-like headers
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        all_results = []
        
        for p_num in range(1, pages_to_scrape + 1):
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}&_pgn={p_num}"
            print(f"📡 Page {p_num}: Attempting to load results...")
            
            try:
                # HUMAN BEHAVIOR: Random pause before Page 2+ to avoid TargetClosedError
                if p_num > 1:
                    delay = random.uniform(4, 8)
                    print(f"⏳ Mimicking human reading time... Waiting {delay:.2f}s")
                    await asyncio.sleep(delay)

                # Use a more stable wait state
                await page.goto(url, wait_until="load", timeout=60000)
                
                # Check for CAPTCHA/Human verification
                if "captcha" in page.url or await page.get_by_text("Verify you are human").is_visible():
                    print("🛑 Bot detection triggered! Please solve the CAPTCHA in the browser window.")
                    await page.wait_for_selector(".s-item", timeout=60000)

            except Exception as e:
                print(f"⚠️ Page {p_num} failed or browser closed: {e}")
                break # Exit the loop but continue to save whatever we have

            # Wait for content and extract
            await page.wait_for_selector(".s-item, .s-card", timeout=15000)
            listings = await page.locator(".s-item, .s-card, [class*='s-item__wrapper']").all()
            
            items_on_this_page = 0
            for item in listings[2:50]: # Scrape up to 50 items per page
                try:
                    title = await item.locator("[class*='title']").first.inner_text()
                    price = await item.locator("[class*='price']").first.inner_text()
                    
                    if "sponsored" in title.lower() or "Shop on" in title: continue

                    clean_price = price.replace('$', '').replace(',', '').split(' to ')[0].strip()
                    ctx = get_superstore_context()

                    all_results.append({
                        "Row_ID": len(all_results) + 1,
                        "Order_ID": ctx["Order_ID"],
                        "Order_Date": ctx["Order_Date"],
                        "Segment": ctx["Segment"],
                        "Region": ctx["Region"],
                        "Product_Name": title.replace("New Listing", "").strip(),
                        "Sales": clean_price
                    })
                    items_on_this_page += 1
                except:
                    continue
            
            print(f"✅ Successfully extracted {items_on_this_page} items from page {p_num}.")

        await browser.close()

        # Final Export
        if all_results:
            with open('data/raw/ebay_scraped.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
                writer.writeheader()
                writer.writerows(all_results)
            print(f"🎉 Pipeline finished. Saved {len(all_results)} items to superstore_scraped.csv")

if __name__ == "__main__":
    asyncio.run(scrape_ebay_v3("ergonomic office chairs", pages_to_scrape=2))
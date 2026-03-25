import asyncio
import csv
import os
import random
import hashlib
from playwright.async_api import async_playwright

# ----------------------------------------------------------------------
# Local list of single words (extend as needed)
# ----------------------------------------------------------------------
SEARCH_WORDS = [
    "computer", "phone", "chair", "desk", "lamp", "book", "game", "tool",
    "shoe", "bag", "watch", "camera", "speaker", "headphone", "monitor",
    "keyboard", "mouse", "printer", "paper", "pen", "pencil", "notebook",
    "bottle", "cup", "plate", "knife", "fork", "spoon", "towel", "soap",
    "shampoo", "brush", "comb", "mirror", "clock", "calendar", "wallet",
    "backpack", "umbrella", "hat", "glove", "scarf", "belt", "socks",
    "shirt", "pants", "jacket", "coat", "dress", "skirt", "shorts",
    "sandals", "boots", "sneakers", "toy", "doll", "puzzle", "card",
    "board", "video", "music", "movie", "magazine", "newspaper"
]

def generate_search_term():
    """Return a single random word from the list."""
    return random.choice(SEARCH_WORDS)

def compute_hash(product_name, sales):
    """Return a SHA-256 hash of product name and sales combined."""
    combined = f"{product_name}|{sales}".encode('utf-8')
    return hashlib.sha256(combined).hexdigest()

def load_existing_hashes(csv_path):
    """
    Read existing eBay CSV and return a set of hashes.
    If the CSV lacks a 'Hash' column, compute hashes on the fly.
    """
    existing = set()
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    h = row.get("Hash")
                    if h:
                        existing.add(h)
                    else:
                        # Backward compatibility: compute hash from product name and sales
                        name = row.get("Product_Name", "")
                        sales = row.get("Sales", "")
                        if name and sales:
                            existing.add(compute_hash(name, sales))
        except Exception as e:
            print(f"⚠️ Error reading existing CSV: {e}")
    return existing

def append_to_csv(csv_path, new_rows):
    """Append new rows to the CSV, writing header if file is empty."""
    file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
    mode = 'a' if file_exists else 'w'
    with open(csv_path, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Product_Name", "Sales", "Hash"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_rows)

async def scrape_ebay_v3(max_pages=10):
    """
    Scrapes eBay product listings using a randomly selected single word
    as the search term and a random page number. Appends only unique products
    (by hash of name + price) to the output file.
    """
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    csv_path = f'{output_dir}/ebay_scraped.csv'

    # Load existing hashes to avoid duplicates
    existing_hashes = load_existing_hashes(csv_path)
    print(f"📚 Found {len(existing_hashes)} existing product entries in {csv_path}")

    # Random search term (single word)
    search_term = generate_search_term()
    print(f"🎲 Randomly selected search term: '{search_term}'")

    # Random page number
    random_page = random.randint(1, max_pages)
    print(f"🎲 Randomly selected page: {random_page} (max pages considered: {max_pages})")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        new_results = []

        url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}&_pgn={random_page}"
        print(f"\n📡 Loading URL: {url}")

        try:
            await page.goto(url, wait_until="load", timeout=60000)

            # Check for CAPTCHA / human verification
            if "captcha" in page.url or await page.get_by_text("Verify you are human").is_visible():
                print("🛑 Bot detection triggered! Please solve the CAPTCHA in the browser window.")
                await page.wait_for_selector(".s-item", timeout=60000)

        except Exception as e:
            print(f"⚠️ Page load failed: {e}")
            await browser.close()
            return

        # Wait for content and extract
        try:
            await page.wait_for_selector(".s-item, .s-card", timeout=15000)
        except:
            print("❌ No listing container found. Saving screenshot for inspection.")
            await page.screenshot(path=f"{output_dir}/ebay_error_layout.png")
            await browser.close()
            return

        listings = await page.locator(".s-item, .s-card, [class*='s-item__wrapper']").all()
        print(f"📦 Found {len(listings)} items.")

        items_on_this_page = 0
        for idx, item in enumerate(listings[2:50]):  # skip first two (often ads)
            try:
                title_el = item.locator("[class*='title']").first
                title = await title_el.inner_text() if await title_el.count() > 0 else "N/A"
                title = title.strip()

                # Skip sponsored items
                if "sponsored" in title.lower() or "Shop on" in title:
                    print(f"   ⏩ Item {idx}: Sponsored. Skipping.")
                    continue

                price_el = item.locator("[class*='price']").first
                price_text = await price_el.inner_text() if await price_el.count() > 0 else ""
                if not price_text:
                    print(f"   ⚠️ Item {idx}: No price found. Skipping.")
                    continue

                # Clean price (first part if range, remove $, commas)
                clean_price = price_text.replace('$', '').replace(',', '').split(' to ')[0].strip()

                # Generate hash
                row_hash = compute_hash(title, clean_price)

                # Skip if already in DB
                if row_hash in existing_hashes:
                    print(f"   ⏩ Item {idx}: Already in database (hash match). Skipping.")
                    continue

                print(f"   ✨ Item {idx}: Found '{title[:35]}...' at ${clean_price}")

                new_results.append({
                    "Product_Name": title,
                    "Sales": clean_price,
                    "Hash": row_hash
                })
                items_on_this_page += 1

            except Exception as e:
                print(f"   ❌ Item {idx} ERROR: {str(e)[:50]}")
                continue

        print(f"🏁 Page {random_page} Summary: Extracted {items_on_this_page} new items.")
        await browser.close()

        # Append new results to CSV
        if new_results:
            append_to_csv(csv_path, new_results)
            print(f"\n🎉 SUCCESS: Appended {len(new_results)} new items to {csv_path}")
        else:
            print("\n💀 No new items to append. All products already exist or nothing found.")

if __name__ == "__main__":
    asyncio.run(scrape_ebay_v3(max_pages=10))
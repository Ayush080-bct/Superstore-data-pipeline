import asyncio
import csv
import os
import random
import hashlib  # for generating hash
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
    """Read existing CSV and return a set of hashes."""
    existing = set()
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # The hash column might not exist in older files
                    h = row.get("Hash")
                    if h:
                        existing.add(h)
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

async def scrape_amazon_v1(max_pages=10):
    """
    Scrapes Amazon product listings using a randomly selected single word
    as the search term and a random page number. Appends only unique products
    (by hash of name + price) to the output file.
    """
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    csv_path = f'{output_dir}/amazon_scraped.csv'

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
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        new_results = []

        url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}&page={random_page}"
        print(f"\n📡 Loading URL: {url}")

        await page.goto(url, wait_until="domcontentloaded")

        # BOT CHECK
        if "api-services-support@amazon.com" in await page.content():
            print("🚨 CAPTCHA detected. Amazon is blocking this session.")
            await page.screenshot(path=f"{output_dir}/captcha_alert.png")
            await browser.close()
            return

        # SCROLL
        print("🕵️ Scrolling to trigger lazy-loading...")
        for _ in range(3):
            await page.mouse.wheel(0, 800)
            await asyncio.sleep(1.5)

        # CONTAINER CHECK
        try:
            await page.wait_for_selector(".s-main-slot", timeout=10000)
        except:
            print("❌ Failed to find .s-main-slot. Saving layout for inspection.")
            await page.screenshot(path=f"{output_dir}/error_layout.png")
            await browser.close()
            return

        listings = await page.locator("div.s-result-item[data-asin]").all()
        print(f"📦 Found {len(listings)} items with data-asin.")

        items_on_this_page = 0
        for index, item in enumerate(listings):
            asin = await item.get_attribute("data-asin")
            if not asin or len(asin) < 5:
                continue

            # diagnostic dump of first item
            if index == 0:
                item_html = await item.inner_html()
                with open(f"{output_dir}/debug_item_structure.txt", "w", encoding="utf-8") as f:
                    f.write(item_html)
                print(f"🔬 Saved item {asin} HTML to debug_item_structure.txt")

            try:
                # TITLE
                title_el = item.locator("h2 a, .a-size-medium, .a-size-base-plus").first
                title = await title_el.inner_text() if await title_el.count() > 0 else "N/A"
                title = title.strip()

                # Skip "Amazon's Choice"
                if "Amazon's Choice" in title:
                    print(f"   ⏩ Item {index} [{asin}]: Contains 'Amazon's Choice'. Skipping.")
                    continue

                # PRICE
                price_val = None
                offscreen = item.locator(".a-price .a-offscreen").first
                whole = item.locator(".a-price-whole").first
                color_price = item.locator(".a-color-price").first
                price_search = item.get_by_text("$", exact=False).first

                if await offscreen.count() > 0:
                    price_val = await offscreen.inner_text()
                elif await whole.count() > 0:
                    w_text = await whole.inner_text()
                    f_el = item.locator(".a-price-fraction").first
                    f_text = await f_el.inner_text() if await f_el.count() > 0 else "00"
                    price_val = f"{w_text}.{f_text}"
                elif await color_price.count() > 0:
                    price_val = await color_price.inner_text()
                elif await price_search.count() > 0:
                    price_val = await price_search.inner_text()

                if not price_val or len(price_val.strip()) == 0:
                    print(f"   ⚠️ Item {index} [{asin}]: No price found. Skipping.")
                    continue

                clean_price = price_val.split('\n')[0].replace('$', '').replace(',', '').strip()

                # SPONSORED
                is_sponsored = await item.locator("text='Sponsored', .puis-sponsored-label-text").count() > 0
                if is_sponsored:
                    print(f"   ⏩ Item {index} [{asin}]: Sponsored. Skipping.")
                    continue

                # Generate hash from product name and price
                row_hash = compute_hash(title, clean_price)

                # Skip if hash already exists
                if row_hash in existing_hashes:
                    print(f"   ⏩ Item {index} [{asin}]: Already in database (hash match). Skipping.")
                    continue

                print(f"   ✨ Item {index} [{asin}]: Found '{title[:35]}...' at ${clean_price}")

                new_results.append({
                    "Product_Name": title,
                    "Sales": clean_price,
                    "Hash": row_hash
                })
                items_on_this_page += 1

            except Exception as e:
                print(f"   ❌ Item {index} ERROR: {str(e)[:50]}")
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
    asyncio.run(scrape_amazon_v1(max_pages=10))
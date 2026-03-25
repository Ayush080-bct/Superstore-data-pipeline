import csv
import random
import re
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
INPUT_CSV = "data/raw/ebay_scraped.csv"
OUTPUT_CSV = "data/processed/cleaned_ebay.csv"

# ----------------------------------------------------------------------
# STATIC LISTS FOR RANDOM GENERATION
# ----------------------------------------------------------------------
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
REGIONS = ["West", "Central", "South", "East"]

# US cities and states (one per state for variety)
CITIES_STATES = {
    "New York": "New York",
    "Los Angeles": "California",
    "Chicago": "Illinois",
    "Houston": "Texas",
    "Phoenix": "Arizona",
    "Philadelphia": "Pennsylvania",
    "San Antonio": "Texas",
    "San Diego": "California",
    "Dallas": "Texas",
    "Austin": "Texas",
    "San Jose": "California",
    "Jacksonville": "Florida",
    "Fort Worth": "Texas",
    "Columbus": "Ohio",
    "Charlotte": "North Carolina",
    "San Francisco": "California",
    "Indianapolis": "Indiana",
    "Seattle": "Washington",
    "Denver": "Colorado",
    "Washington": "District of Columbia",
    "Boston": "Massachusetts",
    "Nashville": "Tennessee",
    "Baltimore": "Maryland",
    "Oklahoma City": "Oklahoma",
    "Portland": "Oregon",
    "Las Vegas": "Nevada",
    "Detroit": "Michigan",
    "Memphis": "Tennessee",
    "Louisville": "Kentucky",
    "Milwaukee": "Wisconsin",
    "Albuquerque": "New Mexico",
    "Tucson": "Arizona",
    "Fresno": "California",
    "Sacramento": "California",
    "Atlanta": "Georgia",
    "Kansas City": "Missouri",
    "Miami": "Florida",
    "Omaha": "Nebraska",
    "Raleigh": "North Carolina",
    "Colorado Springs": "Colorado",
    "Virginia Beach": "Virginia",
    "Long Beach": "California",
    "Oakland": "California",
    "Minneapolis": "Minnesota",
    "Tulsa": "Oklahoma",
    "Arlington": "Texas",
    "New Orleans": "Louisiana",
    "Wichita": "Kansas",
    "Cleveland": "Ohio",
    "Tampa": "Florida"
}

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Helen", "Donald", "Sandra", "Mark", "Donna",
    "Paul", "Carol", "Steven", "Ruth", "Andrew", "Sharon", "Kenneth", "Michelle",
    "George", "Laura", "Joshua", "Sarah", "Kevin", "Kimberly", "Brian", "Deborah",
    "Edward", "Emily", "Ronald", "Amanda", "Timothy", "Angela", "Jason", "Melissa",
    "Jeffrey", "Stephanie", "Ryan", "Rebecca", "Gary", "Kathleen", "Jacob", "Amy",
    "Nicholas", "Shirley", "Eric", "Virginia", "Jonathan", "Kathryn", "Stephen", "Anna",
    "Larry", "Christina", "Justin", "Debra", "Scott", "Cynthia", "Brandon", "Janet",
    "Frank", "Maria", "Benjamin", "Heather", "Gregory", "Diane", "Raymond", "Julie",
    "Samuel", "Joyce", "Patrick", "Evelyn", "Alexander", "Joan", "Jack", "Victoria",
    "Dennis", "Kelly", "Jerry", "Christine"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster",
    "Jimenez"
]

# Keyword‑based category mapping (extended)
CATEGORY_MAP = {
    # Technology
    "keyboard": ("Technology", "Keyboards"),
    "mouse": ("Technology", "Mice"),
    "monitor": ("Technology", "Monitors"),
    "laptop": ("Technology", "Laptops"),
    "printer": ("Technology", "Printers"),
    "phone": ("Technology", "Phones"),
    "tablet": ("Technology", "Tablets"),
    "headphone": ("Technology", "Audio"),
    "speaker": ("Technology", "Audio"),
    "camera": ("Technology", "Cameras"),
    # Furniture
    "chair": ("Furniture", "Chairs"),
    "desk": ("Furniture", "Desks"),
    "table": ("Furniture", "Tables"),
    "bookcase": ("Furniture", "Bookcases"),
    "shelf": ("Furniture", "Bookcases"),
    "cabinet": ("Furniture", "Storage"),
    # Office Supplies
    "paper": ("Office Supplies", "Paper"),
    "pen": ("Office Supplies", "Writing Instruments"),
    "pencil": ("Office Supplies", "Writing Instruments"),
    "folder": ("Office Supplies", "Binders"),
    "binder": ("Office Supplies", "Binders"),
    "label": ("Office Supplies", "Labels"),
    "stapler": ("Office Supplies", "Appliances"),
    "tape": ("Office Supplies", "Appliances"),
    # Apparel / Accessories
    "belt": ("Apparel", "Accessories"),
    "shirt": ("Apparel", "Clothing"),
    "pants": ("Apparel", "Clothing"),
    "jacket": ("Apparel", "Outerwear"),
    "coat": ("Apparel", "Outerwear"),
    "hat": ("Apparel", "Accessories"),
    "glove": ("Apparel", "Accessories"),
    "scarf": ("Apparel", "Accessories"),
    "shoe": ("Apparel", "Footwear"),
    "boots": ("Apparel", "Footwear"),
    "sneakers": ("Apparel", "Footwear"),
    "dress": ("Apparel", "Clothing"),
    "skirt": ("Apparel", "Clothing"),
    "shorts": ("Apparel", "Clothing"),
    # Others
    "toy": ("Office Supplies", "Miscellaneous"),
    "game": ("Office Supplies", "Miscellaneous"),
    "book": ("Office Supplies", "Miscellaneous"),
}
DEFAULT_CATEGORY = ("Office Supplies", "Miscellaneous")

# ----------------------------------------------------------------------
# CLEANING FUNCTION
# ----------------------------------------------------------------------
def clean_product_name(name: str) -> str:
    """Remove common eBay appended text like 'Opens in a new window or tab'."""
    patterns = [
        r'\s*Opens in a new window or tab\s*',
        r'\s*Opens in a new window\s*',
        r'\s*Opens in a new tab\s*',
        r'\s*New listing\s*',
        r'\s*Pre-owned\s*',
    ]
    cleaned = name
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_customer():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    cust_id = f"{first[0].lower()}{last[0].lower()}-{random.randint(10000, 99999)}"
    name = f"{first} {last}"
    return cust_id, name

def random_location():
    city = random.choice(list(CITIES_STATES.keys()))
    state = CITIES_STATES[city]
    region = random.choice(REGIONS)
    postal = f"{random.randint(10000, 99999)}"
    return city, state, region, postal

def get_category(product_name):
    name_lower = product_name.lower()
    for keyword, (cat, subcat) in CATEGORY_MAP.items():
        if keyword in name_lower:
            return cat, subcat
    return DEFAULT_CATEGORY

def get_max_ids(existing_file):
    max_row = 0
    max_order_num = 0
    if Path(existing_file).exists():
        with open(existing_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row_id = int(row.get("Row_ID", 0))
                    if row_id > max_row:
                        max_row = row_id
                except ValueError:
                    pass
                order_id = row.get("Order_ID", "")
                if "-" in order_id:
                    parts = order_id.split("-")
                    if len(parts) >= 3:
                        try:
                            num = int(parts[-1])
                            if num > max_order_num:
                                max_order_num = num
                        except ValueError:
                            pass
    return max_row, max_order_num

def load_existing_hashes(existing_file):
    existing = set()
    if Path(existing_file).exists():
        with open(existing_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                h = row.get("Hash", "")
                if h:
                    existing.add(h)
    return existing

def append_to_csv(csv_path, new_rows, existing_hashes):
    rows_to_write = [row for row in new_rows if row["Hash"] not in existing_hashes]
    if not rows_to_write:
        return 0
    file_exists = Path(csv_path).exists() and Path(csv_path).stat().st_size > 0
    mode = 'a' if file_exists else 'w'
    with open(csv_path, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_rows[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows_to_write)
    return len(rows_to_write)

# ----------------------------------------------------------------------
# MAIN TRANSFORMATION
# ----------------------------------------------------------------------
def main():
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load scraped eBay data (must contain Product_Name, Sales, Hash)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return
    df = pd.read_csv(input_path)
    if df.empty:
        print("No input data.")
        return

    # Ensure required columns exist
    required = {"Product_Name", "Sales", "Hash"}
    if not required.issubset(df.columns):
        print("Input CSV must contain columns: Product_Name, Sales, Hash")
        return

    # 2. Load existing Superstore output (to get max IDs and existing hashes)
    max_row_id, max_order_num = get_max_ids(output_path)
    existing_hashes = load_existing_hashes(output_path)
    print(f"Existing: Row_ID max = {max_row_id}, Order_ID numeric max = {max_order_num}")
    print(f"Existing hashes in output: {len(existing_hashes)}")

    # 3. Prepare date range (last 2 years)
    start_date = datetime.now() - timedelta(days=2*365)
    end_date = datetime.now()

    # 4. Build new rows
    new_rows = []
    current_row_id = max_row_id
    current_order_num = max_order_num

    for _, row in df.iterrows():
        product_name = row["Product_Name"]
        cleaned_name = clean_product_name(product_name)   # <-- clean the name
        sales = row["Sales"]
        row_hash = row["Hash"]

        # Skip if hash already exists in output
        if row_hash in existing_hashes:
            print(f"⏩ Skipping {cleaned_name[:40]}... (already in output)")
            continue

        current_row_id += 1
        current_order_num += 1

        # Order date (random in last 2 years)
        order_date = random_date(start_date, end_date)
        # Ship date: 1–7 days later, occasionally missing
        if random.random() < 0.15:
            ship_date_str = ""
            ship_year = ship_month = ship_weekday = ""
        else:
            ship_date = order_date + timedelta(days=random.randint(1, 7))
            ship_date_str = ship_date.strftime("%Y-%m-%d")
            ship_year = ship_date.year
            ship_month = ship_date.strftime("%B")
            ship_weekday = ship_date.strftime("%A")

        # Customer
        cust_id, cust_name = random_customer()

        # Location
        city, state, region, postal = random_location()

        # Product ID (simple placeholder)
        prod_id = f"PROD-{random.randint(10000000, 99999999)}"

        # Category / Subcategory
        category, subcategory = get_category(cleaned_name)

        # Order ID (use prefix "EB-" to distinguish from original Superstore)
        order_id = f"EB-{order_date.year}-{current_order_num:06d}"

        new_rows.append({
            "Row_ID": current_row_id,
            "Order_ID": order_id,
            "Order_Date": order_date.strftime("%Y-%m-%d"),
            "Ship_Date": ship_date_str,
            "Ship_Mode": random.choice(SHIP_MODES),
            "Customer_ID": cust_id,
            "Customer_Name": cust_name,
            "Segment": random.choice(SEGMENTS),
            "Country": "United States",
            "City": city,
            "State": state,
            "Postal_Code": postal,
            "Region": region,
            "Product_ID": prod_id,
            "Category": category,
            "Sub_Category": subcategory,
            "Product_Name": cleaned_name,          # store cleaned name
            "Sales": sales,
            "Order_Year": order_date.year,
            "Order_Month": order_date.strftime("%B"),
            "Order_Weekday": order_date.strftime("%A"),
            "Ship_Year": ship_year,
            "Ship_Month": ship_month,
            "Ship_Weekday": ship_weekday,
            "Hash": row_hash,           # keep original hash for deduplication
        })

    # 5. Append to output
    if new_rows:
        added = append_to_csv(output_path, new_rows, existing_hashes)
        print(f"✅ Added {added} new rows to {output_path}")
    else:
        print("💀 No new rows to add.")

if __name__ == "__main__":
    main()
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
INPUT_CSV = "data/raw/amazon_scraped.csv"
OUTPUT_CSV = "data/processed/cleaned_amazon.csv"
REFERENCE_CSV = "sample_superstore.csv"   # Optional: path to an existing Superstore file
# If REFERENCE_CSV exists, it will be used to generate realistic values.
# Otherwise, the script falls back to the internal lists below.

# ----------------------------------------------------------------------
# HELPER FUNCTIONS FOR LOADING REFERENCE DATA
# ----------------------------------------------------------------------
def load_reference_data(ref_path):
    """Load real Superstore data and extract unique values for later use."""
    if not Path(ref_path).exists():
        return None
    ref = []
    with open(ref_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ref = list(reader)
    # Extract unique values
    customers = set()
    locations = set()  # (city, state, region, postal)
    categories = {}    # keyword -> (category, subcategory)
    for row in ref:
        cust_name = row.get("Customer_Name", "").strip()
        if cust_name:
            customers.add(cust_name)
        city = row.get("City", "").strip()
        state = row.get("State", "").strip()
        region = row.get("Region", "").strip()
        postal = row.get("Postal_Code", "").strip()
        if city and state and region:
            locations.add((city, state, region, postal))
        # For keyword mapping, we could parse product names, but it's complex.
        # Instead, we'll use the actual categories/subcategories from the reference.
        # We'll just store them for random selection later.
    return {
        "customers": list(customers),
        "locations": list(locations),
        # We'll also collect all unique (category, subcategory) pairs
        "category_pairs": list(set((row.get("Category", ""), row.get("Sub_Category", "")) for row in ref if row.get("Category"))),
        "segments": list(set(row.get("Segment", "") for row in ref if row.get("Segment"))),
        "ship_modes": list(set(row.get("Ship_Mode", "") for row in ref if row.get("Ship_Mode"))),
        "regions": list(set(row.get("Region", "") for row in ref if row.get("Region"))),
    }

# ----------------------------------------------------------------------
# FALLBACK LISTS (much larger than before)
# ----------------------------------------------------------------------
# First names from US Census (top 100)
FALLBACK_FIRST_NAMES = [
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
FALLBACK_LAST_NAMES = [
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

# All 50 US states with major cities (one city per state for simplicity)
FALLBACK_CITIES_STATES = {
    "New York": "New York", "Los Angeles": "California", "Chicago": "Illinois",
    "Houston": "Texas", "Phoenix": "Arizona", "Philadelphia": "Pennsylvania",
    "San Antonio": "Texas", "San Diego": "California", "Dallas": "Texas",
    "Austin": "Texas", "San Jose": "California", "Jacksonville": "Florida",
    "Fort Worth": "Texas", "Columbus": "Ohio", "Charlotte": "North Carolina",
    "San Francisco": "California", "Indianapolis": "Indiana", "Seattle": "Washington",
    "Denver": "Colorado", "Washington": "District of Columbia", "Boston": "Massachusetts",
    "Nashville": "Tennessee", "Baltimore": "Maryland", "Oklahoma City": "Oklahoma",
    "Portland": "Oregon", "Las Vegas": "Nevada", "Detroit": "Michigan", "Memphis": "Tennessee",
    "Louisville": "Kentucky", "Milwaukee": "Wisconsin", "Albuquerque": "New Mexico",
    "Tucson": "Arizona", "Fresno": "California", "Sacramento": "California", "Atlanta": "Georgia",
    "Kansas City": "Missouri", "Miami": "Florida", "Omaha": "Nebraska", "Raleigh": "North Carolina",
    "Colorado Springs": "Colorado", "Virginia Beach": "Virginia", "Long Beach": "California",
    "Oakland": "California", "Minneapolis": "Minnesota", "Tulsa": "Oklahoma", "Arlington": "Texas",
    "New Orleans": "Louisiana", "Wichita": "Kansas", "Cleveland": "Ohio", "Tampa": "Florida"
}

# Expanded keyword mapping (over 100 keywords)
FALLBACK_CATEGORY_MAP = {
    # Technology
    "keyboard": ("Technology", "Keyboards"), "mouse": ("Technology", "Mice"),
    "monitor": ("Technology", "Monitors"), "laptop": ("Technology", "Laptops"),
    "printer": ("Technology", "Printers"), "scanner": ("Technology", "Scanners"),
    "tablet": ("Technology", "Tablets"), "phone": ("Technology", "Phones"),
    "smartphone": ("Technology", "Phones"), "headphone": ("Technology", "Audio"),
    "speaker": ("Technology", "Audio"), "webcam": ("Technology", "Accessories"),
    "router": ("Technology", "Networking"), "switch": ("Technology", "Networking"),
    "hard drive": ("Technology", "Storage"), "ssd": ("Technology", "Storage"),
    "ram": ("Technology", "Components"), "cpu": ("Technology", "Components"),
    "gpu": ("Technology", "Components"), "motherboard": ("Technology", "Components"),
    # Furniture
    "chair": ("Furniture", "Chairs"), "desk": ("Furniture", "Desks"),
    "table": ("Furniture", "Tables"), "bookcase": ("Furniture", "Bookcases"),
    "shelf": ("Furniture", "Bookcases"), "cabinet": ("Furniture", "Storage"),
    "filing cabinet": ("Furniture", "Storage"), "stool": ("Furniture", "Chairs"),
    "couch": ("Furniture", "Furnishings"), "sofa": ("Furniture", "Furnishings"),
    "bed": ("Furniture", "Furnishings"), "mattress": ("Furniture", "Furnishings"),
    # Office Supplies
    "paper": ("Office Supplies", "Paper"), "pen": ("Office Supplies", "Writing Instruments"),
    "pencil": ("Office Supplies", "Writing Instruments"), "marker": ("Office Supplies", "Writing Instruments"),
    "folder": ("Office Supplies", "Binders"), "binder": ("Office Supplies", "Binders"),
    "stapler": ("Office Supplies", "Appliances"), "tape": ("Office Supplies", "Appliances"),
    "label": ("Office Supplies", "Labels"), "envelope": ("Office Supplies", "Paper"),
    "notebook": ("Office Supplies", "Paper"), "calendar": ("Office Supplies", "Storage"),
    "planner": ("Office Supplies", "Storage"), "ruler": ("Office Supplies", "Art"),
    "scissors": ("Office Supplies", "Art"), "glue": ("Office Supplies", "Art"),
    # Additional
    "toy": ("Office Supplies", "Miscellaneous"), "game": ("Office Supplies", "Miscellaneous"),
    "book": ("Office Supplies", "Miscellaneous"), "gift": ("Office Supplies", "Miscellaneous")
}
FALLBACK_DEFAULT_CATEGORY = ("Office Supplies", "Miscellaneous")
FALLBACK_SEGMENTS = ["Consumer", "Corporate", "Home Office"]
FALLBACK_SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
FALLBACK_REGIONS = ["West", "Central", "South", "East"]

# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def compute_hash(product_name, sales):
    combined = f"{product_name}|{sales}".encode('utf-8')
    return hashlib.sha256(combined).hexdigest()

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

# ----------------------------------------------------------------------
# MAIN TRANSFORMATION
# ----------------------------------------------------------------------
def main():
    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

    # Load reference data if available
    ref_data = load_reference_data(REFERENCE_CSV) if REFERENCE_CSV else None
    if ref_data:
        print(f"✅ Loaded reference data from {REFERENCE_CSV}")
        customers = ref_data["customers"]
        locations = ref_data["locations"]
        category_pairs = ref_data["category_pairs"]
        segments = ref_data["segments"] or FALLBACK_SEGMENTS
        ship_modes = ref_data["ship_modes"] or FALLBACK_SHIP_MODES
        regions = ref_data["regions"] or FALLBACK_REGIONS
    else:
        print("⚠️ No reference file found. Using fallback internal lists.")
        customers = None  # will generate on the fly
        locations = None
        category_pairs = None
        segments = FALLBACK_SEGMENTS
        ship_modes = FALLBACK_SHIP_MODES
        regions = FALLBACK_REGIONS

    # Read input Amazon CSV
    if not Path(INPUT_CSV).exists():
        print(f"❌ Input file not found: {INPUT_CSV}")
        return
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        amazon_rows = list(reader)
    if not amazon_rows:
        print("No input data found.")
        return

    # Determine existing max IDs
    max_row_id, max_order_num = get_max_ids(OUTPUT_CSV)
    print(f"Existing: Row_ID max = {max_row_id}, Order_ID numeric max = {max_order_num}")

    # Output columns
    output_columns = [
        "Row_ID", "Order_ID", "Order_Date", "Ship_Date", "Ship_Mode",
        "Customer_ID", "Customer_Name", "Segment", "Country", "City",
        "State", "Postal_Code", "Region", "Product_ID", "Category",
        "Sub_Category", "Product_Name", "Sales", "Order_Year", "Order_Month",
        "Order_Weekday", "Ship_Year", "Ship_Month", "Ship_Weekday"
    ]

    start_date = datetime(2020, 1, 1)  # wider range for more variety
    end_date = datetime.now()
    output_rows = []
    current_row_id = max_row_id
    current_order_num = max_order_num

    for row in amazon_rows:
        product_name = row["Product_Name"]
        sales = row["Sales"]

        current_row_id += 1
        current_order_num += 1

        # Order date
        order_date = random_date(start_date, end_date)
        # Ship date: 1–14 days later, occasionally missing
        if random.random() < 0.15:
            ship_date = None
            ship_date_str = ""
            ship_year = ship_month = ship_weekday = ""
        else:
            ship_date = order_date + timedelta(days=random.randint(1, 14))
            ship_date_str = ship_date.strftime("%Y-%m-%d")
            ship_year = ship_date.year
            ship_month = ship_date.strftime("%B")
            ship_weekday = ship_date.strftime("%A")

        # Customer
        if ref_data and customers:
            cust_name = random.choice(customers)
            # Generate a customer ID similar to original: first two letters of first name + dash + random number
            first_letter = cust_name[0].lower() if cust_name else 'x'
            last_initial = cust_name.split()[-1][0].lower() if len(cust_name.split()) > 1 else 'x'
            cust_id = f"{first_letter}{last_initial}-{random.randint(10000, 99999)}"
        else:
            first = random.choice(FALLBACK_FIRST_NAMES)
            last = random.choice(FALLBACK_LAST_NAMES)
            cust_name = f"{first} {last}"
            cust_id = f"{first[0].lower()}{last[0].lower()}-{random.randint(10000, 99999)}"

        # Location
        if ref_data and locations:
            city, state, region, postal = random.choice(locations)
        else:
            city = random.choice(list(FALLBACK_CITIES_STATES.keys()))
            state = FALLBACK_CITIES_STATES[city]
            region = random.choice(regions)
            postal = f"{random.randint(10000, 99999)}"

        # Product ID (placeholder)
        prod_id = f"PROD-{random.randint(10000000, 99999999)}"

        # Category / Subcategory
        if ref_data and category_pairs:
            category, subcategory = random.choice(category_pairs)
        else:
            category, subcategory = FALLBACK_DEFAULT_CATEGORY
            for keyword, (cat, subcat) in FALLBACK_CATEGORY_MAP.items():
                if keyword in product_name.lower():
                    category, subcategory = cat, subcat
                    break

        # Order ID (use prefix CA- for older years, US- for recent)
        if order_date.year < 2018:
            prefix = "CA"
        else:
            prefix = "US"
        order_id = f"{prefix}-{order_date.year}-{current_order_num:06d}"

        output_row = {
            "Row_ID": current_row_id,
            "Order_ID": order_id,
            "Order_Date": order_date.strftime("%Y-%m-%d"),
            "Ship_Date": ship_date_str,
            "Ship_Mode": random.choice(ship_modes),
            "Customer_ID": cust_id,
            "Customer_Name": cust_name,
            "Segment": random.choice(segments),
            "Country": "United States",
            "City": city,
            "State": state,
            "Postal_Code": postal,
            "Region": region,
            "Product_ID": prod_id,
            "Category": category,
            "Sub_Category": subcategory,
            "Product_Name": product_name,
            "Sales": sales,
            "Order_Year": order_date.year,
            "Order_Month": order_date.strftime("%B"),
            "Order_Weekday": order_date.strftime("%A"),
            "Ship_Year": ship_year,
            "Ship_Month": ship_month,
            "Ship_Weekday": ship_weekday
        }
        output_rows.append(output_row)

    # Append to output
    write_mode = 'a' if Path(OUTPUT_CSV).exists() else 'w'
    with open(OUTPUT_CSV, mode=write_mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        if write_mode == 'w':
            writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ Transformation complete. Appended {len(output_rows)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
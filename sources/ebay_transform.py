import pandas as pd
import numpy as np

def transform_ebay_data(input_file, output_file):
    print(f"🛠️ Starting transformation on {input_file}...")
    
    # 1. Load the data
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("❌ Error: ebay_scraped.csv not found. Run the scraper first!")
        return

    # 2. Clean the 'Sales' column
    # Convert to numeric, turning any errors (like "Free Shipping" text) into NaN
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    
    # 3. Filter "Junk" and Outliers
    # We remove anything under $50 (usually parts/wheels) 
    # and anything over $2500 (usually bulk lots or scam listings)
    initial_count = len(df)
    df = df[(df['Sales'] >= 50) & (df['Sales'] <= 2500)]
    
    # 4. Add the 'Profit' Column
    # We'll simulate a random profit margin between 12% and 22% 
    # to make the Superstore data look realistic
    df['Profit_Margin'] = np.random.uniform(0.12, 0.22, len(df))
    df['Profit'] = (df['Sales'] * df['Profit_Margin']).round(2)
    
    # 5. Categorization
    # Since we know these are chairs, we can hardcode the Superstore Category
    df['Category'] = 'Furniture'
    df['Sub-Category'] = 'Chairs'

    # 6. Final Cleanup
    # Drop the temporary margin column and remove any rows that had NaN sales
    df = df.drop(columns=['Profit_Margin']).dropna(subset=['Sales'])
    
    # Save the result
    df.to_csv(output_file, index=False)
    
    final_count = len(df)
    print(f"✨ Transformation Complete!")
    print(f"📊 Filtered out {initial_count - final_count} outliers.")
    print(f"💾 Cleaned data saved to: {output_file}")

if __name__ == "__main__":
    transform_ebay_data('../data/raw/ebay_scraped.csv', '../data/processed/ebay_cleaned.csv')
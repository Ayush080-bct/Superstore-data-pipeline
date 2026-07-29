import pandas as pd  # type: ignore
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger=logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).parent.parent
def transform(
    df: pd.DataFrame,
    order_date_col: str = "Order_Date",
    ship_date_col: str = "Ship_Date",
    
    lowercase_categories: bool = True,
    remove_duplicates: bool = True,
) -> pd.DataFrame:
   

    logger.info("Transformation started")
    data = df.copy()#This create a new dataframe object with its own copy of data ,changing this won't affect df
    if order_date_col in data.columns:
        # dayfirst=True: source dates are DD/MM/YYYY. Without this, pandas assumes
        # MM/DD/YYYY and silently coerces ~60% of valid dates to NaT.
        data[order_date_col] = pd.to_datetime(data[order_date_col], dayfirst=True, errors="coerce")
        logger.info(f"Converted {order_date_col} to datetime")
    

    if ship_date_col in data.columns:
        data[ship_date_col] = pd.to_datetime(data[ship_date_col], dayfirst=True, errors="coerce")#error =coerce 
        #fill invalid date which can none data type also with NaT(Not a time)
        logger.info(f"Converted {ship_date_col} to datetime")

   

    data["Order_Year"] = data[order_date_col].dt.year
    data["Order_Month"] = data[order_date_col].dt.month
    data["Order_Weekday"] = data[order_date_col].dt.day_name()
    data["Ship_Year"] = data[ship_date_col].dt.year
    data["Ship_Month"] = data[ship_date_col].dt.month
    data["Ship_Weekday"] = data[ship_date_col].dt.day_name()

    if order_date_col in data.columns and ship_date_col in data.columns:
        data["Shipping_Days"] = (data[ship_date_col] - data[order_date_col]).dt.days
        logger.info("Added Shipping_Days feature")

    logger.info("Date-based feature engineering completed")
    cat_cols = data.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        data[col] = data[col].astype("string").str.strip()
        if lowercase_categories:
            data[col] = data[col].str.lower()
    

    logger.info(f"Cleaned categorical columns: {list(cat_cols)}")


    if remove_duplicates:
        before = len(data)
        data = data.drop_duplicates().reset_index(drop=True)
        after = len(data)
        logger.info(f"Removed duplicates: {before - after} rows dropped")

    logger.info("transformation completed")

    return data


if __name__ == "__main__":
    from  extractors import extract_data
    df = extract_data(str(PROJECT_ROOT / "data" / "raw" / "SuperstoreData.csv"), encoded_system="ISO-8859-1")
    df = transform(df)
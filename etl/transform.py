import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent

def smoothed_target_encode(train_series, target_series, min_samples=5, smoothing=10):
    """
    Compute smoothed target encoding for a categorical column.
    Args:
        train_series: pd.Series of categorical values (training only)
        target_series: pd.Series of target values (Sales)
        min_samples: minimum count before trusting category mean
        smoothing: strength of shrinkage toward global mean
    Returns:
        pd.Series of encoded values
    """
    global_mean = target_series.mean()
    agg = target_series.groupby(train_series).agg(['mean', 'count'])
    smoothing_factor = 1 / (1 + np.exp(-(agg['count'] - min_samples) / smoothing))
    encoded = global_mean * (1 - smoothing_factor) + agg['mean'] * smoothing_factor
    return train_series.map(encoded)


def transform(
    df: pd.DataFrame,
    order_date_col: str = "Order_Date",
    ship_date_col: str = "Ship_Date",
    lowercase_categories: bool = True,
    remove_duplicates: bool = True,
) -> pd.DataFrame:

    logger.info("Transformation started")
    data = df.copy()

    # Convert dates
    if order_date_col in data.columns:
        data[order_date_col] = pd.to_datetime(data[order_date_col], dayfirst=True, errors="coerce")
        logger.info(f"Converted {order_date_col} to datetime")

    if ship_date_col in data.columns:
        data[ship_date_col] = pd.to_datetime(data[ship_date_col], dayfirst=True, errors="coerce")
        logger.info(f"Converted {ship_date_col} to datetime")

    # Date-based features
    data["Order_Year"] = data[order_date_col].dt.year
    data["Order_Month"] = data[order_date_col].dt.month
    data["Order_Weekday"] = data[order_date_col].dt.day_name()
    data["Ship_Year"] = data[ship_date_col].dt.year
    data["Ship_Month"] = data[ship_date_col].dt.month
    data["Ship_Weekday"] = data[ship_date_col].dt.day_name()

    # Shipping days
    data["Shipping_Days"] = (data[ship_date_col] - data[order_date_col]).dt.days
    logger.info("Added Shipping_Days feature")

    # Clean categorical columns
    cat_cols = data.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        data[col] = data[col].astype("string").str.strip()
        if lowercase_categories:
            data[col] = data[col].str.lower()
    logger.info(f"Cleaned categorical columns: {list(cat_cols)}")

    # Smoothed target encoding for high-cardinality columns
    if "Sales" in data.columns:
        for col in ["Product_ID", "Customer_ID", "City"]:
            if col in data.columns:
                data[f"{col}_enc"] = smoothed_target_encode(data[col], data["Sales"])
                logger.info(f"Applied smoothed target encoding to {col}")

    # Remove duplicates
    if remove_duplicates:
        before = len(data)
        data = data.drop_duplicates().reset_index(drop=True)
        after = len(data)
        logger.info(f"Removed duplicates: {before - after} rows dropped")

    logger.info("Transformation completed")
    return data


if __name__ == "__main__":
    from extractors import extract_data
    df = extract_data(str(PROJECT_ROOT / "data" / "raw" / "SuperstoreData.csv"), encoded_system="ISO-8859-1")
    df = transform(df)
    print(df.head())

  
import pandas as pd  # type: ignore
import logging
from typing import Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).parent.parent

def validate_data(
    df: pd.DataFrame,
    required_columns: Optional[list[str]]=None,#in python version 3.9 , we use this but if i have higher version 
    #we use list[str]|None=None
    order_date_col: str = "Order_Date",
    ship_date_col: str = "Ship_Date",
    sales_col: str = "Sales",
) -> bool:
    """Simple validation for transformed data."""

    logger.info("Validation started")

    if required_columns is None:
        required_columns = ["Order_ID", "Order_Date", "Ship_Date", "Customer_ID", "Sales"]

    if df.empty:
        logger.error("DataFrame is empty")
        raise ValueError("Validation failed: DataFrame is empty")
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing columns: {missing_cols}")
        raise ValueError(f"Validation failed: Missing columns {missing_cols}")
    else:
        logger.info("All required columns are present")

    duplicate_rows = int(df.duplicated().sum())
    logger.info(f"Duplicate rows: {duplicate_rows}")

    if sales_col in df.columns:
        negative_sales = int((df[sales_col] < 0).sum())
        logger.info(f"Negative sales rows: {negative_sales}")

    if order_date_col in df.columns and ship_date_col in df.columns:
        date_mask = df[order_date_col].notna() & df[ship_date_col].notna()
        invalid_dates = int(
            (df.loc[date_mask, ship_date_col] < df.loc[date_mask, order_date_col]).sum()
        )
        logger.info(f"Invalid date rows (Ship < Order): {invalid_dates}")

        if invalid_dates > 0:
            logger.error("Ship_Date earlier than Order_Date found")
            raise ValueError(
                f"Validation failed: {invalid_dates} rows have Ship_Date earlier than Order_Date"
            )

    logger.info("Validation passed successfully")
    return True


if __name__ == "__main__":
    from extractors import extract_data
    from transform import transform

    raw_df = extract_data(str(PROJECT_ROOT / "data" / "raw" / "SuperstoreData.csv"), encoded_system="ISO-8859-1")
    transformed_df = transform(raw_df)
    validate_data(transformed_df)
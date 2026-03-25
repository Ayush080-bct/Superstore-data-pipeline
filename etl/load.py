import logging
import pandas as pd  # type: ignore
from pathlib import Path
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()
password=os.getenv("password")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).parent.parent

def save_to_csv(df: pd.DataFrame, file_path: str):
    path = Path(file_path)#create a Path instance ,pathlib.Path gives an object-oriented way
    #to handle paths (methods like .parent, .mkdir, .exists), 
    # while os.path works with plain strings and helper function(like os.path.join)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_csv(path, index=False)
        logger.info(f"Saved CSV: {len(df)} rows, {len(df.columns)} columns")

    except Exception as e:
        logger.error(f"Error saving CSV: {e}")
        raise
# def save_to_postgres(
#         df: pd.DataFrame,
#         password: str,
#         table_name: str = 'superstore_sales',
# ):
#     if not password:
#         logger.warning("PostgreSQL password not configured in .env file. Skipping PostgreSQL save.")
#         return
    
#     db_url = f"postgresql://ayush:{password}@localhost:5432/mydb"
    
#     try:
#         engine = create_engine(db_url)
#         df.to_sql(
#             table_name,
#             engine,
#             if_exists='replace',  # or 'append'
#             index=False
#         )
#         logger.info(f"Loaded data into PostgreSQL table: {table_name}")
#     except Exception as e:
#         logger.warning(f' PostgreSQL error (continuing with CSV): {e}')
       

def load_data(df: pd.DataFrame):
    logger.info("Starting load step")
    
  
    save_to_csv(df, str(PROJECT_ROOT / "data" / "processed" / "cleansuperstoredata.csv"))
  
    # save_to_postgres(df, password=password)
    
    logger.info("Load step completed")
   
    

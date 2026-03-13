import pandas as pd
import logging 
from pathlib import Path
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s -%(levelname)s - %(message)s'
)
logger=logging.getLogger(__name__)
def load_data(file_path:str,encoded_system:str="ISO-8859-1") ->pd.DataFrame:
    file_path=Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found:{file_path}")
    try:
        df=pd.read_csv(file_path,encoding=encoded_system)
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Error Loading file{file_path}:{str(e)}")
        raise
if __name__=="__main__":
    df=load_data("../test.csv",encoded_system="ISO-8859-1")
    print(df.head())
    
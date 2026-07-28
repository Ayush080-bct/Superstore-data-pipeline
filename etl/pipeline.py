import logging
from pathlib import Path

from .extractors import extract_data
from .transform import transform
from .validate import validate_data
from .load import load_data as load



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def run_pipeline():
    logger.info("Pipeline started")

    try:
        raw_data_path = PROJECT_ROOT / "data" / "raw" / "SuperstoreData.csv"
        
        logger.info("Starting extract step")
        df = extract_data(str(raw_data_path), encoded_system="ISO-8859-1")
        logger.info("Starting transform step")
        df = transform(df)        
        logger.info("Starting validation step")
        validate_data(df)
        logger.info("Starting load step")
        load(df)
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
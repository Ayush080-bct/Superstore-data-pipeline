import logging

from .extractors import extract_data
from .transform import transform
from .validate import validate_data
from .load import load_data as load


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("Pipeline started")

    try:
     
        logger.info("Starting extract step")
        df = extract_data("../data/raw/SuperstoreData.csv", encoded_system="ISO-8859-1")
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
# services/csv_loader.py
import pandas as pd
import io
import traceback
from config.settings import REQUIRED_INTERNAL_COLUMNS
from utils.logging_config import get_logger
logger = get_logger(__name__)

def load_csv_event_log(csv_file_obj, column_mapping, timestamp_format=None):
    """Load CSV with column mapping"""
    logger.info("Loading CSV data...")
    try:
        df = pd.read_csv(csv_file_obj, dtype=str)
        
        # Apply column mapping
        standardized_data = {}
        for source_col, standard_name in column_mapping.items():
            if source_col in df.columns:
                standardized_data[standard_name] = df[source_col]
        
        event_df = pd.DataFrame(standardized_data)
        
        # Process timestamp
        timestamp_col = REQUIRED_INTERNAL_COLUMNS['Timestamp']
        if timestamp_col in event_df.columns:
            event_df[timestamp_col] = pd.to_datetime(event_df[timestamp_col], errors='coerce')
            event_df.dropna(subset=[timestamp_col], inplace=True)
        
        logger.info(f"Loaded {len(event_df)} events")
        return event_df
        
    except Exception as e:
        logger.info(f"Error loading CSV: {e}")
        return None

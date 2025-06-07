from pathlib import Path
import pandas as pd


def load_sample_access_logs() -> pd.DataFrame:
    """Load small sample access log data for offline tests."""
    csv_path = Path(__file__).with_name('sample_access_logs.csv')
    return pd.read_csv(csv_path)

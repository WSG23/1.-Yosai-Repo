from typing import List
import pandas as pd

from utils.error_handler import ValidationError
from config.settings import FILE_LIMITS


class CSVValidator:
    """Basic CSV validation utilities."""

    def __init__(self) -> None:
        self.allowed_extensions = FILE_LIMITS.get('allowed_extensions', ['.csv'])
        self.max_file_size = FILE_LIMITS.get('max_file_size', 0)
        self.max_rows = FILE_LIMITS.get('max_rows', 0)

    def validate_file_extension(self, filename: str) -> None:
        if not any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
            allowed = ', '.join(self.allowed_extensions)
            raise ValidationError(f"Invalid file extension. Allowed: {allowed}")

    def validate_file_size(self, file_size: int) -> None:
        if self.max_file_size and file_size > self.max_file_size:
            raise ValidationError(
                f"File size {file_size} exceeds limit of {self.max_file_size} bytes"
            )

    def validate_csv_structure(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValidationError("CSV file is empty")
        if len(df.columns) == 0:
            raise ValidationError("CSV file has no columns")
        if self.max_rows and len(df) > self.max_rows:
            raise ValidationError(
                f"CSV has too many rows: {len(df)} (max {self.max_rows})"
            )

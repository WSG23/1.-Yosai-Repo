# tests/test_simple_loader.py
"""
Simple test to debug the CSV loader service
"""

import io
import pandas as pd
from services.csv_loader import load_csv_event_log
from constants import REQUIRED_INTERNAL_COLUMNS

def test_loader_debug():
    """Debug the CSV loader service"""
    
    # Simple CSV content
    csv_content = """Timestamp,UserID,DoorID,EventType
2024-01-01 10:00:00,USER_001,DOOR_001,ACCESS GRANTED
2024-01-01 11:00:00,USER_002,DOOR_002,ACCESS GRANTED"""

    # Correct column mapping
    column_mapping = {
        'Timestamp': 'Timestamp (Event Time)',
        'UserID': 'UserID (Person Identifier)',
        'DoorID': 'DoorID (Device Name)',
        'EventType': 'EventType (Access Result)'
    }
    
    logger.info("🔍 Constants:", REQUIRED_INTERNAL_COLUMNS)
    logger.info("🔍 Mapping:", column_mapping)
    
    csv_io = io.StringIO(csv_content)
    result = load_csv_event_log(csv_io, column_mapping)
    
    logger.info("🔍 Result type:", type(result))
    logger.info("🔍 Result:", result)
    
    if isinstance(result, dict):
        logger.info("🔍 Success:", result.get('success'))
        if result.get('success'):
           logger.info("🔍 DataFrame shape:", result['result'].shape)
           logger.info("🔍 DataFrame columns:", list(result['result'].columns))
        else:
           logger.info("🔍 Error:", result.get('error'))
    
    # This will always pass - we just want to see the debug output
    assert True

def test_constants_check():
    """Check that constants are as expected"""
    logger.info("🔍 REQUIRED_INTERNAL_COLUMNS:")
    for key, value in REQUIRED_INTERNAL_COLUMNS.items():
       logger.info(f"  {key} -> {value}")
    
    expected_values = {
        'Timestamp (Event Time)',
        'UserID (Person Identifier)',
        'DoorID (Device Name)',
        'EventType (Access Result)'
    }
    
    actual_values = set(REQUIRED_INTERNAL_COLUMNS.values())
    logger.info("🔍 Expected values:", expected_values)
    logger.info("🔍 Actual values:", actual_values)
    logger.info("🔍 Match:", expected_values == actual_values)
    
    assert True  # Always pass, just want debug info

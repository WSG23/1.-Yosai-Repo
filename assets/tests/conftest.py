# tests/conftest.py
"""
Pytest configuration and shared fixtures
"""

import pytest
import pandas as pd
import io
from datetime import datetime, timedelta
from typing import Dict, Any, List
import tempfile
import os
import base64


@pytest.fixture
def sample_access_data():
    """Generate sample access control data for testing"""
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='h')  # Fixed: 'h' instead of 'H'
    doors = ['DOOR_001', 'DOOR_002', 'DOOR_003', 'DOOR_004', 'DOOR_005']
    users = ['USER_001', 'USER_002', 'USER_003', 'USER_004', 'USER_005']
    events = ['ACCESS GRANTED', 'ACCESS DENIED', 'INVALID ACCESS LEVEL']
    
    data = []
    for i in range(1000):
        data.append({
            'Timestamp': dates[i % len(dates)],
            'UserID': users[i % len(users)],
            'DoorID': doors[i % len(doors)],
            'EventType': events[i % len(events)]
        })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_content(sample_access_data):
    """Convert sample data to CSV content"""
    return sample_access_data.to_csv(index=False)


@pytest.fixture
def sample_csv_base64(sample_csv_content):
    """Convert CSV content to base64 format"""
    encoded = base64.b64encode(sample_csv_content.encode('utf-8')).decode('utf-8')
    return f"data:text/csv;base64,{encoded}"


@pytest.fixture
def valid_column_mapping():
    """Valid column mapping for testing - FIXED to use correct display names"""
    return {
        'Timestamp': 'Timestamp (Event Time)',
        'UserID': 'UserID (Person Identifier)', 
        'DoorID': 'DoorID (Device Name)',
        'EventType': 'EventType (Access Result)'
    }


@pytest.fixture
def sample_door_classifications():
    """Sample door classifications for testing"""
    return {
        'DOOR_001': {'floor': '1', 'is_ee': True, 'is_stair': False, 'security': 'green'},
        'DOOR_002': {'floor': '1', 'is_ee': False, 'is_stair': False, 'security': 'yellow'},
        'DOOR_003': {'floor': '2', 'is_ee': False, 'is_stair': True, 'security': 'green'},
        'DOOR_004': {'floor': '2', 'is_ee': False, 'is_stair': False, 'security': 'red'},
        'DOOR_005': {'floor': '1', 'is_ee': True, 'is_stair': False, 'security': 'green'}
    }


@pytest.fixture
def temp_file():
    """Create temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_dash_app():
    """Create a mock Dash app for testing"""
    import dash
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    return app


@pytest.fixture
def sample_csv_with_headers():
    """Sample CSV content with various header formats for mapping tests"""
    return {
        'standard': "Timestamp,UserID,DoorID,EventType\n2024-01-01 10:00:00,USER_001,DOOR_001,ACCESS GRANTED\n",
        'alternative': "Event Time,Person ID,Device Name,Access Result\n2024-01-01 10:00:00,USER_001,DOOR_001,ACCESS GRANTED\n",
        'messy': "  timestamp  , user_id , door_id , event_type  \n2024-01-01 10:00:00,USER_001,DOOR_001,ACCESS GRANTED\n"
    }


@pytest.fixture
def sample_processed_data(sample_access_data):
    """Sample processed data with additional columns for testing"""
    df = sample_access_data.copy()
    df['Date'] = df['Timestamp'].dt.date
    df['DeviceDepthPerDay'] = range(1, len(df) + 1)
    df['EventType_UserDay'] = 'MOVEMENT'
    return df


@pytest.fixture
def sample_device_attributes():
    """Sample device attributes for testing graph components"""
    return pd.DataFrame([
        {'DoorID (Device Name)': 'DOOR_001', 'FinalGlobalDeviceDepth': 1, 'IsOfficialEntrance': True, 'IsGloballyCritical': False, 'Floor': '1', 'SecurityLevel': 'green'},
        {'DoorID (Device Name)': 'DOOR_002', 'FinalGlobalDeviceDepth': 2, 'IsOfficialEntrance': False, 'IsGloballyCritical': False, 'Floor': '1', 'SecurityLevel': 'yellow'},
        {'DoorID (Device Name)': 'DOOR_003', 'FinalGlobalDeviceDepth': 2, 'IsOfficialEntrance': False, 'IsGloballyCritical': False, 'Floor': '2', 'SecurityLevel': 'green'},
        {'DoorID (Device Name)': 'DOOR_004', 'FinalGlobalDeviceDepth': 3, 'IsOfficialEntrance': False, 'IsGloballyCritical': True, 'Floor': '2', 'SecurityLevel': 'red'},
        {'DoorID (Device Name)': 'DOOR_005', 'FinalGlobalDeviceDepth': 1, 'IsOfficialEntrance': True, 'IsGloballyCritical': False, 'Floor': '1', 'SecurityLevel': 'green'}
    ])


@pytest.fixture
def sample_path_data():
    """Sample path data for testing graph visualization"""
    return pd.DataFrame([
        {'SourceDoor': 'DOOR_001', 'TargetDoor': 'DOOR_002', 'TransitionFrequency': 15},
        {'SourceDoor': 'DOOR_002', 'TargetDoor': 'DOOR_003', 'TransitionFrequency': 8},
        {'SourceDoor': 'DOOR_001', 'TargetDoor': 'DOOR_005', 'TransitionFrequency': 12},
        {'SourceDoor': 'DOOR_003', 'TargetDoor': 'DOOR_004', 'TransitionFrequency': 5}
    ])


@pytest.fixture
def sample_error_scenarios():
    """Sample error scenarios for testing error handling"""
    return {
        'missing_columns': pd.DataFrame([
            {'Timestamp': '2024-01-01 10:00:00', 'UserID': 'USER_001', 'EventType': 'ACCESS GRANTED'}
            # Missing DoorID column
        ]),
        'invalid_timestamps': pd.DataFrame([
            {'Timestamp': 'invalid-date', 'UserID': 'USER_001', 'DoorID': 'DOOR_001', 'EventType': 'ACCESS GRANTED'}
        ]),
        'empty_data': pd.DataFrame(columns=['Timestamp', 'UserID', 'DoorID', 'EventType']),
        'malformed_csv': "This is not,a valid,CSV\nfile format"
    }


@pytest.fixture
def mock_file_upload():
    """Mock file upload data for testing upload handlers"""
    csv_content = "Timestamp,UserID,DoorID,EventType\n2024-01-01 10:00:00,USER_001,DOOR_001,ACCESS GRANTED\n"
    encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    
    return {
        'contents': f"data:text/csv;base64,{encoded}",
        'filename': 'test_data.csv',
        'last_modified': datetime.now().timestamp()
    }


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings"""
    return {
        'TESTING': True,
        'DEBUG': True,
        'LOG_LEVEL': 'DEBUG',
        'GRAPH_PROCESSING_CONFIG': {
            'num_floors': 2,
            'top_n_heuristic_entrances': 3,
            'primary_positive_indicator': "ACCESS GRANTED",
            'invalid_phrases_exact': ["INVALID ACCESS LEVEL"],
            'invalid_phrases_contain': ["NO ENTRY MADE"],
            'same_door_scan_threshold_seconds': 10,
            'ping_pong_threshold_minutes': 1
        }
    }
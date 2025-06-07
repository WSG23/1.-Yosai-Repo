import base64
from pathlib import Path

from services.secure_file_handler import SecureFileHandler


SAMPLE_PATH = Path(__file__).resolve().parent.parent / 'fixtures' / 'sample_access_logs.csv'


def _load_sample_base64() -> str:
    data = SAMPLE_PATH.read_text()
    encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    return f'data:text/csv;base64,{encoded}'


def test_secure_file_handler_accepts_csv():
    handler = SecureFileHandler()
    result = handler.process_uploaded_file(_load_sample_base64(), 'sample.csv')
    assert result['success'] is True
    assert 'file_io' in result


def test_secure_file_handler_rejects_bad_extension():
    handler = SecureFileHandler()
    result = handler.process_uploaded_file(_load_sample_base64(), 'bad.txt')
    assert result['success'] is False

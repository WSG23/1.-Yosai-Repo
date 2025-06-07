import io
from services.csv_loader import load_csv_event_log


def test_load_csv_event_log(sample_csv_content, valid_column_mapping):
    csv_io = io.StringIO(sample_csv_content)
    df = load_csv_event_log(csv_io, valid_column_mapping)
    assert df is not None
    assert not df.empty


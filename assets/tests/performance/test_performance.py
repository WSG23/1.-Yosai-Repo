import time

from services.onion_model import run_onion_model_processing
from tests.fixtures.sample_data import load_sample_access_logs

CONFIG = {
    'num_floors': 2,
    'top_n_heuristic_entrances': 3,
    'primary_positive_indicator': 'ACCESS GRANTED',
    'invalid_phrases_exact': [],
    'invalid_phrases_contain': [],
    'same_door_scan_threshold_seconds': 10,
    'ping_pong_threshold_minutes': 1,
}


def test_onion_model_runs_quickly():
    df = load_sample_access_logs()
    start = time.time()
    enriched, attrs, viz, paths = run_onion_model_processing(df, CONFIG)
    duration = time.time() - start
    assert not enriched.empty
    assert duration < 5

import os
import time
import pytest
import json
from dash.testing.application_runners import import_app


@pytest.fixture
def app_runner():
    app = import_app('app')
    return app


def test_generate_shows_analytics(dash_duo, app_runner):
    dash_duo.start_server(app_runner)

    upload_input = dash_duo.wait_for_element('input[type="file"]')
    sample_path = os.path.join(os.path.dirname(__file__), 'data', 'sample.csv')
    upload_input.send_keys(sample_path)

    dash_duo.wait_for_element('#confirm-and-generate-button')
    dash_duo.find_element('#confirm-and-generate-button').click()

    analytic_container = dash_duo.wait_for_element('#analytic-stats-container', timeout=10)
    assert analytic_container.value_of_css_property('display') != 'none'


def test_enhanced_stats_store_populated(dash_duo, app_runner):
    dash_duo.start_server(app_runner)

    upload_input = dash_duo.wait_for_element('input[type="file"]')
    sample_path = os.path.join(os.path.dirname(__file__), 'data', 'sample.csv')
    upload_input.send_keys(sample_path)

    dash_duo.wait_for_element('#confirm-and-generate-button')
    dash_duo.find_element('#confirm-and-generate-button').click()

    dash_duo.wait_for_text_to_equal('#processing-status', 'Analysis complete', timeout=10)

    store = dash_duo.wait_for_element('#enhanced-stats-data-store', timeout=5)
    store_data = store.get_attribute('data-dash-store') or store.text
    metrics = json.loads(store_data) if store_data else {}

    assert metrics, 'Enhanced stats store should contain metrics'
    assert len(metrics.keys()) >= 10


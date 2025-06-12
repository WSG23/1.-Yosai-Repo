import os
import time
import pytest
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


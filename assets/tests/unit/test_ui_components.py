import pytest
from dash import dcc, html

from ui.components.upload import create_simple_upload_component, EnhancedUploadComponent
from ui.components.common import LoadingComponent


def test_create_simple_upload_component():
    comp = create_simple_upload_component('/icon.png')
    assert isinstance(comp, EnhancedUploadComponent)


def test_upload_area_has_correct_id():
    comp = create_simple_upload_component('/icon.png')
    upload_area = comp.create_upload_area()
    assert isinstance(upload_area, dcc.Upload)
    assert upload_area.id == 'upload-data'


def test_loading_spinner_returns_div():
    spinner = LoadingComponent.create_spinner()
    assert isinstance(spinner, html.Div)


def test_progress_bar_returns_div():
    bar = LoadingComponent.create_progress_bar(50)
    assert isinstance(bar, html.Div)

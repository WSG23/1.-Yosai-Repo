import pandas as pd
from services.cytoscape_prep import (
    prepare_path_visualization_data,
    prepare_cytoscape_elements,
)


def test_prepare_path_visualization_data(sample_path_data):
    df = prepare_path_visualization_data(sample_path_data)
    assert not df.empty
    assert set(df.columns) == {"Door1", "Door2", "PathWidth"}


def test_prepare_cytoscape_elements(sample_device_attributes, sample_path_data):
    viz = prepare_path_visualization_data(sample_path_data)
    nodes, edges = prepare_cytoscape_elements(sample_device_attributes, viz, sample_path_data)
    assert len(nodes) > 0
    assert len(edges) > 0

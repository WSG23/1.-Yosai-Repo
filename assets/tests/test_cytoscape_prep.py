from services.cytoscape_prep import prepare_path_visualization_data
from tests.fixtures.sample_data import load_sample_access_logs


def test_prepare_path_visualization_data_from_file():
    df = load_sample_access_logs()
    # create simple paths DataFrame
    paths = df.assign(SourceDoor=df['DoorID'], TargetDoor=df['DoorID'])
    paths['TransitionFrequency'] = 1
    viz = prepare_path_visualization_data(paths[['SourceDoor', 'TargetDoor', 'TransitionFrequency']])
    assert not viz.empty
    assert set(viz.columns) == {'Door1', 'Door2', 'PathWidth'}

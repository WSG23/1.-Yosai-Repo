# Create ui/components/debug_component.py
from dash import html, dcc, Input, Output, callback

def create_debug_panel():
    """Create debug panel to check data flow"""
    return html.Div([
        html.H4("Debug Info", style={'color': '#fff'}),
        html.P(id="debug-info", style={'color': '#ccc', 'fontSize': '0.8rem'}),
        html.P(id="metrics-debug", style={'color': '#ccc', 'fontSize': '0.8rem'})
    ], style={
        'position': 'fixed',
        'top': '10px',
        'right': '10px',
        'backgroundColor': '#333',
        'padding': '10px',
        'borderRadius': '5px',
        'zIndex': '9999'
    })

@callback(
    [Output('debug-info', 'children'), Output('metrics-debug', 'children')],
    [Input('enhanced-metrics-store', 'data'), Input('processed-data-store', 'data')]
)
def update_debug_info(metrics_data, processed_data):
    metrics_info = f"Metrics: {len(metrics_data) if metrics_data else 0} items"
    processed_info = f"Processed: {len(processed_data) if processed_data else 0} rows"
    return metrics_info, processed_info
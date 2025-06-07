# graph_config.py

GRAPH_PROCESSING_CONFIG = {
    'num_floors': 1,
    'top_n_heuristic_entrances': 5,
    'primary_positive_indicator': '',
    'invalid_phrases_exact': [],
    'invalid_phrases_contain': [],
    'same_door_scan_threshold_seconds': 100,
    'ping_pong_threshold_minutes': 1
}

# ✅ UI display constants with consistent container sizing
UI_STYLES = {
    'hide': {'display': 'none'},
    'show_block': {
        'display': 'block',
        'width': '90%',           # ← Match setup container width
        'maxWidth': '1200px',     # ← Optional: max width limit
        'margin': '0 auto',       # ← Center containers
        'padding': '20px',        # ← Consistent padding
        'marginBottom': '20px'    # ← Space between containers
    },
    'show_flex_stats': {
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-around',
        'marginBottom': '30px',
        'width': '90%',           # ← Match other containers
        'margin': '0 auto 30px auto'  # ← Center and add bottom margin
    },
    # ✅ Specific container styles that match setup container
    'container_standard': {
        'display': 'block',
        'width': '90%',           # ← Same as interactive-setup-container
        'maxWidth': '1200px',     # ← Consistent max width
        'margin': '0 auto',       # ← Centered
        'padding': '20px',        # ← Consistent padding
        'backgroundColor': '#ffffff',  # ← Optional: background color
        'borderRadius': '8px',         # ← Optional: rounded corners
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',  # ← Optional: subtle shadow
        'marginBottom': '20px'    # ← Space between containers
    },
    'status_standard': {
        'display': 'block',
        'width': '90%',           # ← Same width as other containers
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '15px 20px',   # ← Slightly less padding for status
        'textAlign': 'center',    # ← Center status text
        'backgroundColor': '#f8f9fa',  # ← Light background for status
        'borderRadius': '8px',
        'marginBottom': '20px',
        'fontSize': '16px',       # ← Clear readable text
        'fontWeight': '500'       # ← Slightly bold
     
    },

    'header_matching': {
        'fontSize': '18px',
        'fontWeight': '400', 
        'color': '#ffffff',
        'fontFamily': 'system-ui, -apple-system, sans-serif',
        'textAlign': 'center',
        'margin': '0 0 30px 0',
        'padding': '20px 0',
        'borderBottom': '1px solid #374151'
    },

}
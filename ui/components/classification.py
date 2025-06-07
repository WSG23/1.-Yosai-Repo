# ui/components/classification.py - FIXED VERSION (Complete with all methods)
"""
Door classification component with simplified toggle switch - FIXED
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from ui.themes.style_config import (
    COLORS,
    SPACING,
    BORDER_RADIUS,
    SHADOWS,
    TYPOGRAPHY,
    CLASSIFICATION_STYLES,
)


class ClassificationComponent:
    """Centralized classification component with simplified toggle - COMPLETE"""
    
    def __init__(self):
        # Define Security Levels for the slider (0-10 range)
        self.security_levels_map = {
            0: {"label": "0", "color": COLORS['border'], "value": "unclassified"},
            1: {"label": "1", "color": COLORS['border'], "value": "unclassified"},
            2: {"label": "2", "color": COLORS['border'], "value": "unclassified"},
            3: {"label": "3", "color": COLORS['success'], "value": "green"},
            4: {"label": "4", "color": COLORS['success'], "value": "green"},
            5: {"label": "5", "color": COLORS['success'], "value": "green"},
            6: {"label": "6", "color": COLORS['warning'], "value": "yellow"},
            7: {"label": "7", "color": COLORS['warning'], "value": "yellow"},
            8: {"label": "8", "color": COLORS['critical'], "value": "red"},
            9: {"label": "9", "color": COLORS['critical'], "value": "red"},
            10: {"label": "10", "color": COLORS['critical'], "value": "red"},
        }
        
        # Reverse map for pre-selecting from stored data
        self.reverse_security_map = {v['value']: k for k, v in self.security_levels_map.items()}
    
    def create_entrance_verification_section(self):
        """Creates the complete entrance verification UI section with simplified toggle"""
        return html.Div(
            id='entrance-verification-ui-section', 
            style={'display': 'none', 'padding': '0', 'margin': '0 auto', 'textAlign': 'center'}, 
            children=[
                self.create_facility_setup_card(),
                self.create_door_classification_card()  # This method was missing!
            ]
        )
    
    def create_facility_setup_card(self):
        """Creates Step 2: Facility Setup card with modern slider and simplified toggle"""
        return html.Div([
            html.H4("Step 2: Facility Setup", 
                   style={'color': COLORS['text_primary'], 'textAlign': 'center', 'marginBottom': '16px'}),
            
            # Floors Slider Row
            self.create_floors_slider_row(),
            
            # Simplified Toggle Row (no Bootstrap switch)
            self.create_simplified_toggle_row()
            
        ], style=CLASSIFICATION_STYLES['setup_card'])
    
    def create_floors_slider_row(self):
        """Creates the modern floors slider"""
        return html.Div([
            html.Label(
                "How many floors are in the facility?", 
                style={
                    'color': COLORS['text_primary'],
                    'fontWeight': TYPOGRAPHY['font_bold'],
                    'fontSize': '1rem',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'display': 'block'
                }
            ),
            
            # Modern Slider (0-100 floors)
            dcc.Slider(
                id="num-floors-input",
                min=0,
                max=100,
                step=5,
                value=4,
                marks={i: str(i) for i in range(0, 101, 5)},
                tooltip={"always_visible": False, "placement": "bottom"},
                updatemode="drag",
                className="modern-floor-slider"
            ),
            
            # Live display of slider value
            html.Div(
                id="num-floors-display",
                children="4 floors",  # Default text
                style={
                    "fontSize": "0.9rem",
                    "color": COLORS['text_secondary'],
                    "marginTop": "6px",
                    "textAlign": "center",
                    "fontWeight": "600"
                }
            ),
            
            # Helper text
            html.Small(
                "Count floors above ground including mezzanines and secure zones.", 
                style={
                    'color': COLORS['text_tertiary'],
                    'fontSize': '0.8rem',
                    'textAlign': 'center',
                    'display': 'block',
                    'marginTop': '4px',
                    'marginBottom': '24px'
                }
            )
        ])
    
    def create_simplified_toggle_row(self):
        """Creates a simplified toggle using styled radio items - CLEAN VERSION"""
        return html.Div([
            html.Label(
                "Enable Manual Door Classification?", 
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': '1rem',
                    'marginBottom': '12px',
                    'textAlign': 'center',
                    'display': 'block',
                    'fontWeight': TYPOGRAPHY['font_bold']
                }
            ),
            
            # Clean RadioItems - NO CONFLICTING STYLES
            dcc.RadioItems(
                id='manual-map-toggle',
                options=[
                    {'label': 'No', 'value': 'no'}, 
                    {'label': 'Yes', 'value': 'yes'}
                ],
                value='no',  # Default to No
                inline=True,
                # Remove ALL styling - let CSS and JavaScript handle everything
                className='clean-radio-toggle'
            ),
            
            html.Small(
                "Choose 'Yes' to manually set security levels for each door, or 'No' for automatic classification.", 
                style={
                    'color': COLORS['text_tertiary'],
                    'fontSize': '0.8rem',
                    'textAlign': 'center',
                    'display': 'block',
                    'marginTop': '8px'
                }
            )
        ])
    
    def create_door_classification_card(self):
        """Creates Step 3: Door Classification card - MISSING METHOD FIXED"""
        return html.Div(
            id="door-classification-table-container",
            style={'display': 'none'},
            children=[
                html.Div([
                    html.H4("Step 3: Door Classification", 
                           style={'color': COLORS['text_primary'], 'textAlign': 'center', 'marginBottom': '12px'}),
                    html.P(
                        "Assign a security level to each door below:", 
                        style={'color': COLORS['text_primary'], 'textAlign': 'center', 'marginBottom': '8px'}
                    ),
                    html.Div(id="door-classification-table")
                ], style=CLASSIFICATION_STYLES['classification_card'])
            ]
        )
    
    def create_scrollable_door_list(self, doors_to_classify, existing_classifications=None, num_floors=3):
        """Creates a scrollable door classification list with header"""
        if not doors_to_classify:
            return [html.P("No doors available for classification.", 
                          style={'color': COLORS['text_secondary'], 'textAlign': 'center'})]
        
        if existing_classifications is None:
            existing_classifications = {}
        
        # Generate floor options
        floor_options = [{'label': str(i), 'value': str(i)} for i in range(1, num_floors + 1)]
        
        # Create header row
        header_row = html.Div([
            html.Div("Door ID", style={
                'fontWeight': TYPOGRAPHY['font_semibold'], 
                'color': COLORS['text_primary'],
                'flex': '0 0 200px'
            }),
            html.Div("Floor", style={
                'fontWeight': TYPOGRAPHY['font_semibold'], 
                'color': COLORS['text_primary'],
                'flex': '0 0 80px'
            }),
            html.Div("Entry/Exit", style={
                'fontWeight': TYPOGRAPHY['font_semibold'], 
                'color': COLORS['text_primary'],
                'flex': '0 0 100px'
            }),
            html.Div("Stairway", style={
                'fontWeight': TYPOGRAPHY['font_semibold'], 
                'color': COLORS['text_primary'],
                'flex': '0 0 100px'
            }),
            html.Div("Security Level", style={
                'fontWeight': TYPOGRAPHY['font_semibold'], 
                'color': COLORS['text_primary'],
                'flex': '1'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': SPACING['base'],
            'backgroundColor': COLORS['border'],
            'borderRadius': f"{BORDER_RADIUS['md']} {BORDER_RADIUS['md']} 0 0",
            'gap': SPACING['sm']
        })
        
        # Create door rows
        door_rows = []
        for door_id in sorted(doors_to_classify):
            door_row = self._create_door_row(
                door_id, 
                existing_classifications.get(door_id, {}), 
                floor_options
            )
            door_rows.append(door_row)
        
        # Return complete structure
        return [
            header_row,
            html.Div(
                door_rows,
                style={
                    'maxHeight': '600px',
                    'overflowY': 'auto',
                    'padding': SPACING['sm'],
                    'backgroundColor': COLORS['background'],
                    'borderRadius': f"0 0 {BORDER_RADIUS['md']} {BORDER_RADIUS['md']}",
                    'border': f"1px solid {COLORS['border']}",
                    'borderTop': 'none'
                },
                className='door-list-scrollable'
            )
        ]
    
    def _create_door_row(self, door_id, current_classification, floor_options):
        """Creates a single door classification row with horizontal layout"""
        # Pre-select values based on existing classifications
        pre_sel_floor = current_classification.get('floor', '1')
        pre_sel_door_type = current_classification.get('door_type', 'none')
        pre_sel_security_val = current_classification.get('security_level', 5)
        
        return html.Div([
            # Door ID Label
            html.Div(
                door_id, 
                style={
                    'fontWeight': TYPOGRAPHY['font_semibold'], 
                    'color': COLORS['text_primary'],
                    'fontSize': TYPOGRAPHY['text_base'],
                    'flex': '0 0 200px',
                    'display': 'flex',
                    'alignItems': 'center'
                }
            ),
            
            # Floor Dropdown
            html.Div([
                dcc.Dropdown(
                    id={'type': 'floor-select', 'index': door_id},
                    options=floor_options,
                    value=pre_sel_floor,
                    clearable=False,
                    style={
                        'backgroundColor': COLORS['surface'],
                        'borderColor': COLORS['border'],
                        'color': COLORS['text_primary'],
                        'width': '80px'
                    }
                )
            ], style={'flex': '0 0 80px', 'marginRight': SPACING['sm']}),
            
            # Entry/Exit Toggle
            html.Div([
                dcc.RadioItems(
                    id={'type': 'door-type-toggle', 'index': door_id},
                    options=[{'label': 'Entry/Exit', 'value': 'entry_exit'}],
                    value='entry_exit' if pre_sel_door_type == 'entry_exit' else None,
                    className='door-type-pill',
                    labelStyle={
                        'backgroundColor': COLORS['success'] if pre_sel_door_type == 'entry_exit' else COLORS['surface'],
                        'color': 'white' if pre_sel_door_type == 'entry_exit' else COLORS['text_secondary'],
                        'borderRadius': BORDER_RADIUS['full'],
                        'padding': f"{SPACING['xs']} {SPACING['sm']}",
                        'border': f"1px solid {COLORS['border']}",
                        'cursor': 'pointer',
                        'fontSize': TYPOGRAPHY['text_sm'],
                        'transition': 'all 0.2s ease',
                        'display': 'inline-block',
                        'textAlign': 'center'
                    }
                )
            ], style={'flex': '0 0 100px', 'marginRight': SPACING['sm']}),
            
            # Stairway Toggle
            html.Div([
                dcc.RadioItems(
                    id={'type': 'stairway-toggle', 'index': door_id},
                    options=[{'label': 'Stairway', 'value': 'stairway'}],
                    value='stairway' if pre_sel_door_type == 'stairway' else None,
                    className='door-type-pill',
                    labelStyle={
                        'backgroundColor': COLORS['success'] if pre_sel_door_type == 'stairway' else COLORS['surface'],
                        'color': 'white' if pre_sel_door_type == 'stairway' else COLORS['text_secondary'],
                        'borderRadius': BORDER_RADIUS['full'],
                        'padding': f"{SPACING['xs']} {SPACING['sm']}",
                        'border': f"1px solid {COLORS['border']}",
                        'cursor': 'pointer',
                        'fontSize': TYPOGRAPHY['text_sm'],
                        'transition': 'all 0.2s ease',
                        'display': 'inline-block',
                        'textAlign': 'center'
                    }
                )
            ], style={'flex': '0 0 100px', 'marginRight': SPACING['sm']}),
            
            # Security Level Slider
            html.Div([
                dcc.Slider(
                    id={'type': 'security-level-slider', 'index': door_id},
                    min=0,
                    max=10,
                    step=1,
                    value=pre_sel_security_val,
                    marks={i: {
                        'label': str(i),
                        'style': {
                            'color': COLORS['text_secondary'],
                            'fontSize': TYPOGRAPHY['text_xs']
                        }
                    } for i in [0, 2, 4, 6, 8, 10]},
                    tooltip={"placement": "bottom", "always_visible": False},
                    className="security-range-slider"
                )
            ], style={'flex': '1', 'minWidth': '150px', 'paddingTop': '10px'})
            
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': SPACING['base'],
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['md'],
            'border': f"1px solid {COLORS['border']}",
            'marginBottom': SPACING['sm'],
            'boxShadow': SHADOWS['sm'],
            'transition': 'all 0.2s ease',
            'gap': SPACING['sm']
        }, className='door-classification-card')
    
    def get_security_levels_map(self):
        """Returns the security levels mapping"""
        return self.security_levels_map
    
    def get_reverse_security_map(self):
        """Returns the reverse security mapping"""
        return self.reverse_security_map


# Factory functions for easy component creation
def create_classification_component():
    """Factory function to create classification component instance"""
    return ClassificationComponent()

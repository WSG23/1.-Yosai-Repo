# ui/components/classification_modular.py
"""
Refactored classification component using new modular architecture
"""
from typing import Dict, Any, Optional, List
from dash import html, dcc
import dash_bootstrap_components as dbc

from ui.core.interfaces import StatefulComponent, ComponentConfig
from ui.core.config_manager import get_component_config
from ui.themes.style_config import (
    COLORS,
    SPACING,
    BORDER_RADIUS,
    SHADOWS,
    TYPOGRAPHY,
    CLASSIFICATION_STYLES,
    ENHANCED_TYPOGRAPHY,
    ENHANCED_SPACING,
    ENHANCED_SHADOWS,
    get_enhanced_card_style,
    get_enhanced_button_style,
)


class ModularClassificationComponent(StatefulComponent):
    """Modular classification component with clean separation of concerns"""

    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id)
        self.props = kwargs

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
        self.reverse_security_map = {v['value']: k for k, v in self.security_levels_map.items()}

        def _validate_config(self) -> None:


            """Validate required configuration - Fixed to handle missing settings gracefully"""


            required_settings = ['security_levels', 'classification_method', 'auto_classify']
        


            for setting in required_settings:


                if self.get_setting(setting) is None:


                    print(f"Warning: Missing setting '{setting}', using defaults")


                    # Set default values instead of raising errors


                    defaults = {'security_levels': [0, 1, 2, 3], 'classification_method': 'manual', 'auto_classify': False}


                    if setting in defaults:


                        self.config.settings[setting] = defaults[setting]

    def render(self, **props) -> html.Div:
        """Render the classification component"""
        return self.create_entrance_verification_section()

    # --- Legacy UI methods migrated below ---

    def create_entrance_verification_section(self) -> html.Div:
        """Creates the complete entrance verification UI section"""
        return html.Div(
            id='entrance-verification-ui-section',
            style={'display': 'none', 'padding': '0', 'margin': '0 auto', 'textAlign': 'center'},
            children=[
                self.create_facility_setup_card(),
                self.create_door_classification_card()
            ]
        )

    def create_facility_setup_card(self) -> html.Div:
        """Enhanced facility setup with modern visual design"""
        card_style = get_enhanced_card_style('premium', interactive=True)

        return html.Div([
            html.Div(
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'marginBottom': ENHANCED_SPACING['xl'],
                },
                children=[
                    html.Div(
                        "2",
                        style={
                            'width': '40px',
                            'height': '40px',
                            'borderRadius': '50%',
                            'backgroundColor': COLORS['accent'],
                            'color': COLORS['text_on_accent'],
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'fontSize': TYPOGRAPHY['text_lg'],
                            'fontWeight': TYPOGRAPHY['font_bold'],
                            'marginRight': ENHANCED_SPACING['md'],
                            'boxShadow': ENHANCED_SHADOWS['accent'],
                        }
                    ),
                    html.H4(
                        "Facility Setup",
                        style={
                            'color': COLORS['text_primary'],
                            'fontSize': ENHANCED_TYPOGRAPHY['text_xl'],
                            'fontWeight': TYPOGRAPHY['font_semibold'],
                            'margin': '0',
                            'letterSpacing': ENHANCED_TYPOGRAPHY['tracking_wide'],
                        }
                    )
                ]
            ),

            self.create_floors_slider_row(),
            self.create_simplified_toggle_row()

        ], style=card_style, className='enhanced-card-hover enhanced-focus')

    def create_floors_slider_row(self) -> html.Div:
        """Enhanced floors slider with better visual design"""
        return html.Div([
            html.Label(
                "How many floors are in the facility?",
                style={
                    'color': COLORS['text_primary'],
                    'fontWeight': TYPOGRAPHY['font_semibold'],
                    'fontSize': TYPOGRAPHY['text_lg'],
                    'marginBottom': ENHANCED_SPACING['md'],
                    'textAlign': 'center',
                    'display': 'block',
                }
            ),

            html.Div(
                style={
                    'backgroundColor': COLORS['surface_elevated'],
                    'borderRadius': BORDER_RADIUS['xl'],
                    'padding': ENHANCED_SPACING['lg'],
                    'border': f"1px solid {COLORS['border']}",
                    'boxShadow': SHADOWS['inner'],
                    'marginBottom': ENHANCED_SPACING['xl'],
                },
                children=[
                    dcc.Slider(
                        id="floor-slider",
                        min=0,
                        max=100,
                        step=5,
                        value=4,
                        marks={i: str(i) for i in range(0, 101, 5)},
                        tooltip={"always_visible": False, "placement": "bottom"},
                        updatemode="drag",
                        className="enhanced-floor-slider"
                    ),

                    html.Div(
                        id="floor-slider-value",
                        children="4 floors",
                        style={
                            "fontSize": TYPOGRAPHY['text_lg'],
                            "color": COLORS['accent'],
                            "marginTop": ENHANCED_SPACING['md'],
                            "textAlign": "center",
                            "fontWeight": TYPOGRAPHY['font_semibold'],
                            "padding": ENHANCED_SPACING['sm'],
                            "backgroundColor": f"{COLORS['accent']}10",
                            "borderRadius": BORDER_RADIUS['lg'],
                            "border": f"1px solid {COLORS['accent']}30",
                        }
                    )
                ]
            ),

            html.Small(
                "Count floors above ground including mezzanines and secure zones.",
                style={
                    'color': COLORS['text_tertiary'],
                    'fontSize': TYPOGRAPHY['text_sm'],
                    'textAlign': 'center',
                    'display': 'block',
                    'marginTop': ENHANCED_SPACING['md'],
                    'fontStyle': 'italic',
                    'lineHeight': ENHANCED_TYPOGRAPHY['leading_relaxed'],
                }
            )
        ])

    def create_simplified_toggle_row(self) -> html.Div:
        """Creates a simplified toggle using styled radio items"""
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

            dcc.RadioItems(
                id='manual-map-toggle',
                options=[
                    {'label': 'No', 'value': 'no'},
                    {'label': 'Yes', 'value': 'yes'}
                ],
                value='no',
                inline=True,
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

    def create_door_classification_card(self) -> html.Div:
        """Creates Step 3: Door Classification card"""
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

        floor_options = [{'label': str(i), 'value': str(i)} for i in range(1, num_floors + 1)]

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

        door_rows = []
        for door_id in sorted(doors_to_classify):
            door_row = self._create_door_row(
                door_id,
                existing_classifications.get(door_id, {}),
                floor_options
            )
            door_rows.append(door_row)

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
                className='door-list-scrollable',
            )
        ]

    def _create_door_row(self, door_id, current_classification, floor_options):
        """Creates a single door classification row with horizontal layout"""
        pre_sel_floor = current_classification.get('floor', '1')
        pre_sel_door_type = current_classification.get('door_type', 'none')
        pre_sel_security_val = current_classification.get('security_level', 5)

        return html.Div([
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


# Factory functions

def create_modular_classification_component(component_id: Optional[str] = None, **props):
    """Factory function to create modular classification component"""
    config = get_component_config('classification')
    return ModularClassificationComponent(config, component_id, **props)


def register_modular_classification_component():
    """Register modular classification component with global registry"""
    from ui.core.component_registry import register_component

    register_component('classification_modular', ModularClassificationComponent)

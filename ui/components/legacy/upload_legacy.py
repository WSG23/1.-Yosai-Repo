# ui/components/upload.py
"""
Upload component - Fixed for actual directory structure
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional

# Import from actual structure

from config.settings import DEFAULT_ICONS
from ui.themes.style_config import (
    COLORS,
    SPACING,
    TYPOGRAPHY,
    UPLOAD_STYLES,
    get_upload_style,
    get_interactive_setup_style,
)


class EnhancedUploadComponent:
    """Enhanced upload component for actual directory structure"""
    
    def __init__(self, icon_default: str, icon_success: str, icon_fail: str):
        self.icons = {
            'default': icon_default,
            'success': icon_success, 
            'fail': icon_fail
        }
    
    def create_upload_area(self):
        """Creates upload area"""
        return dcc.Upload(
            id='upload-data',
            children=self.create_upload_content(),
            style=get_upload_style("initial"),
            multiple=False,
            accept='.csv,.json',
            className="upload-area hover-lift"
        )
    
    def create_upload_content(self):
        """Creates upload content"""
        return html.Div([
            html.Div([
                html.Img(
                    id='upload-icon',
                    src=self.icons['default'],
                    style=UPLOAD_STYLES['icon']
                )
            ], style={'textAlign': 'center'}),
            
            html.H3("Drop your CSV or JSON file here", style={
                'margin': '0',
                'fontSize': TYPOGRAPHY['text_lg'],
                'fontWeight': TYPOGRAPHY['font_semibold'],
                'color': COLORS['text_primary'],
                'marginBottom': SPACING['xs']
            }),
            
            html.P("or click to browse", style={
                'margin': '0',
                'fontSize': TYPOGRAPHY['text_sm'],
                'color': COLORS['text_secondary'],
            }),
        ], style=UPLOAD_STYLES['content'])
    
    def get_upload_style(self, state="initial"):
        """Wrapper for style_config.get_upload_style"""
        return get_upload_style(state)
    
    def get_upload_styles(self):
        """Returns styles dictionary for handlers"""
        return {
            'initial': get_upload_style('initial'),
            'success': get_upload_style('success'),
            'error': get_upload_style('error'),
        }
    
    def create_interactive_setup_container(self):
        """Creates setup container"""
        return html.Div(
            id='interactive-setup-container',
            style=get_interactive_setup_style(False),
            children=[
                # Mapping section placeholder
                html.Div(id='mapping-ui-section', style={'display': 'none'}),
                
                # Classification section placeholder  
                html.Div(id='entrance-verification-ui-section', style={'display': 'none'}),
                
                # Generate button
                self.create_generate_button()
            ]
        )
    
    def create_generate_button(self):
        """Creates generate button"""
        return dbc.Button(
            'Confirm Selections & Generate Onion Model',
            id='confirm-and-generate-button',
            n_clicks=0,
            color='primary',
            size='lg',
            className='w-100',
            style=UPLOAD_STYLES['generate_button']
        )
    
    def _get_interactive_setup_style(self, visible=False):
        """Wrapper for style_config.get_interactive_setup_style"""
        return get_interactive_setup_style(visible)
    
    def _get_button_style(self, variant='primary'):
        """Get button style"""
        return UPLOAD_STYLES['generate_button'].copy()


# Factory functions for easy component creation
def create_enhanced_upload_component(icon_default: str, icon_success: str, icon_fail: str):
    """Factory function to create enhanced upload component"""
    return EnhancedUploadComponent(icon_default, icon_success, icon_fail)

def create_upload_component(icon_default: str, icon_success: str, icon_fail: str):
    """Alias for backward compatibility"""
    return create_enhanced_upload_component(icon_default, icon_success, icon_fail)

def create_simple_upload_component(icon_path: str):
    """Create simple upload component with single icon"""
    return EnhancedUploadComponent(icon_path, icon_path, icon_path)


# ui/components/secure_upload_handlers.py
"""
Secure upload handlers with comprehensive validation - FIXED VERSION
"""

import base64
import pandas as pd
import io
import json
import traceback
from typing import Dict, Any, Optional, Tuple
from dash import Input, Output, State, html, no_update

from config.settings import REQUIRED_INTERNAL_COLUMNS
from utils.logging_config import get_logger
from ui.themes.style_config import UPLOAD_STYLES, get_interactive_setup_style

logger = get_logger(__name__)

class SecureUploadHandlers:
    """Enhanced upload handlers with security validation"""

    def __init__(self, app, component, icons: Dict[str, str]):
        self.app = app
        self.component = component
        self.icons = icons
        logger.info("SecureUploadHandlers initialized")

    def register_callbacks(self) -> None:
        """Register upload callbacks with validation"""

        @self.app.callback(
            [
                Output('uploaded-file-store', 'data'),
                Output('csv-headers-store', 'data'),
                Output('dropdown-mapping-area', 'children'),
                Output('confirm-header-map-button', 'style'),
                Output('interactive-setup-container', 'style'),
                Output('processing-status', 'children'),
                Output('upload-icon', 'src'),
                Output('upload-data', 'style'),
                Output('entrance-verification-ui-section', 'style'),
                Output('door-classification-table-container', 'style', allow_duplicate=True),
                Output('graph-output-container', 'style'),
                Output('stats-panels-container', 'style'),
                Output('yosai-custom-header', 'style', allow_duplicate=True),
                Output('onion-graph', 'elements'),
                Output('all-doors-from-csv-store', 'data'),
                Output('upload-icon', 'style')
            ],
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename'), State('column-mapping-store', 'data')],
            prevent_initial_call='initial_duplicate'
        )
        def handle_secure_upload(contents, filename, saved_col_mappings_json):
            """Handle file upload with validation"""

            # Get styles from upload component
            upload_styles = self.component.get_upload_styles()
            
            # Initial state values
            hide_style = {'display': 'none'}
            show_interactive_setup_style = get_interactive_setup_style(True)
            confirm_button_style_hidden = UPLOAD_STYLES['generate_button'].copy()
            confirm_button_style_hidden['display'] = 'none'
            upload_icon_style = UPLOAD_STYLES['icon']

            if contents is None:
                return (
                    None, None, [],  # file store, headers, dropdown area
                    confirm_button_style_hidden,  # confirm button style
                    hide_style,  # interactive setup container
                    "",  # processing status
                    self.icons['default'],  # upload icon src
                    upload_styles['initial'],  # upload box style
                    hide_style, hide_style, hide_style, hide_style,  # various containers
                    hide_style,  # yosai header
                    [],  # graph elements
                    None,  # all doors store
                    upload_icon_style  # upload icon style
                )

            try:
                logger.info(f"Processing upload: {filename}")
                
                # Decode file content
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                if filename.lower().endswith('.csv'):
                    df_full_for_doors = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif filename.lower().endswith('.json'):
                    df_full_for_doors = pd.read_json(io.StringIO(decoded.decode('utf-8')))
                else:
                    raise ValueError("Uploaded file must be a CSV or JSON file.")
                headers = df_full_for_doors.columns.tolist()
                
                if not headers:
                    raise ValueError("CSV has no headers.")
                
                # Process column mappings
                if isinstance(saved_col_mappings_json, str):
                    saved_col_mappings = json.loads(saved_col_mappings_json)
                else:
                    saved_col_mappings = saved_col_mappings_json or {}
                
                header_key = json.dumps(sorted(headers))
                loaded_col_map_prefs = saved_col_mappings.get(header_key, {})
                
                # Create temporary mapping for door extraction
                temp_mapping_for_doors = {}
                for csv_h_selected, internal_k in loaded_col_map_prefs.items():
                    if internal_k in REQUIRED_INTERNAL_COLUMNS:
                        temp_mapping_for_doors[csv_h_selected] = REQUIRED_INTERNAL_COLUMNS[internal_k]
                    else:
                        temp_mapping_for_doors[csv_h_selected] = internal_k
                
                # Extract unique doors for classification
                df_copy = df_full_for_doors.copy()
                df_copy.rename(columns=temp_mapping_for_doors, inplace=True)
                
                DOORID_COL_DISPLAY = REQUIRED_INTERNAL_COLUMNS['DoorID']
                
                if DOORID_COL_DISPLAY in df_copy.columns:
                    all_unique_doors = sorted(df_copy[DOORID_COL_DISPLAY].astype(str).unique().tolist())
                    logger.info(f"Extracted {len(all_unique_doors)} unique doors for classification.")
                else:
                    logger.warning(f"'{DOORID_COL_DISPLAY}' column not found after preliminary mapping.")
                    all_unique_doors = []
                
                # Create mapping dropdowns
                mapping_dropdowns = self._create_mapping_dropdowns(headers, loaded_col_map_prefs)
                
                # Success response
                confirm_button_style_visible = confirm_button_style_hidden.copy()
                confirm_button_style_visible['display'] = 'block'
                
                processing_status_msg = f"Step 1: Confirm Header Mapping for '{filename}'."
                
                return (
                    contents,  # uploaded file store
                    headers,  # csv headers store
                    mapping_dropdowns,  # dropdown mapping area
                    confirm_button_style_visible,  # confirm button style
                    show_interactive_setup_style,  # interactive setup container
                    processing_status_msg,  # processing status
                    self.icons['success'],  # upload icon src
                    upload_styles['success'],  # upload box style
                    hide_style, hide_style, hide_style, hide_style,  # various containers
                    hide_style,  # yosai header
                    [],  # graph elements
                    all_unique_doors,  # all doors store
                    upload_icon_style  # upload icon style
                )
                
            except Exception as e:
                logger.error(f"Upload error for {filename}: {str(e)}")
                traceback.print_exc()
                
                error_message = f"Error processing '{filename}': {str(e)}"
                processing_status_msg = error_message
                
                return (
                    None, None,  # file store, headers
                    [html.P(processing_status_msg, style={'color': 'red'})],  # dropdown area
                    confirm_button_style_hidden,  # confirm button style
                    show_interactive_setup_style,  # interactive setup container
                    processing_status_msg,  # processing status
                    self.icons['fail'],  # upload icon src
                    upload_styles['error'],  # upload box style
                    hide_style, hide_style, hide_style, hide_style,  # various containers
                    hide_style,  # yosai header
                    [],  # graph elements
                    None,  # all doors store
                    upload_icon_style  # upload icon style
                )

    def _create_mapping_dropdowns(self, headers, loaded_col_map_prefs):
        """Create dropdown components for column mapping"""
        try:
            from ui.components.mapping import create_mapping_component
            mapping_component = create_mapping_component()
            return mapping_component.create_mapping_dropdowns(headers, loaded_col_map_prefs)
        except ImportError:
            # Fallback if mapping component not available
            return [html.P("Mapping component not available", style={'color': 'orange'})]


def create_secure_upload_handlers(app, upload_component, icons: Dict[str, str]) -> SecureUploadHandlers:
    """Factory function to create secure upload handlers"""
    logger.info("Creating secure upload handlers")
    return SecureUploadHandlers(app, upload_component, icons)
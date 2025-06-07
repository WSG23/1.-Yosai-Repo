# ui/handlers/upload_handlers.py
"""
Upload callback handlers - extracted from upload_callbacks.py
Separated business logic from UI definitions
"""

import base64
import io
import pandas as pd
import json
import traceback
from dash import Input, Output, State, html, dcc

# Import UI components
from ui.components.upload import create_upload_component
from ui.themes.graph_styles import upload_icon_img_style

from ui.themes.style_config import UPLOAD_STYLES, get_interactive_setup_style
from config.settings import REQUIRED_INTERNAL_COLUMNS


from utils.logging_config import get_logger
logger = get_logger(__name__)                 

class UploadHandlers:
    """Handles all upload-related callbacks and business logic"""
    
    def __init__(self, app, upload_component, icon_paths):
        self.app = app
        self.upload_component = upload_component
        self.icon_upload_default = icon_paths['default']
        self.icon_upload_success = icon_paths['success']
        self.icon_upload_fail = icon_paths['fail']
        
    def register_callbacks(self):
        """Register all upload-related callbacks"""
        self._register_upload_handler()
        
    def _register_upload_handler(self):
        """Main upload handler callback"""
        @self.app.callback(
            [
                Output('uploaded-file-store', 'data'),
                Output('csv-headers-store', 'data'),
                Output('dropdown-mapping-area', 'children'),
                Output('confirm-header-map-button', 'style', allow_duplicate=True),
                Output('interactive-setup-container', 'style'),
                Output('processing-status', 'children', allow_duplicate=True),
                Output('upload-icon', 'src'),
                Output('upload-data', 'style'),
                Output('entrance-verification-ui-section', 'style', allow_duplicate=True),
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
        def handle_upload_and_show_header_mapping(contents, filename, saved_col_mappings_json):
            return self._process_upload(contents, filename, saved_col_mappings_json)
    
    def _process_upload(self, contents, filename, saved_col_mappings_json):
        """Core upload processing logic"""
        # Get styles from upload component
        upload_styles = self.upload_component.get_upload_styles()
        
        # Initial state values
        initial_values = self._get_initial_state_values(upload_styles)
        
        if contents is None:
            return initial_values
            
        try:
            # Process the uploaded file
            result = self._process_csv_file(contents, filename, saved_col_mappings_json)
            
            if result['success']:
                return self._create_success_response(result, upload_styles, filename)
            else:
                return self._create_error_response(result, upload_styles, filename)
                
        except Exception as e:
            logger.info(f"Error in handle_upload: {e}")
            traceback.print_exc()
            error_result = {'error': str(e), 'success': False}
            return self._create_error_response(error_result, upload_styles, filename)
    
    def _process_csv_file(self, contents, filename, saved_col_mappings_json):
        """Process and validate uploaded CSV or JSON file"""
        try:
            # Decode the file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)# Determine file type and load accordingly
            # Determine file type and load accordingly
            if filename.lower().endswith('.csv'):
                df_full_for_doors = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif filename.lower().endswith('.json'):
                df_full_for_doors = pd.read_json(io.StringIO(decoded.decode('utf-8')))
            else:
                raise ValueError("Uploaded file must be a CSV or JSON file.")
            headers = df_full_for_doors.columns.tolist()
            
            if not headers:
                raise ValueError("CSV or JSON has no headers.")
            
            # Process column mappings
            mapping_result = self._process_column_mappings(
                df_full_for_doors, headers, saved_col_mappings_json
            )
            
            # Extract unique doors for classification
            all_unique_doors = self._extract_unique_doors(df_full_for_doors, mapping_result)
            
            # Create mapping dropdowns
            mapping_dropdowns = self._create_mapping_dropdowns(headers, mapping_result)
            
            return {
                'success': True,
                'contents': contents,
                'headers': headers,
                'mapping_dropdowns': mapping_dropdowns,
                'all_unique_doors': all_unique_doors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_column_mappings(self, df, headers, saved_col_mappings_json):
        """Process saved column mappings"""
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
        
        return {
            'saved_mappings': saved_col_mappings,
            'current_preferences': loaded_col_map_prefs,
            'temp_mapping': temp_mapping_for_doors
        }
    
    def _extract_unique_doors(self, df, mapping_result):
        """Extract unique door IDs from the CSV"""
        temp_mapping = mapping_result['temp_mapping']
        df_copy = df.copy()
        df_copy.rename(columns=temp_mapping, inplace=True)
        
        DOORID_COL_DISPLAY = REQUIRED_INTERNAL_COLUMNS['DoorID']
        
        if DOORID_COL_DISPLAY in df_copy.columns:
            all_unique_doors = sorted(df_copy[DOORID_COL_DISPLAY].astype(str).unique().tolist())
            logger.info(f"DEBUG: Extracted {len(all_unique_doors)} unique doors for classification.")
            return all_unique_doors
        else:
            logger.info(f"Warning: '{DOORID_COL_DISPLAY}' column not found after preliminary mapping.")
            return []
    
    def _create_mapping_dropdowns(self, headers, mapping_result):
        """Create dropdown components for column mapping"""
        from ui.components.mapping import create_mapping_component
        
        mapping_component = create_mapping_component()
        loaded_col_map_prefs = mapping_result['current_preferences']
        
        return mapping_component.create_mapping_dropdowns(headers, loaded_col_map_prefs)
    
    def _get_initial_state_values(self, upload_styles):
        """Get initial state values for all outputs"""
        hide_style = {'display': 'none'}
        show_interactive_setup_style = get_interactive_setup_style(True)
        confirm_button_style_hidden = UPLOAD_STYLES['generate_button'].copy()
        confirm_button_style_hidden['display'] = 'none'
        
        return (
            None, None, [],  # file store, headers, dropdown area
            confirm_button_style_hidden,  # confirm button style
            hide_style,  # interactive setup container
            "",  # processing status
            self.icon_upload_default,  # upload icon src
            upload_styles['initial'],  # upload box style
            hide_style, hide_style, hide_style, hide_style,  # various containers
            hide_style,  # yosai header
            [],  # graph elements
            None,  # all doors store
            upload_icon_img_style  # upload icon style
        )
    
    def _create_success_response(self, result, upload_styles, filename):
        """Create response for successful upload"""
        hide_style = {'display': 'none'}
        show_interactive_setup_style = get_interactive_setup_style(True)
        confirm_button_style_visible = UPLOAD_STYLES['generate_button']
        
        processing_status_msg = f"Step 1: Confirm Header Mapping for '{filename}'."
        
        return (
            result['contents'],  # uploaded file store
            result['headers'],  # csv headers store
            result['mapping_dropdowns'],  # dropdown mapping area
            confirm_button_style_visible,  # confirm button style
            show_interactive_setup_style,  # interactive setup container
            processing_status_msg,  # processing status
            self.icon_upload_success,  # upload icon src
            upload_styles['success'],  # upload box style
            hide_style, hide_style, hide_style, hide_style,  # various containers
            hide_style,  # yosai header
            [],  # graph elements
            result['all_unique_doors'],  # all doors store
            upload_icon_img_style  # upload icon style
        )
    
    def _create_error_response(self, result, upload_styles, filename):
        """Create response for failed upload"""
        hide_style = {'display': 'none'}
        show_interactive_setup_style = get_interactive_setup_style(True)
        confirm_button_style_hidden = UPLOAD_STYLES['generate_button'].copy()
        confirm_button_style_hidden['display'] = 'none'
        
        error_message = result.get('error', 'Unknown error')
        processing_status_msg = f"Error processing '{filename}': {error_message}"
        
        return (
            None, None,  # file store, headers
            [html.P(processing_status_msg, style={'color': 'red'})],  # dropdown area
            confirm_button_style_hidden,  # confirm button style
            show_interactive_setup_style,  # interactive setup container
            processing_status_msg,  # processing status
            self.icon_upload_fail,  # upload icon src
            upload_styles['fail'],  # upload box style
            hide_style, hide_style, hide_style, hide_style,  # various containers
            hide_style,  # yosai header
            [],  # graph elements
            None,  # all doors store
            upload_icon_img_style  # upload icon style
        )


# Factory function for easy handler creation
def create_upload_handlers(app, upload_component, icon_paths):
    """Factory function to create upload handlers"""
    return UploadHandlers(app, upload_component, icon_paths)
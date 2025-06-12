# ui/handlers/upload_handlers.py
"""Unified upload handlers with optional security features."""

import base64
import io
import pandas as pd
import json
import traceback
import uuid
from dash import Input, Output, State, html

from ui.themes.style_config import UPLOAD_STYLES, get_interactive_setup_style, COLORS
from ui.themes.graph_styles import upload_icon_img_style
from config.settings import REQUIRED_INTERNAL_COLUMNS


from utils.logging_config import get_logger
from utils.error_handler import ValidationError, DataProcessingError
from utils.helpers import process_large_csv
from utils.secure_validator import validate_upload_security
logger = get_logger(__name__)                 

class UploadHandlers:
    """Handle upload-related callbacks with optional security checks."""

    def __init__(self, app, upload_component, icon_paths, *, secure: bool = False, max_file_size: int | None = None):
        self.app = app
        self.upload_component = upload_component
        self.icons = icon_paths
        self.secure = secure
        self.max_file_size = max_file_size
        logger.info(
            "UploadHandlers initialized (secure=%s, max_file_size=%s)",
            self.secure,
            self.max_file_size,
        )
        
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
                Output('mapping-ui-section', 'style', allow_duplicate=True),
                Output('interactive-setup-container', 'style'),
                # Store status messages in a single location
                Output('status-message-store', 'data', allow_duplicate=True),
                Output('upload-icon', 'src'),
                Output('upload-data', 'style'),
                Output('entrance-verification-ui-section', 'style', allow_duplicate=True),
                Output('door-classification-table-container', 'style', allow_duplicate=True),
                Output('graph-output-container', 'style', allow_duplicate=True),
                Output('stats-panels-container', 'style', allow_duplicate=True),
                Output('yosai-custom-header', 'style', allow_duplicate=True),
                Output('onion-graph', 'elements', allow_duplicate=True),
                Output('all-doors-from-csv-store', 'data'),
                Output('upload-icon', 'style'),
                Output('processed-data-store', 'data')
            ],
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename'), State('column-mapping-store', 'data')],
            prevent_initial_call='initial_duplicate'
        )
        def handle_upload_and_show_header_mapping(contents, filename, saved_col_mappings_json):
            return self._process_upload(contents, filename, saved_col_mappings_json)
    
    def _process_upload(self, contents, filename, saved_col_mappings_json):
        """Core upload processing logic with detailed error handling"""
        upload_styles = self.upload_component.get_upload_styles()
        initial_values = self._get_initial_state_values(upload_styles)

        if contents is None:
            return initial_values

        try:
            logger.info("Processing upload: %s", filename)
            result = self._process_csv_file(contents, filename, saved_col_mappings_json)

            if result['success']:
                return self._create_success_response(result, upload_styles, filename)
            else:
                return self._create_error_response(result, upload_styles, filename)

        except FileNotFoundError:
            logger.warning("File not found during upload: %s", filename)
            return self._create_error_response({
                'error': f"File '{filename}' could not be found or accessed",
                'success': False,
                'error_type': 'file_not_found'
            }, upload_styles, filename)
        except PermissionError:
            logger.error("Permission denied accessing file: %s", filename)
            return self._create_error_response({
                'error': f"Permission denied: Cannot access '{filename}'. Check file permissions.",
                'success': False,
                'error_type': 'permission_denied'
            }, upload_styles, filename)
        except pd.errors.EmptyDataError:
            logger.warning("Empty CSV file uploaded: %s", filename)
            return self._create_error_response({
                'error': f"The file '{filename}' appears to be empty. Please upload a file with data.",
                'success': False,
                'error_type': 'empty_file'
            }, upload_styles, filename)
        except pd.errors.ParserError as e:
            logger.error("CSV parsing error for %s: %s", filename, str(e))
            return self._create_error_response({
                'error': f"Unable to parse '{filename}'. Please ensure it's a valid CSV file with proper formatting.",
                'success': False,
                'error_type': 'parse_error'
            }, upload_styles, filename)
        except UnicodeDecodeError as e:
            logger.error("Encoding error for %s: %s", filename, str(e))
            return self._create_error_response({
                'error': f"File encoding issue with '{filename}'. Please save as UTF-8 and try again.",
                'success': False,
                'error_type': 'encoding_error'
            }, upload_styles, filename)
        except ValidationError as e:
            logger.warning("Validation error for %s: %s", filename, str(e))
            return self._create_error_response({
                'error': f"Data validation failed: {str(e)}",
                'success': False,
                'error_type': 'validation_error'
            }, upload_styles, filename)
        except MemoryError:
            logger.error("Memory error processing %s: file too large", filename)
            return self._create_error_response({
                'error': f"File '{filename}' is too large to process. Please try a smaller file or contact support.",
                'success': False,
                'error_type': 'memory_error'
            }, upload_styles, filename)
        except ValueError as e:
            error_msg = str(e)
            if "too large" in error_msg.lower():
                logger.warning("File size limit exceeded for %s", filename)
                return self._create_error_response({
                    'error': f"File '{filename}' exceeds the size limit. Please upload a smaller file.",
                    'success': False,
                    'error_type': 'file_too_large'
                }, upload_styles, filename)
            logger.error("Value error processing %s: %s", filename, error_msg)
            return self._create_error_response({
                'error': f"Invalid data in '{filename}': {error_msg}",
                'success': False,
                'error_type': 'invalid_data'
            }, upload_styles, filename)
        except json.JSONDecodeError as e:
            logger.error("JSON parsing error for %s: %s", filename, str(e))
            return self._create_error_response({
                'error': f"Invalid JSON format in configuration. Line {e.lineno}: {e.msg}",
                'success': False,
                'error_type': 'json_error'
            }, upload_styles, filename)
        except TimeoutError as e:
            logger.error("Timeout processing %s: %s", filename, str(e))
            return self._create_error_response({
                'error': f"Processing '{filename}' timed out. Please try again or use a smaller file.",
                'success': False,
                'error_type': 'timeout_error'
            }, upload_styles, filename)
        except Exception as e:
            error_id = str(uuid.uuid4())[:8]
            logger.error(
                "Unexpected error processing %s (ID: %s): %s",
                filename, error_id, str(e),
                extra={
                    'error_id': error_id,
                    'filename': filename,
                    'error_type': type(e).__name__,
                    'traceback': traceback.format_exc()
                }
            )
            return self._create_error_response({
                'error': f"An unexpected error occurred processing '{filename}'. Error ID: {error_id}. Please try again or contact support.",
                'success': False,
                'error_type': 'unexpected_error',
                'error_id': error_id
            }, upload_styles, filename)
    
    def _process_csv_file(self, contents, filename, saved_col_mappings_json):
        """Process and validate uploaded CSV or JSON file with improved error handling"""

        try:
            if ',' not in contents:
                raise ValueError("Invalid file format: missing data separator")

            content_type, content_string = contents.split(',', 1)
            try:
                decoded = base64.b64decode(content_string)
            except Exception as e:
                raise ValueError("File encoding error: unable to decode file data") from e

            if self.secure:
                validation = validate_upload_security(decoded, filename)
                if not validation.get('is_valid'):
                    reason = validation.get('errors', ['failed security validation'])[0]
                    raise ValidationError(f"Security validation failed: {reason}")

            if self.secure and self.max_file_size and len(decoded) > self.max_file_size:
                file_size_mb = len(decoded) / (1024 * 1024)
                max_size_mb = self.max_file_size / (1024 * 1024)
                raise ValueError(
                    f"File too large: {file_size_mb:.1f}MB exceeds limit of {max_size_mb:.1f}MB"
                )

            file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
            allowed_extensions = ['csv', 'txt', 'json']  # Added 'json'
            if file_extension not in allowed_extensions:
                raise ValueError(
                    f"Unsupported file type: '.{file_extension}'. Please upload a CSV or JSON file."
                )

            try:
                decoded_string = decoded.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    decoded_string = decoded.decode('latin1')
                    logger.warning("File %s used latin1 encoding, converted to UTF-8", filename)
                except UnicodeDecodeError as e:
                    raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end,
                                         "Unable to decode file. Please save as UTF-8 encoding.")

            # Parse file based on extension
            try:
                if file_extension == 'json':
                    df = pd.read_json(io.StringIO(decoded_string))
                else:
                    df = pd.read_csv(io.StringIO(decoded_string))
            except pd.errors.EmptyDataError:
                raise pd.errors.EmptyDataError(f"{file_extension.upper()} file is empty or contains no data")
            except ValueError as e:
                if file_extension == 'json':
                    raise ValueError(f"JSON format error: {str(e)}")
                else:
                    raise pd.errors.ParserError(f"CSV format error: {str(e)}")
            except Exception as e:
                raise DataProcessingError(f"Unable to read {file_extension.upper()} data: {str(e)}") from e

            if df.empty:
                raise ValidationError("CSV file contains no data rows")
            if len(df.columns) == 0:
                raise ValidationError("CSV file contains no columns")
            if len(df.columns) > 1000:
                raise ValidationError("CSV has too many columns (>1000). Please check file format.")

            if len(df) > 1000000:
                logger.warning("Large file detected: %d rows in %s", len(df), filename)

            logger.info("Successfully processed %s: %d rows, %d columns", filename, len(df), len(df.columns))

            mapping_result = self._process_column_mappings(df, df.columns.tolist(), saved_col_mappings_json)
            all_unique_doors = self._extract_unique_doors(df, mapping_result)
            mapping_dropdowns = self._create_mapping_dropdowns(df.columns.tolist(), mapping_result)

            processed_data = {
                'filename': filename,
                'dataframe': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'upload_timestamp': pd.Timestamp.now().isoformat(),
            }

            return {
                'success': True,
                'contents': contents,
                'headers': df.columns.tolist(),
                'mapping_dropdowns': mapping_dropdowns,
                'all_unique_doors': all_unique_doors,
                'processed_data': processed_data,
            }

        except (ValidationError, ValueError, pd.errors.EmptyDataError,
                pd.errors.ParserError, UnicodeDecodeError):
            raise
        except Exception as e:
            raise DataProcessingError(f"Unexpected error processing CSV: {str(e)}") from e
    
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
        try:
            from ui.components.mapping import create_mapping_component
            mapping_component = create_mapping_component()
            loaded_col_map_prefs = mapping_result['current_preferences']
            return mapping_component._create_mapping_dropdowns(headers, loaded_col_map_prefs)
        except ImportError:
            return [html.P("Mapping component not available", style={'color': 'orange'})]
    
    def _get_initial_state_values(self, upload_styles):
        """Get initial state values for all outputs"""
        hide_style = {'display': 'none'}
        show_interactive_setup_style = get_interactive_setup_style(True)
        confirm_button_style_hidden = UPLOAD_STYLES['generate_button'].copy()
        confirm_button_style_hidden['display'] = 'none'
        
        return (
            None, None, [],  # file store, headers, dropdown area
            confirm_button_style_hidden,  # confirm button style
            hide_style,  # mapping-ui-section style (hidden)
            hide_style,  # interactive setup container
            "",  # status message store
            self.icons['default'],  # upload icon src
            upload_styles['initial'],  # upload box style
            hide_style, hide_style, hide_style, hide_style,  # various containers
            hide_style,  # yosai header
            [],  # graph elements
            None,  # all doors store
            upload_icon_img_style,  # upload icon style
            None  # processed data store

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
            {
                'display': 'block',
                'padding': '25px',
                'backgroundColor': COLORS['surface'],
                'borderRadius': '12px',
                'margin': '20px auto',
            },  # mapping-ui-section style
            show_interactive_setup_style,  # interactive setup container
            processing_status_msg,  # status message store
            self.icons['success'],  # upload icon src
            upload_styles['success'],  # upload box style
            hide_style, hide_style, hide_style, hide_style,  # various containers
            hide_style,  # yosai header
            [],  # graph elements
            result['all_unique_doors'],  # all doors store
            upload_icon_img_style,  # upload icon style
            result.get('processed_data')  # processed data store

        )
    
    def _create_error_response(self, result, upload_styles, filename):
        """Create response for failed upload with user friendly message"""
        hide_style = {'display': 'none'}
        show_interactive_setup_style = get_interactive_setup_style(True)
        confirm_button_style_hidden = UPLOAD_STYLES['generate_button'].copy()
        confirm_button_style_hidden['display'] = 'none'

        error_message = result.get('error', 'Unknown error occurred')
        error_type = result.get('error_type', 'generic_error')
        error_id = result.get('error_id', '')

        user_messages = {
            'file_not_found': "\ud83d\udcc1 File not found. Please try uploading again.",
            'empty_file': "\ud83d\udccb The uploaded file is empty. Please upload a file with data.",
            'parse_error': "\u26a0\ufe0f File format issue. Please ensure it's a valid CSV file.",
            'encoding_error': "\ud83d\udd24 Text encoding issue. Please save your file as UTF-8.",
            'file_too_large': "\ud83d\udccd File is too large. Please try a smaller file.",
            'memory_error': "\ud83d\udcbe File too large for processing. Please use a smaller file.",
            'validation_error': "\u2705 Data validation failed. Please check your data format.",
            'permission_denied': "\ud83d\udd12 Permission denied. Please check file access rights.",
            'timeout_error': "\u23f1\ufe0f Processing timed out. Please try again with a smaller file.",
            'json_error': "\ud83d\udcc4 Invalid JSON format in configuration file.",
            'unexpected_error': f"\u274c Unexpected error occurred. Error ID: {error_id}"
        }

        user_friendly_message = user_messages.get(error_type, error_message)

        processing_status_msg = f"{user_friendly_message}"

        logger.error(
            "Error processing upload: %s (type: %s, file: %s)",
            error_message, error_type, filename
        )

        return (
            None, None,
            [html.Div([
                html.P(user_friendly_message, style={
                    'color': COLORS['critical'],
                    'fontWeight': 'bold',
                    'marginBottom': '10px'
                }),
                html.P(f"File: {filename}", style={
                    'color': COLORS['text_secondary'],
                    'fontSize': '0.9em'
                }),
                html.P(f"Error ID: {error_id}", style={
                    'color': COLORS['text_tertiary'],
                    'fontSize': '0.8em',
                    'fontFamily': 'monospace'
                }) if error_id else html.Div()
            ])],
            confirm_button_style_hidden,
            hide_style,
            show_interactive_setup_style,
            processing_status_msg,
            self.icons['fail'],
            upload_styles['error'],
            hide_style, hide_style, hide_style, hide_style,
            hide_style,
            [],
            None,
            upload_icon_img_style,
            None

        )


# Factory function for easy handler creation
def create_upload_handlers(app, upload_component, icon_paths, *, secure: bool = False, max_file_size: int | None = None):
    """Factory function to create upload handlers"""
    return UploadHandlers(app, upload_component, icon_paths, secure=secure, max_file_size=max_file_size)

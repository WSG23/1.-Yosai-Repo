# ui/components/upload_modular.py
"""
Refactored upload component using new modular architecture
"""
from typing import Dict, Any, Optional, Union, Tuple
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash
import base64
import io
import pandas as pd
import json

from ui.core.interfaces import StatefulComponent, ComponentConfig
from ui.core.dependency_injection import inject, DataService, EventBus
from ui.core.config_manager import get_component_config

class ModularUploadComponent(StatefulComponent):
    """Modular upload component with clean separation of concerns"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id)
        self.upload_id = f"{self.component_id}-upload"
        self.status_id = f"{self.component_id}-status"
        self.content_id = f"{self.component_id}-content"
        
        # Store any additional props
        self.props = kwargs
        
        def _validate_config(self) -> None:

        
            """Validate required configuration - Fixed to handle missing settings gracefully"""

        
            required_settings = ['max_file_size', 'allowed_extensions', 'secure_validation', 'upload_timeout']
        

        
            for setting in required_settings:

        
                value = self.get_setting(setting)
            

        
                # Handle field name compatibility

        
                if value is None and setting == 'allowed_extensions':

        
                    value = self.get_setting('accepted_types')  # Try alternative name

        
                    if value is not None:

        
                        self.config.settings[setting] = value
            

        
                if value is None:

        
                    print(f"Warning: Missing setting '{setting}', using defaults")

        
                    # Set default values instead of raising errors

        
                    defaults = {'max_file_size': 52428800, 'allowed_extensions': ['.csv', '.json'], 'secure_validation': True, 'upload_timeout': 30}

        
                    if setting in defaults:

        
                        self.config.settings[setting] = defaults[setting]
    
    def render(self, **props) -> html.Div:
        """Render the upload component"""
        return html.Div([
            self._create_upload_area(),
            self._create_status_area(),
            self._create_content_display()
        ], id=self.component_id, style=self._get_container_style())
    
    def _create_upload_area(self) -> dcc.Upload:
        """Create the upload area"""
        return dcc.Upload(
            id=self.upload_id,
            children=self._create_upload_content(),
            style=self._get_upload_style(),
            multiple=False,
            accept=",".join(self.get_setting('accepted_types', ['.csv', '.json']))
        )
    
    def _create_upload_content(self) -> html.Div:
        """Create upload area content"""
        return html.Div([
            html.Div(self.get_icon('upload'), style={'fontSize': '48px', 'marginBottom': '16px'}),
            html.H4("Drag and Drop or Click to Upload", style={'margin': '16px 0 8px 0'}),
            html.P(f"Supports {', '.join(self.get_setting('accepted_types', ['.csv', '.json']))}", 
                  style={'margin': '0', 'opacity': '0.7'})
        ], style={'textAlign': 'center', 'padding': '32px'})
    
    def _create_status_area(self) -> html.Div:
        """Create status display area"""
        return html.Div(id=self.status_id, style={'margin': '16px 0'})
    
    def _create_content_display(self) -> html.Div:
        """Create content display area"""
        return html.Div(id=self.content_id)
    
    def _get_container_style(self) -> Dict[str, Any]:
        """Get container styling"""
        base_style = {
            'margin': '16px 0',
            'borderRadius': self.get_style('border_radius') or '8px',
        }
        return {**base_style, **self.get_style('container')}
    
    def _get_upload_style(self) -> Dict[str, Any]:
        """Get upload area styling"""
        base_style = {
            'width': '100%',
            'height': self.get_style('min_height') or '200px',
            'lineHeight': self.get_style('min_height') or '200px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': self.get_style('border_radius') or '8px',
            'borderColor': self.get_style('border_color') or '#e5e7eb',
            'textAlign': 'center',
            'backgroundColor': '#f8f9fa',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease'
        }
        return {**base_style, **self.get_style('upload_area')}
    
    def register_callbacks(self, app: dash.Dash) -> None:
        """Register component callbacks"""
        
        @app.callback(
            [Output(self.status_id, 'children'),
             Output(self.content_id, 'children')],
            [Input(self.upload_id, 'contents')],
            [State(self.upload_id, 'filename'),
             State(self.upload_id, 'last_modified')]
        )
        def handle_upload(contents, filename, last_modified):
            if contents is None:
                return no_update, no_update
            
            return self._handle_upload_with_injection(contents, filename, last_modified)
    
    def _handle_upload_with_injection(self, contents, filename, last_modified):
        """Handle file upload with dependency injection wrapper"""
        
        from ui.core.dependency_injection import get_container
        container = get_container()
        
        try:
            data_service = container.get(DataService)
            event_bus = container.get(EventBus)
        except ValueError:
            from ui.core.dependency_injection import InMemoryDataService, SimpleEventBus
            data_service = InMemoryDataService()
            event_bus = SimpleEventBus()
        
        return self._handle_upload_callback(data_service, event_bus, contents, filename, last_modified)
    
    def _handle_upload_callback(self, data_service: DataService, event_bus: EventBus,
                              contents, filename, last_modified):
        """Handle file upload with dependency injection"""
        if contents is None:
            return no_update, no_update
        
        try:
            validation_result = self._validate_file(contents, filename)
            if not validation_result['valid']:
                return self._create_error_status(validation_result['error']), no_update
            
            processed_data = self._process_file(contents, filename)
            
            data_service.save_data(f"{self.component_id}_data", processed_data)
            
            event_bus.publish('file_uploaded', {
                'component_id': self.component_id,
                'filename': filename,
                'data': processed_data
            })
            
            row_count = processed_data.get('row_count', 0)
            return (
                self._create_success_status(filename, row_count),
                self._create_data_preview(processed_data)
            )
            
        except Exception as e:
            return self._create_error_status(str(e)), no_update
    
    def _validate_file(self, contents: str, filename: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        if not filename:
            return {'valid': False, 'error': 'No filename provided'}
        
        accepted_types = self.get_setting('accepted_types', ['.csv', '.json'])
        if not any(filename.lower().endswith(ext) for ext in accepted_types):
            return {'valid': False, 'error': f'File type not supported. Accepted: {", ".join(accepted_types)}'}
        
        max_size = self.get_setting('max_file_size', 10 * 1024 * 1024)
        estimated_size = len(contents) * 3 // 4
        if estimated_size > max_size:
            return {'valid': False, 'error': f'File too large. Max size: {max_size // (1024*1024)}MB'}
        
        return {'valid': True}
    
    def _process_file(self, contents: str, filename: str) -> Dict[str, Any]:
        """Process uploaded file with comprehensive error handling and validation"""
        try:
            # Validate input
            if ',' not in contents:
                raise ValueError("Invalid file format: missing data separator")

            # Decode base64 content
            content_type, content_string = contents.split(',', 1)
            try:
                decoded = base64.b64decode(content_string)
            except Exception as e:
                raise ValueError("File encoding error: unable to decode file data") from e

            # Determine file extension
            file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
            allowed_extensions = ['csv', 'txt', 'json']

            if file_extension not in allowed_extensions:
                raise ValueError(f"Unsupported file type: '.{file_extension}'. Please upload a CSV or JSON file.")

            # Try different encodings for decoding
            encoding_fallbacks = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            decoded_string = None
            used_encoding = None

            for encoding in encoding_fallbacks:
                try:
                    decoded_string = decoded.decode(encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if decoded_string is None:
                raise ValueError("Unable to decode file. Please save as UTF-8 encoding.")

            # Parse file based on extension
            try:
                if file_extension == 'json':
                    # Handle JSON files
                    data = json.loads(decoded_string)

                    # Convert to DataFrame if it's a list of objects
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                        df = pd.DataFrame(data)
                    else:
                        # For other JSON structures, create a simple DataFrame
                        df = pd.DataFrame([data] if not isinstance(data, list) else data)

                else:  # CSV or TXT
                    df = pd.read_csv(io.StringIO(decoded_string))

            except pd.errors.EmptyDataError:
                raise ValueError(f"{file_extension.upper()} file is empty or contains no data")
            except pd.errors.ParserError as e:
                if file_extension == 'json':
                    raise ValueError(f"JSON format error: {str(e)}")
                else:
                    raise ValueError(f"CSV format error: {str(e)}")
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON format error: {str(e)}")
            except Exception as e:
                raise ValueError(f"Unable to read {file_extension.upper()} data: {str(e)}")

            # Validate parsed data
            if df.empty:
                raise ValueError("File contains no data rows")

            if len(df.columns) == 0:
                raise ValueError("File contains no columns")

            if len(df.columns) > 1000:
                raise ValueError("File has too many columns (>1000). Please check file format.")

            # Log success
            print(f"Successfully processed {filename}: {len(df)} rows, {len(df.columns)} columns")

            # Return processed data in consistent format
            return {
                'filename': filename,
                'dataframe': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'column_count': len(df.columns),
                'upload_timestamp': pd.Timestamp.now().isoformat(),
                'encoding_used': used_encoding,
                'file_type': file_extension,
                'success': True
            }

        except Exception as e:
            raise ValueError(f"Processing failed: {str(e)}")
    
    def _create_success_status(self, filename: str, row_count: int):
        """Create success status message"""
        return dbc.Alert([
            html.Span(self.get_icon('success'), style={'marginRight': '8px'}),
            f"Successfully uploaded {filename} ({row_count} rows)"
        ], color="success", dismissable=True)
    
    def _create_error_status(self, error_message: str):
        """Create error status message"""
        return dbc.Alert([
            html.Span(self.get_icon('error'), style={'marginRight': '8px'}),
            f"Error: {error_message}"
        ], color="danger", dismissable=True)
    
    def _create_data_preview(self, data: Dict[str, Any]) -> html.Div:
        """Create data preview"""
        return html.Div([
            html.H5("Data Preview"),
            html.P(f"Type: {data['type'].upper()}"),
            html.P(f"Rows: {data['row_count']}"),
            html.P(f"Columns: {', '.join(data.get('columns', []))}" if data.get('columns') else "")
        ], style={'margin': '16px 0'})

def create_modular_upload_component(component_id: Optional[str] = None, **props) -> ModularUploadComponent:
    """Factory function to create modular upload component"""
    config = get_component_config('upload')
    return ModularUploadComponent(config, component_id)

def register_modular_upload_component():
    """Register modular upload component with global registry"""
    from ui.core.component_registry import register_component
    
    register_component('upload_modular', ModularUploadComponent)

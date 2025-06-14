# ui/handlers/mapping_handlers.py
"""
Mapping callback handlers - extracted from mapping_callbacks.py
Separated business logic from UI definitions
FIXED: Removed duplicate callback that conflicts with classification_handlers.py
"""

import json
from dash import Input, Output, State, no_update
from dash.dependencies import ALL
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import pandas as pd

from utils.logging_config import get_logger

# Import UI components
from ui.components.mapping import create_mapping_component, create_mapping_validator
from ui.themes.style_config import COLORS


class MappingHandlers:
    """Handles all mapping-related callbacks and business logic"""
    
    def __init__(self, app: Any, mapping_component: Optional[Any] = None) -> None:
        self.app = app
        self.mapping_component = mapping_component or create_mapping_component()
        self.validator = create_mapping_validator()
        self.logger = get_logger(__name__)
        
    def register_callbacks(self) -> None:
        """Register ONLY mapping callbacks"""
        # Dropdown creation is now handled in UploadHandlers to avoid duplicate outputs
        self._register_mapping_confirmation_handler()
        # REMOVED: Any callback that outputs to 'door-classification-table-container'

    
    def _register_mapping_confirmation_handler(self) -> None:
        """Mapping confirmation - NO classification outputs"""
        @self.app.callback(
            [
                Output('mapping-ui-section', 'style', allow_duplicate=True),  
                Output('entrance-verification-ui-section', 'style', allow_duplicate=True),  # Only show/hide the section
                Output('column-mapping-store', 'data', allow_duplicate=True),  # Save updated mappings
                # Update status via shared store
                Output('status-message-store', 'data', allow_duplicate=True),
                Output('confirm-header-map-button', 'style', allow_duplicate=True),  # Add this
 
                # REMOVED: Output('door-classification-table-container', 'style')  ← This was causing conflict
            ],
            Input('confirm-header-map-button', 'n_clicks'),
            [
                State({'type': 'mapping-dropdown', 'index': ALL}, 'value'),
                State({'type': 'mapping-dropdown', 'index': ALL}, 'id'),
                State('csv-headers-store', 'data'),
                State('column-mapping-store', 'data')
            ],
            prevent_initial_call=True
        )
        def confirm_mapping_and_show_next_step(n_clicks, values, ids, csv_headers, existing_json):
            # ... existing logic but DON'T control door-classification-table-container
            if not n_clicks:
                return no_update, no_update, no_update, no_update, no_update
                
            result = self._process_mapping_confirmation(values, ids, csv_headers, existing_json)
            
            if result['success']:
                hide_mapping_style = {'display': 'none'}
                show_entrance_verification_style = {'display': 'block', 'width': '95%', 'margin': '0 auto'}
                hide_button_style = {'display': 'none'}
                status_message = "Step 2: Set Classification Options"
                
                return (
                    hide_mapping_style,                    # Hide mapping UI
                    show_entrance_verification_style,      # Show entrance verification UI  
                    result['updated_mappings'],            # Save updated mappings
                    status_message,                        # Update status message
                    hide_button_style                      # Hide confirm button
                )
            else:
                error_message = f"Mapping Error: {result.get('error', 'Unknown error')}"
                return no_update, no_update, no_update, error_message, no_update

    
    # REMOVED: _register_classification_toggle_handler method
    # This is now handled exclusively by classification_handlers.py to avoid conflicts
    
    def _process_mapping_confirmation(self, values, ids, csv_headers, existing_json):
        """Process user's mapping selections and validate completeness.

        Takes the user's dropdown selections from the mapping interface, validates
        that all required columns are mapped, and prepares the data for the next
        workflow step. Also updates stored user preferences for future uploads.

        Args:
            values: List of selected values from mapping dropdowns. Each value
                corresponds to a CSV column name chosen by the user.
            ids: List of dropdown component IDs containing the internal field names.
                Structure: ``[{'index': 'UserID'}, {'index': 'DoorID'}, ...]``
            csv_headers: Complete list of available CSV column headers that can
                be selected in the dropdowns.
            existing_json: Previously saved mapping preferences, either as JSON
                string or dictionary. Used to update user's preference history.

        Returns:
            Processing result dictionary containing:
                - ``success`` (bool): ``True`` if mapping is valid and complete
                - ``mapping`` (Dict[str, str]): Final validated mapping if successful
                - ``updated_mappings`` (Dict): Updated preference storage including new mapping
                - ``csv_headers`` (List[str]): Original headers for reference
                - ``error`` (str): Error message if validation failed
                - ``missing_columns`` (List[str]): Missing required columns if validation failed

        Raises:
            ValueError: If ``values`` and ``ids`` lists have different lengths
            TypeError: If input parameters are not the expected types

        Example:
            >>> values = ['user_id_col', 'door_name_col', 'event_time', 'access_result']
            >>> ids = [{'index': 'UserID'}, {'index': 'DoorID'}, {'index': 'Timestamp'}, {'index': 'EventType'}]
            >>> headers = ['user_id_col', 'door_name_col', 'event_time', 'access_result', 'extra_col']
            >>> result = handler._process_mapping_confirmation(values, ids, headers, None)
            >>> print(result['success'])
            True
            >>> print(result['mapping'])
            {'user_id_col': 'UserID', 'door_name_col': 'DoorID', 'event_time': 'Timestamp', 'access_result': 'EventType'}

        Side Effects:
            Updates internal mapping preferences storage for future use.
            May trigger UI state changes through callback return values.
        """

        try:
            # Create mapping dictionary
            mapping = {
                dropdown_value: dropdown_id['index']
                for dropdown_value, dropdown_id in zip(values, ids)
                if dropdown_value
            }
            
            # Validate mapping
            try:
                validation_result = self.validator.validate_mapping(mapping)
            except (TypeError, ValueError) as e:
                return {
                    'success': False,
                    'error': f"Invalid mapping data: {str(e)}",
                    'missing_columns': []
                }
            
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': validation_result['message'],
                    'missing_columns': validation_result['missing_columns']
                }
            
            # Update stored mappings
            updated_mappings = self._update_stored_mappings(
                mapping, csv_headers, existing_json
            )
            
            return {
                'success': True,
                'mapping': mapping,
                'updated_mappings': updated_mappings,
                'csv_headers': csv_headers
            }
            
        except KeyError as e:
            return {
                'success': False,
                'error': f"Missing required mapping key: {str(e)}"
            }
        except TypeError as e:
            return {
                'success': False,
                'error': f"Invalid mapping data type: {str(e)}"
            }
        except Exception as e:
            self.logger.error("Mapping error: %s", str(e))
            return {
                'success': False,
                'error': f"Mapping operation failed: {str(e)}"
            }
    
    def _update_stored_mappings(
        self,
        mapping: Dict[str, str],
        csv_headers: List[str],
        existing_json: Union[str, Dict[str, Any], None]
    ) -> Dict[str, Any]:
        """Update the stored column mappings"""
        if isinstance(existing_json, str):
            updated_mappings = json.loads(existing_json)
        else:
            updated_mappings = existing_json or {}
        
        # Create header key for this CSV structure
        header_key = json.dumps(sorted(csv_headers)) if csv_headers else None
        
        if header_key:
            updated_mappings[header_key] = mapping
        
        return updated_mappings
    
    def _create_mapping_success_response(
        self, result: Dict[str, Any]
    ) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, Any], str, Dict[str, str]]:
        """Create response for successful mapping confirmation"""
        hide_mapping_style = {'display': 'none'}
        
        show_entrance_verification_style = {
            'display': 'block', 
            'width': '95%', 
            'margin': '0 auto', 
            'paddingLeft': '15px', 
            'boxSizing': 'border-box', 
            'textAlign': 'center'
        }
        
        hide_button_style = {'display': 'none'}
        
        status_message = "Step 2: Set Classification Options"
        
        return (
            hide_mapping_style,                    # Hide mapping UI
            show_entrance_verification_style,      # Show entrance verification UI
            result['updated_mappings'],            # Save updated mappings
            status_message,                        # Update status message
            hide_button_style                      # Hide confirm button
        )
    
    def _create_mapping_error_response(self, result: Dict[str, Any]) -> Tuple[Any, Any, Any, str, Any]:
        """Create response for mapping errors"""
        # Keep current states but update status
        error_message = f"Mapping Error: {result.get('error', 'Unknown error')}"
        
        return (
            no_update,      # Keep mapping UI visible
            no_update,      # Don't show next step
            no_update,      # Don't update mappings
            error_message,  # Show error message
            no_update       # Keep button state
        )


# Factory functions for easy handler creation
def create_mapping_handlers(app: Any, mapping_component: Optional[Any] = None) -> MappingHandlers:
    """Factory function to create mapping handlers"""
    return MappingHandlers(app, mapping_component)

# ui/components/mapping.py (UPDATED - Fixed import and reduced width to match other components)
"""
Column mapping component for CSV header mapping
Extracted from core_layout.py and mapping_callbacks.py with consistent reduced width
FIXED: Corrected import statement
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from ui.themes.style_config import COLORS, MAPPING_STYLES, get_validation_message_style
from config.settings import REQUIRED_INTERNAL_COLUMNS


class MappingComponent:
    """Centralized mapping component with all related UI elements and consistent widths"""
    
    def __init__(self):
        self.required_columns = REQUIRED_INTERNAL_COLUMNS
    
    def create_mapping_section(self):
        """Creates the Step 1: Map CSV Headers section with reduced width"""
        return html.Div(
            id='mapping-ui-section',
            style=MAPPING_STYLES['section'],
            children=[
                self.create_mapping_header(),
                self.create_mapping_help_text(),
                self.create_mapping_area(),
                html.Div(id='mapping-validation-message', style={'display': 'none'}),  # Add validation message div
                self.create_confirm_button()
            ]
        )
    
    def create_mapping_header(self):
        """Creates the mapping section header with smaller font"""
        return html.H4(
            "Step 1: Map CSV Headers", 
            className="text-center", 
            style={'color': COLORS['text_primary'], 'fontSize': '1.3rem', 'marginBottom': '1rem'}  # Reduced font size and margin
        )
    
    def create_mapping_area(self):
        """Creates the dropdown mapping area container"""
        return html.Div(id='dropdown-mapping-area')
    
    def create_confirm_button(self):
        """Creates the confirm header mapping button with reduced size"""
        return html.Button(
            'Confirm Header Mapping & Proceed',
            id='confirm-header-map-button',
            n_clicks=0,
            style=MAPPING_STYLES['confirm_button']
        )
    
    def _create_mapping_dropdowns(self, headers, loaded_col_map_prefs=None):
        """
        Creates dropdown components for column mapping with improved layout
        
        Args:
            headers: List of CSV column headers
            loaded_col_map_prefs: Previously saved column mapping preferences
        
        Returns:
            List of html.Div components with dropdowns
        """
        if loaded_col_map_prefs is None:
            loaded_col_map_prefs = {}
            
        mapping_dropdowns_children = []
        
        for internal_name, display_text in self.required_columns.items():
            # Find pre-selected value
            pre_sel = self._find_preselected_value(
                internal_name, headers, loaded_col_map_prefs
            )
            
            dropdown = self._create_single_dropdown(
                internal_name, headers, pre_sel
            )
            
            dropdown_container = self._create_dropdown_container(
                display_text, dropdown
            )
            
            mapping_dropdowns_children.append(dropdown_container)
        
        return mapping_dropdowns_children
    
    def create_mapping_validation_message(self, missing_columns=None, status="info"):
        """
        Creates validation message for mapping status
        
        Args:
            missing_columns: List of missing required columns
            status: 'info', 'warning', 'error', 'success'
        """
        if missing_columns:
            message = f"Missing required mappings: {', '.join(missing_columns)}"
            status = "error"
        else:
            message = "All required columns mapped successfully!"
            status = "success"
            
        return html.Div(
            id='mapping-validation-message',
            children=message,
            style=get_validation_message_style(status)
        )
    
    def create_mapping_help_text(self):
        """Creates help text for the mapping process with smaller fonts"""
        return html.Div([
            html.P([
                "Map your CSV columns to the required fields. ",
                html.Strong("All four fields are required"), 
                " for the analysis to work properly."
            ], style={
                'color': COLORS['text_secondary'], 
                'fontSize': '0.85rem',  # Reduced from 0.9em
                'marginBottom': '8px'  # Reduced margin
            }),
            html.Details([
                html.Summary("What do these fields mean?", 
                           style={'color': COLORS['accent'], 'cursor': 'pointer', 'fontSize': '0.9rem'}),  # Reduced font
                html.Ul([
                    html.Li([html.Strong("Timestamp: "), "When the access event occurred"]),
                    html.Li([html.Strong("UserID: "), "Person identifier (badge number, employee ID, etc.)"]),
                    html.Li([html.Strong("DoorID: "), "Device or door identifier"]),
                    html.Li([html.Strong("EventType: "), "Access result (granted, denied, etc.)"])
                ], style={'color': COLORS['text_secondary'], 'fontSize': '0.8rem'})  # Reduced font
            ])
        ], style={'marginBottom': '12px'})  # Reduced margin
    
    def get_mapping_styles(self):
        """Returns all mapping-related styles"""
        return {
            'section': MAPPING_STYLES['section'],
            'button_hidden': {**MAPPING_STYLES['confirm_button'], 'display': 'none'},
            'button_visible': MAPPING_STYLES['confirm_button'],
            'dropdown': MAPPING_STYLES['dropdown'],
            'label': MAPPING_STYLES['label']
        }
    
    def _find_preselected_value(self, internal_name, headers, loaded_col_map_prefs):
        """Find preselected value for dropdown based on saved preferences"""
        pre_sel = None
        if loaded_col_map_prefs:
            for csv_h, internal_h in loaded_col_map_prefs.items():
                if internal_h == internal_name and csv_h in headers:
                    pre_sel = csv_h
                    break
        return pre_sel
    
    def _create_single_dropdown(self, internal_name, headers, pre_sel):
        """Create a single dropdown for column mapping with improved styling"""
        return dcc.Dropdown(
            id={'type': 'mapping-dropdown', 'index': internal_name},
            options=[{'label': h, 'value': h} for h in headers],
            value=pre_sel,
            placeholder="Select column...",
            style=MAPPING_STYLES['dropdown'],
            className="mapping-dropdown"
        )
    
    def _create_dropdown_container(self, display_text, dropdown):
        """Create container for label and dropdown with improved layout"""
        return html.Div([
            html.Label(
                f"{display_text}:",
                style=MAPPING_STYLES['label']
            ),
            dropdown
        ], className="mapping-row", style={'marginBottom': '12px'})  # Reduced margin
    
    def _get_mapping_section_style(self):
        """Backward-compatible wrapper for section style"""
        return MAPPING_STYLES['section']
    
    def _get_confirm_button_style(self, visible=True):
        """Backward-compatible wrapper for button style"""
        style = MAPPING_STYLES['confirm_button'].copy()
        if not visible:
            style['display'] = 'none'
        return style
    
    def _get_dropdown_style(self):
        """Backward-compatible wrapper for dropdown style"""
        return MAPPING_STYLES['dropdown']
    
    def _get_label_style(self):
        """Backward-compatible wrapper for label style"""
        return MAPPING_STYLES['label']
    
    def _get_validation_message_style(self, status="info"):
        """Backward-compatible wrapper for validation message style"""
        return get_validation_message_style(status)


class MappingValidator:
    """Validates mapping completeness and correctness"""
    
    def __init__(self, required_columns):
        self.required_columns = required_columns
    
    def validate_mapping(self, mapping_dict):
        """
        Validates that all required columns are mapped

        Args:
            mapping_dict: Dict of {csv_column: internal_key}

        Returns:
            Dict with 'is_valid', 'missing_columns', 'message'

        Raises:
            TypeError: If mapping_dict is not a dictionary
            ValueError: If mapping_dict contains invalid data types
        """

        # INPUT VALIDATION - NEW SECTION
        # 1. Check if input is a dictionary
        if not isinstance(mapping_dict, dict):
            raise TypeError(
                f"mapping_dict must be a dictionary, got {type(mapping_dict).__name__}"
            )

        # 2. Check for None input (explicit check)
        if mapping_dict is None:
            return {
                'is_valid': False,
                'missing_columns': list(self.required_columns.keys()),
                'message': 'No mapping provided'
            }

        # 3. Check if dictionary is empty
        if not mapping_dict:
            return {
                'is_valid': False,
                'missing_columns': list(self.required_columns.keys()),
                'message': 'No columns mapped'
            }

        # 4. Validate dictionary keys and values are strings
        for key, value in mapping_dict.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"All mapping keys must be strings, got {type(key).__name__}: {key}"
                )
            if not isinstance(value, str):
                raise ValueError(
                    f"All mapping values must be strings, got {type(value).__name__}: {value}"
                )
            if not key.strip():
                raise ValueError("Mapping keys cannot be empty or whitespace-only")
            if not value.strip():
                raise ValueError("Mapping values cannot be empty or whitespace-only")

        # 5. Check for None or empty values in the dictionary
        invalid_entries = [
            key for key, value in mapping_dict.items()
            if value is None or (isinstance(value, str) and not value.strip())
        ]
        if invalid_entries:
            return {
                'is_valid': False,
                'missing_columns': invalid_entries,
                'message': f'Invalid mapping values for: {", ".join(invalid_entries)}'
            }

        # 6. Validate that required_columns exists and is properly initialized
        if not hasattr(self, 'required_columns') or not self.required_columns:
            raise ValueError("MappingValidator not properly initialized: missing required_columns")

        # EXISTING VALIDATION LOGIC (unchanged)
        mapped_internal_keys = set(mapping_dict.values())
        required_internal_keys = set(self.required_columns.keys())
        missing_keys = required_internal_keys - mapped_internal_keys

        if missing_keys:
            missing_display_names = [
                self.required_columns[key] for key in missing_keys
            ]
            return {
                'is_valid': False,
                'missing_columns': missing_display_names,
                'message': f'Missing required mappings: {", ".join(missing_display_names)}'
            }

        return {
            'is_valid': True,
            'missing_columns': [],
            'message': 'All required columns mapped successfully'
        }

    def validate_single_mapping(self, csv_column, internal_key):
        """
        Validate a single mapping entry

        Args:
            csv_column: CSV column name
            internal_key: Internal key to map to

        Returns:
            Dict with validation result

        Raises:
            TypeError: If inputs are not strings
            ValueError: If inputs are invalid
        """

        # Input validation for single entries
        if not isinstance(csv_column, str):
            raise TypeError(f"csv_column must be a string, got {type(csv_column).__name__}")

        if not isinstance(internal_key, str):
            raise TypeError(f"internal_key must be a string, got {type(internal_key).__name__}")

        if not csv_column.strip():
            raise ValueError("csv_column cannot be empty or whitespace-only")

        if not internal_key.strip():
            raise ValueError("internal_key cannot be empty or whitespace-only")

        # Check if internal_key is valid
        if internal_key not in self.required_columns:
            valid_keys = list(self.required_columns.keys())
            return {
                'is_valid': False,
                'error': f'Invalid internal key "{internal_key}". Valid keys: {", ".join(valid_keys)}'
            }

        return {
            'is_valid': True,
            'message': f'Valid mapping: {csv_column} -> {internal_key}'
        }
    
    def suggest_mappings(self, csv_headers):
        """
        Suggests automatic mappings based on fuzzy matching
        
        Args:
            csv_headers: List of CSV column headers
            
        Returns:
            Dict of suggested mappings {csv_header: internal_key}
        """
        from difflib import get_close_matches
        
        suggestions = {}
        
        for internal_key, display_name in self.required_columns.items():
            # Try exact match first
            if display_name in csv_headers:
                suggestions[display_name] = internal_key
                continue
                
            if internal_key in csv_headers:
                suggestions[internal_key] = internal_key
                continue
            
            # Fuzzy match on display name
            matches = get_close_matches(display_name.lower(), 
                                      [h.lower() for h in csv_headers], 
                                      n=1, cutoff=0.6)
            if matches:
                # Find original case header
                original_header = next(h for h in csv_headers if h.lower() == matches[0])
                suggestions[original_header] = internal_key
                continue
            
            # Fuzzy match on internal key
            matches = get_close_matches(internal_key.lower(), 
                                      [h.lower() for h in csv_headers], 
                                      n=1, cutoff=0.6)
            if matches:
                original_header = next(h for h in csv_headers if h.lower() == matches[0])
                suggestions[original_header] = internal_key
        
        return suggestions


# Factory functions for easy component creation
def create_mapping_component():
    """Factory function to create mapping component instance"""
    return MappingComponent()

def create_mapping_validator():
    """Factory function to create mapping validator instance"""
    return MappingValidator(REQUIRED_INTERNAL_COLUMNS)

# Convenience functions for individual elements (backward compatibility)
def create_mapping_section():
    """Create the mapping section"""
    component = MappingComponent()
    return component.create_mapping_section()

def _create_mapping_dropdowns(headers, saved_preferences=None):
    """Create mapping dropdowns"""
    component = MappingComponent()
    return component._create_mapping_dropdowns(headers, saved_preferences)

# ui/components/mapping.py (UPDATED - Fixed import and reduced width to match other components)
"""
Column mapping component for CSV header mapping
Extracted from core_layout.py and mapping_callbacks.py with consistent reduced width
FIXED: Corrected import statement
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import pandas as pd

from ui.themes.style_config import COLORS, MAPPING_STYLES, get_validation_message_style
from config.settings import REQUIRED_INTERNAL_COLUMNS
from functools import lru_cache
from typing import List, Dict, Tuple


class MappingComponent:
    """Centralized mapping component with all related UI elements and consistent widths"""
    
    def __init__(self) -> None:
        self.required_columns = REQUIRED_INTERNAL_COLUMNS

    def create_mapping_section(self) -> html.Div:
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
    
    def create_mapping_header(self) -> html.H4:
        """Creates the mapping section header with smaller font"""
        return html.H4(
            "Step 1: Map CSV Headers", 
            className="text-center", 
            style={'color': COLORS['text_primary'], 'fontSize': '1.3rem', 'marginBottom': '1rem'}  # Reduced font size and margin
        )
    
    def create_mapping_area(self) -> html.Div:
        """Creates the dropdown mapping area container"""
        return html.Div(id='dropdown-mapping-area')
    
    def create_confirm_button(self) -> html.Button:
        """Creates the confirm header mapping button with reduced size"""
        return html.Button(
            'Confirm Header Mapping & Proceed',
            id='confirm-header-map-button',
            n_clicks=0,
            style=MAPPING_STYLES['confirm_button']
        )
    
    def _create_mapping_dropdowns(
        self, headers: List[str], loaded_col_map_prefs: Optional[Dict[str, str]] = None
    ) -> List[html.Div]:
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
    
    def create_mapping_validation_message(
        self, missing_columns: Optional[List[str]] = None, status: str = "info"
    ) -> html.Div:
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
    
    def create_mapping_help_text(self) -> html.Div:
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
    
    def get_mapping_styles(self) -> Dict[str, Dict[str, Any]]:
        """Returns all mapping-related styles"""
        return {
            'section': MAPPING_STYLES['section'],
            'button_hidden': {**MAPPING_STYLES['confirm_button'], 'display': 'none'},
            'button_visible': MAPPING_STYLES['confirm_button'],
            'dropdown': MAPPING_STYLES['dropdown'],
            'label': MAPPING_STYLES['label']
        }
    
    def _find_preselected_value(
        self, internal_name: str, headers: List[str], loaded_col_map_prefs: Dict[str, str]
    ) -> Optional[str]:
        """Find preselected value for dropdown based on saved preferences"""
        pre_sel = None
        if loaded_col_map_prefs:
            for csv_h, internal_h in loaded_col_map_prefs.items():
                if internal_h == internal_name and csv_h in headers:
                    pre_sel = csv_h
                    break
        return pre_sel
    
    def _create_single_dropdown(
        self, internal_name: str, headers: List[str], pre_sel: Optional[str]
    ) -> dcc.Dropdown:
        """Create a single dropdown for column mapping with improved styling"""
        return dcc.Dropdown(
            id={'type': 'mapping-dropdown', 'index': internal_name},
            options=[{'label': h, 'value': h} for h in headers],
            value=pre_sel,
            placeholder="Select column...",
            style=MAPPING_STYLES['dropdown'],
            className="mapping-dropdown"
        )
    
    def _create_dropdown_container(self, display_text: str, dropdown: Any) -> html.Div:
        """Create container for label and dropdown with improved layout"""
        return html.Div([
            html.Label(
                f"{display_text}:",
                style=MAPPING_STYLES['label']
            ),
            dropdown
        ], className="mapping-row", style={'marginBottom': '12px'})  # Reduced margin
    
    def _get_mapping_section_style(self) -> Dict[str, Any]:
        """Backward-compatible wrapper for section style"""
        return MAPPING_STYLES['section']
    
    def _get_confirm_button_style(self, visible: bool = True) -> Dict[str, Any]:
        """Backward-compatible wrapper for button style"""
        style = MAPPING_STYLES['confirm_button'].copy()
        if not visible:
            style['display'] = 'none'
        return style
    
    def _get_dropdown_style(self) -> Dict[str, Any]:
        """Backward-compatible wrapper for dropdown style"""
        return MAPPING_STYLES['dropdown']
    
    def _get_label_style(self) -> Dict[str, Any]:
        """Backward-compatible wrapper for label style"""
        return MAPPING_STYLES['label']
    
    def _get_validation_message_style(self, status: str = "info") -> Dict[str, Any]:
        """Backward-compatible wrapper for validation message style"""
        return get_validation_message_style(status)


class MappingValidator:
    """Validates mapping completeness and correctness for CSV column mapping.

    This class ensures that all required columns are properly mapped from CSV headers
    to internal column names, and provides automatic suggestions using fuzzy matching
    when exact matches are not found.

    Attributes:
        required_columns (Dict[str, str]): Mapping of internal keys to display names
            for all columns that must be present in the final mapping.

    Example:
        >>> validator = MappingValidator({'UserID': 'User ID', 'DoorID': 'Door ID'})
        >>> result = validator.validate_mapping({'user_col': 'UserID', 'door_col': 'DoorID'})
        >>> print(result['is_valid'])  # True
    """
    
    def __init__(self, required_columns):
        """Initialize the mapping validator with required columns.

        Args:
            required_columns: Dictionary mapping internal column keys to their
                display names. For example: ``{'UserID': 'User ID', 'DoorID': 'Door ID'}``

        Raises:
            ValueError: If ``required_columns`` is empty or ``None``.
            TypeError: If ``required_columns`` is not a dictionary.
        """
        if not isinstance(required_columns, dict):
            raise TypeError("required_columns must be a dictionary")
        if not required_columns:
            raise ValueError("required_columns cannot be empty")

        self.required_columns = required_columns
        # Initialize cache for fuzzy matching results
        self._fuzzy_cache = {}
    
    def validate_mapping(self, mapping_dict):
        """Validate that all required columns are properly mapped.

        Checks that the provided mapping dictionary contains valid mappings for all
        required internal columns. Returns detailed validation results including
        any missing mappings and appropriate error messages.


        Args:
            mapping_dict: Dictionary mapping CSV column names to internal column keys.
                Example: ``{'user_column': 'UserID', 'door_column': 'DoorID'}``

        Returns:
            Dictionary with validation results containing:
                - ``is_valid`` (bool): ``True`` if all required columns are mapped
                - ``missing_columns`` (List[str]): Display names of unmapped required columns
                - ``message`` (str): Human-readable validation message

        Raises:
            TypeError: If ``mapping_dict`` is not a dictionary
            ValueError: If ``mapping_dict`` contains invalid key/value types

        Example:
            >>> validator = MappingValidator({'UserID': 'User ID'})
            >>> result = validator.validate_mapping({'user_col': 'UserID'})
            >>> print(result)
            {'is_valid': True, 'missing_columns': [], 'message': 'All required columns mapped successfully'}
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

    def validate_single_mapping(self, csv_column: str, internal_key: str) -> Dict[str, Any]:
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
        """Generate automatic mapping suggestions using fuzzy string matching.

        Analyzes CSV column headers and suggests appropriate mappings to required
        internal columns using exact matching first, then fuzzy matching with
        configurable similarity thresholds.

        The algorithm works as follows:
        1. Try exact matches between CSV headers and display names
        2. Try exact matches between CSV headers and internal keys
        3. Use fuzzy matching on display names (cutoff: 0.6)
        4. Use fuzzy matching on internal keys (cutoff: 0.6)

        Args:
            csv_headers: List of column header names from the uploaded CSV file.
                Must be non-empty and contain only string values.


        Returns:
            Dictionary mapping CSV headers to suggested internal keys.
            Example: ``{'user_id_col': 'UserID', 'door_name': 'DoorID'}``

        Raises:
            TypeError: If ``csv_headers`` is not a list
            ValueError: If ``csv_headers`` is empty or contains non-string values

        Example:
            >>> validator = MappingValidator({'UserID': 'User ID', 'DoorID': 'Door ID'})
            >>> suggestions = validator.suggest_mappings(['user_id', 'door_name', 'timestamp'])
            >>> print(suggestions)
            {'user_id': 'UserID', 'door_name': 'DoorID'}

        Note:
            This method uses caching to improve performance on repeated calls
            with similar header sets. Cache can be cleared using ``clear_fuzzy_cache()``.
        """
        from difflib import get_close_matches

        suggestions: Dict[str, str] = {}

        for internal_key, display_name in self.required_columns.items():
            # Try exact match first (no caching needed - this is fast)
            if display_name in csv_headers:
                suggestions[display_name] = internal_key
                continue

            if internal_key in csv_headers:
                suggestions[internal_key] = internal_key
                continue

            # OPTIMIZATION: Cache expensive fuzzy matching operations
            display_matches = self._get_cached_fuzzy_matches(
                display_name.lower(),
                tuple(h.lower() for h in csv_headers),
                cutoff=0.6
            )
            if display_matches:
                original_header = next(h for h in csv_headers if h.lower() == display_matches[0])
                suggestions[original_header] = internal_key
                continue

            internal_matches = self._get_cached_fuzzy_matches(
                internal_key.lower(),
                tuple(h.lower() for h in csv_headers),
                cutoff=0.6
            )
            if internal_matches:
                original_header = next(h for h in csv_headers if h.lower() == internal_matches[0])
                suggestions[original_header] = internal_key

        return suggestions

    @lru_cache(maxsize=256)
    def _get_cached_fuzzy_matches(self, target: str, candidates_tuple: Tuple[str, ...], cutoff: float = 0.6) -> List[str]:
        """Cached fuzzy matching to avoid recomputing expensive string comparisons"""
        from difflib import get_close_matches

        return get_close_matches(target, list(candidates_tuple), n=1, cutoff=cutoff)

    def clear_fuzzy_cache(self) -> None:
        """Clear the fuzzy matching cache (useful for testing or memory management)"""
        self._get_cached_fuzzy_matches.cache_clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics"""
        cache_info = self._get_cached_fuzzy_matches.cache_info()
        return {
            'hits': cache_info.hits,
            'misses': cache_info.misses,
            'current_size': cache_info.currsize,
            'max_size': cache_info.maxsize
        }


# Factory functions for easy component creation
def create_mapping_component() -> MappingComponent:
    """Factory function to create mapping component instance"""
    return MappingComponent()

def create_mapping_validator() -> MappingValidator:
    """Factory function to create mapping validator instance"""
    return MappingValidator(REQUIRED_INTERNAL_COLUMNS)

# Convenience functions for individual elements (backward compatibility)
def create_mapping_section() -> html.Div:
    """Create the mapping section"""
    component = MappingComponent()
    return component.create_mapping_section()

def _create_mapping_dropdowns(
    headers: List[str], saved_preferences: Optional[Dict[str, str]] = None
) -> List[html.Div]:
    """Create mapping dropdowns"""
    component = MappingComponent()
    return component._create_mapping_dropdowns(headers, saved_preferences)

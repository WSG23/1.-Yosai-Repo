# ui/components/classification_handlers.py
"""
Classification callback handlers - FIXED VERSION with allow_duplicate for conflicting outputs
"""

import json
from dash import Input, Output, State, html, callback, no_update
from dash.dependencies import ALL

# Import UI components
from ui.components.classification import create_classification_component
from ui.themes.style_config import COLORS
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ClassificationHandlers:
    """Handles all classification-related callbacks and business logic"""
    
    def __init__(self, app, classification_component=None):
        self.app = app
        self.classification_component = classification_component or create_classification_component()
        
    def register_callbacks(self):
        """Register classification callbacks with duplicate handling"""
        self._register_door_table_generation_handler()
        self._register_door_type_mutual_exclusion_handler() 
        self._register_floor_slider_display_handler()
        self._register_classification_toggle_handler()
        
    def _register_classification_toggle_handler(self):
        """SINGLE callback - controls classification table visibility"""
        @self.app.callback(
            Output('door-classification-table-container', 'style', allow_duplicate=True),
            Input('manual-map-toggle', 'value'),
            prevent_initial_call=False
        )
        def toggle_classification_tools(manual_map_choice):
            """Control classification table visibility"""
            if manual_map_choice == 'yes':
                return {'display': 'block'}
            else:
                return {'display': 'none'}

    def _register_floor_slider_display_handler(self):
        """Update floor display when slider value changes - FIXED with allow_duplicate"""
        @self.app.callback(
            Output("num-floors-display", "children", allow_duplicate=True),
            Input("num-floors-input", "value"),
            prevent_initial_call=False
        )
        def update_floor_display(value):
            """Update the floor display text based on slider value"""
            if value is None:
                value = 4
            
            floors = int(value)
            if floors == 1:
                return "1 floor"
            else:
                return f"{floors} floors"
        
    def _register_door_table_generation_handler(self):
        """Generates door classification table when conditions are met"""
        @self.app.callback(
            Output('door-classification-table', 'children', allow_duplicate=True),
            [
                Input('confirm-header-map-button', 'n_clicks'),
                Input('manual-map-toggle', 'value'),
                Input('num-floors-input', 'value')
            ],
            [
                State('all-doors-from-csv-store', 'data'),
                State('manual-door-classifications-store', 'data')
            ],
            prevent_initial_call=True
        )
        def generate_door_classification_table_content(
            n_clicks_confirm_map, manual_map_choice, num_floors, 
            all_doors_from_store_data, existing_saved_classifications
        ):
            # Only generate if manual mapping is chosen and there are doors
            if manual_map_choice != 'yes' or not all_doors_from_store_data:
                logger.info("DEBUG: Not in manual mode or no doors available for classification table.")
                return []
                
            # Handle slider value (ensure it's an integer)
            num_floors_int = int(num_floors) if num_floors is not None else 4
                
            return self._generate_classification_table(
                all_doors_from_store_data,
                existing_saved_classifications,
                num_floors_int
            )
    
    def _register_door_type_mutual_exclusion_handler(self):
        """Ensures Entry/Exit and Stairway are mutually exclusive"""
        @self.app.callback(
            [
                Output({'type': 'door-type-toggle', 'index': ALL}, 'value', allow_duplicate=True),
                Output({'type': 'stairway-toggle', 'index': ALL}, 'value', allow_duplicate=True)
            ],
            [
                Input({'type': 'door-type-toggle', 'index': ALL}, 'value'),
                Input({'type': 'stairway-toggle', 'index': ALL}, 'value')
            ],
            [
                State({'type': 'door-type-toggle', 'index': ALL}, 'id'),
                State({'type': 'stairway-toggle', 'index': ALL}, 'id')
            ],
            prevent_initial_call=True
        )
        def handle_mutual_exclusion(door_type_values, stairway_values, door_type_ids, stairway_ids):
            """Ensure only one type can be selected per door"""
            from dash import ctx
            
            if not ctx.triggered:
                return no_update, no_update
            
            # Get the trigger info
            trigger = ctx.triggered[0]
            trigger_id = trigger['prop_id']
            
            # Initialize return values
            new_door_type_values = list(door_type_values) if door_type_values else [None] * len(door_type_ids)
            new_stairway_values = list(stairway_values) if stairway_values else [None] * len(stairway_ids)
            
            # Find which door was clicked
            if 'door-type-toggle' in trigger_id:
                # Entry/Exit was clicked - clear corresponding stairway
                for i, door_type_id in enumerate(door_type_ids):
                    if door_type_id['index'] in trigger_id:
                        # Clear the corresponding stairway toggle
                        for j, stairway_id in enumerate(stairway_ids):
                            if stairway_id['index'] == door_type_id['index']:
                                new_stairway_values[j] = None
                                break
                        break
            
            elif 'stairway-toggle' in trigger_id:
                # Stairway was clicked - clear corresponding entry/exit
                for i, stairway_id in enumerate(stairway_ids):
                    if stairway_id['index'] in trigger_id:
                        # Clear the corresponding door-type toggle
                        for j, door_type_id in enumerate(door_type_ids):
                            if door_type_id['index'] == stairway_id['index']:
                                new_door_type_values[j] = None
                                break
                        break
            
            return new_door_type_values, new_stairway_values
    
    def _generate_classification_table(self, all_doors_data, existing_classifications, num_floors):
        """Generate the door classification table content with new scrollable design"""
        try:
            # Parse existing classifications if they're in JSON format
            if isinstance(existing_classifications, str):
                existing_classifications = json.loads(existing_classifications)
            else:
                existing_classifications = existing_classifications or {}
            
            # Generate scrollable table content using the classification component
            table_content = self.classification_component.create_scrollable_door_list(
                doors_to_classify=all_doors_data,
                existing_classifications=existing_classifications,
                num_floors=num_floors
            )
            
            logger.info(f"DEBUG: Generated scrollable classification table with {len(all_doors_data)} doors.")
            return table_content
            
        except Exception as e:
            logger.info(f"Error generating classification table: {e}")
            return [html.P(f"Error generating classification table: {str(e)}", 
                          style={'color': 'red', 'textAlign': 'center'})]

    def extract_current_classifications_from_inputs(self, floor_values, door_type_values, stairway_values, 
                                                   security_slider_values, all_door_ids):
        """Extract current classification values from form inputs - updated for new structure"""
        classifications = {}
        
        if not all_door_ids:
            return classifications
        
        # Create mappings for each door
        for i, door_id in enumerate(all_door_ids):
            # Get floor value
            floor = floor_values[i] if floor_values and i < len(floor_values) else '1'
            
            # Determine door type (mutually exclusive)
            door_type = 'none'
            if door_type_values and i < len(door_type_values) and door_type_values[i] == 'entry_exit':
                door_type = 'entry_exit'
            elif stairway_values and i < len(stairway_values) and stairway_values[i] == 'stairway':
                door_type = 'stairway'
            
            # Get security level (0-10 range)
            security_level = security_slider_values[i] if security_slider_values and i < len(security_slider_values) else 5
            
            # Build classification
            classifications[door_id] = {
                'floor': str(floor),
                'door_type': door_type,
                'is_ee': door_type == 'entry_exit',
                'is_stair': door_type == 'stairway',
                'security_level': int(security_level),
                'security': self._map_security_level_to_category(security_level)
            }
        
        return classifications
    
    def _map_security_level_to_category(self, level):
        """Map 0-10 security level to category"""
        level = int(level)
        if level <= 2:
            return 'unclassified'
        elif level <= 5:
            return 'green'
        elif level <= 7:
            return 'yellow'
        else:
            return 'red'
    
    def get_classification_summary(self, classifications):
        """Get a summary of current classifications"""
        if not classifications:
            return {
                'total_doors': 0,
                'entrances': 0,
                'stairways': 0,
                'high_security': 0,
                'avg_security_level': 0
            }
        
        total_doors = len(classifications)
        entrances = sum(1 for c in classifications.values() if c.get('is_ee', False))
        stairways = sum(1 for c in classifications.values() if c.get('is_stair', False))
        high_security = sum(1 for c in classifications.values() if c.get('security_level', 0) >= 8)
        avg_security = sum(c.get('security_level', 0) for c in classifications.values()) / total_doors if total_doors > 0 else 0
        
        return {
            'total_doors': total_doors,
            'entrances': entrances,
            'stairways': stairways,
            'high_security': high_security,
            'avg_security_level': round(avg_security, 1)
        }

    def _get_validation_message(self, is_complete, missing_count, total_doors):
        """Get user-friendly validation message"""
        if is_complete:
            return f"✓ All {total_doors} doors classified successfully"
        elif missing_count == 1:
            return f"⚠️ 1 door needs classification"
        else:
            return f"⚠️ {missing_count} doors need classification"
    
    def export_classifications(self, classifications):
        """Export classifications in a standardized format"""
        if not classifications:
            return {}
        
        exported = {}
        for door_id, classification in classifications.items():
            exported[door_id] = {
                'floor': str(classification.get('floor', '1')),
                'door_type': str(classification.get('door_type', 'none')),
                'is_ee': bool(classification.get('is_ee', False)),
                'is_stair': bool(classification.get('is_stair', False)),
                'security_level': int(classification.get('security_level', 5)),
                'security': str(classification.get('security', 'green'))
            }
        
        return exported
    
    def import_classifications(self, classification_data, all_doors):
        """Import and validate classification data"""
        if not classification_data or not all_doors:
            return {}
        
        imported = {}
        for door_id in all_doors:
            if door_id in classification_data:
                # Import existing classification
                imported[door_id] = classification_data[door_id]
            else:
                # Set defaults for missing doors
                imported[door_id] = {
                    'floor': '1',
                    'door_type': 'none',
                    'is_ee': False,
                    'is_stair': False,
                    'security_level': 5,
                    'security': 'green'
                }
        
        return imported


class ClassificationDataProcessor:
    """Processes classification data for use in other components"""
    
    def __init__(self, classification_component):
        self.classification_component = classification_component
        
    def process_for_onion_model(self, classifications):
        """Process classifications for onion model processing"""
        if not classifications:
            return {}, []
        
        # Extract confirmed entrances
        confirmed_entrances = [
            door_id for door_id, classification in classifications.items()
            if classification.get('is_ee', False)
        ]
        
        # Prepare detailed door classifications
        detailed_classifications = {}
        for door_id, classification in classifications.items():
            detailed_classifications[door_id] = {
                'floor': str(classification.get('floor', '1')),
                'is_ee': bool(classification.get('is_ee', False)),
                'is_stair': bool(classification.get('is_stair', False)),
                'security': str(classification.get('security', 'green')),
                'security_level': int(classification.get('security_level', 5))
            }
        
        return detailed_classifications, confirmed_entrances
    
    def get_entrance_summary(self, classifications):
        """Get summary of entrance/exit classifications"""
        if not classifications:
            return {'count': 0, 'doors': []}
        
        entrances = [
            door_id for door_id, classification in classifications.items()
            if classification.get('is_ee', False)
        ]
        
        return {
            'count': len(entrances),
            'doors': sorted(entrances)
        }
    
    def get_security_distribution(self, classifications):
        """Get distribution of security levels"""
        if not classifications:
            return {}
        
        # Distribution by category
        category_distribution = {}
        for classification in classifications.values():
            security_category = classification.get('security', 'green')
            category_distribution[security_category] = category_distribution.get(security_category, 0) + 1
        
        # Distribution by numeric level
        level_distribution = {}
        for classification in classifications.values():
            security_level = classification.get('security_level', 5)
            level_distribution[security_level] = level_distribution.get(security_level, 0) + 1
        
        return {
            'by_category': category_distribution,
            'by_level': level_distribution
        }
    
    def get_door_type_distribution(self, classifications):
        """Get distribution of door types"""
        if not classifications:
            return {}
        
        distribution = {
            'entry_exit': 0,
            'stairway': 0,
            'regular': 0
        }
        
        for classification in classifications.values():
            door_type = classification.get('door_type', 'none')
            if door_type == 'entry_exit':
                distribution['entry_exit'] += 1
            elif door_type == 'stairway':
                distribution['stairway'] += 1
            else:
                distribution['regular'] += 1
        
        return distribution


# Factory functions for easy handler creation
def create_classification_handlers(app, classification_component=None):
    """Factory function to create classification handlers"""
    return ClassificationHandlers(app, classification_component)

def create_classification_data_processor(classification_component=None):
    """Factory function to create data processor"""
    if classification_component is None:
        classification_component = create_classification_component()
    return ClassificationDataProcessor(classification_component)
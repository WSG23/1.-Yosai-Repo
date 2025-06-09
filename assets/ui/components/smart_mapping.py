# ui/components/smart_mapping.py
"""
Enhanced mapping component with smart header matching and memory functionality
"""

from dash import html, dcc
import json
import re
from typing import Dict, List, Tuple, Optional, Any
from difflib import SequenceMatcher
from ui.themes.style_config import MAPPING_STYLES, COLORS, SPACING, BORDER_RADIUS
from config.settings import REQUIRED_INTERNAL_COLUMNS

class SmartMappingComponent:
    """Enhanced mapping component with intelligent header matching"""
    
    def __init__(self):
        self.required_fields = REQUIRED_INTERNAL_COLUMNS
        
        # Enhanced keyword mapping for better matching
        self.field_keywords = {
            'Timestamp': [
                'timestamp', 'time', 'datetime', 'date', 'event_time', 'eventtime',
                'access_time', 'accesstime', 'log_time', 'logtime', 'created',
                'occurred', 'when', 'ts', 'dt', 'event_dt', 'access_dt'
            ],
            'UserID': [
                'userid', 'user_id', 'user', 'person', 'employee', 'badge',
                'card', 'identifier', 'id', 'person_id', 'personid', 'emp_id',
                'empid', 'badge_id', 'badgeid', 'card_id', 'cardid', 'user_code',
                'usercode', 'person_identifier', 'employee_id', 'employeeid',
                'credential', 'credentials', 'token_holder', 'holder'
            ],
            'DoorID': [
                'doorid', 'door_id', 'door', 'device', 'reader', 'access_point',
                'accesspoint', 'panel', 'controller', 'gate', 'entrance',
                'device_name', 'devicename', 'reader_id', 'readerid', 'door_name',
                'doorname', 'panel_id', 'panelid', 'location', 'point',
                'device_id', 'terminal', 'scanner', 'barrier'
            ],
            'EventType': [
                'eventtype', 'event_type', 'event', 'result', 'status', 'action',
                'access_result', 'accessresult', 'outcome', 'response',
                'access_status', 'accessstatus', 'access_type', 'accesstype',
                'entry_type', 'entrytype', 'authorization', 'auth_result',
                'authresult', 'grant', 'deny', 'success', 'failure', 'verdict'
            ]
        }
        
        # Additional pattern matching for complex headers
        self.field_patterns = {
            'Timestamp': [
                r'.*time.*', r'.*date.*', r'.*ts.*', r'.*dt.*', r'.*when.*',
                r'.*created.*', r'.*occurred.*', r'.*log.*time.*'
            ],
            'UserID': [
                r'.*user.*', r'.*person.*', r'.*employee.*', r'.*badge.*',
                r'.*card.*', r'.*id.*', r'.*credential.*', r'.*holder.*'
            ],
            'DoorID': [
                r'.*door.*', r'.*device.*', r'.*reader.*', r'.*panel.*',
                r'.*gate.*', r'.*entrance.*', r'.*point.*', r'.*terminal.*'
            ],
            'EventType': [
                r'.*event.*', r'.*result.*', r'.*status.*', r'.*action.*',
                r'.*access.*', r'.*outcome.*', r'.*auth.*', r'.*grant.*'
            ]
        }
    
    def smart_header_matching(self, csv_headers: List[str]) -> Dict[str, str]:
        """
        Intelligently match CSV headers to required fields
        Returns dict mapping CSV headers to internal field names
        """
        mapping = {}
        used_headers = set()
        
        # Clean headers for better matching
        cleaned_headers = {header: self._clean_header(header) for header in csv_headers}
        
        # Score all possible matches
        for internal_field in self.required_fields.keys():
            best_match = self._find_best_match(
                internal_field, 
                csv_headers, 
                cleaned_headers, 
                used_headers
            )
            
            if best_match:
                mapping[best_match] = internal_field
                used_headers.add(best_match)
        
        return mapping
    
    def _clean_header(self, header: str) -> str:
        """Clean header for better matching"""
        return re.sub(r'[^a-zA-Z0-9]', '', header.lower().strip())
    
    def _find_best_match(self, internal_field: str, csv_headers: List[str], 
                        cleaned_headers: Dict[str, str], used_headers: set) -> Optional[str]:
        """Find the best matching CSV header for an internal field"""
        best_score = 0
        best_header = None
        
        field_keywords = self.field_keywords.get(internal_field, [])
        field_patterns = self.field_patterns.get(internal_field, [])
        
        for header in csv_headers:
            if header in used_headers:
                continue
                
            score = self._calculate_match_score(
                header, 
                cleaned_headers[header], 
                field_keywords, 
                field_patterns
            )
            
            if score > best_score and score > 0.3:  # Minimum threshold
                best_score = score
                best_header = header
        
        return best_header
    
    def _calculate_match_score(self, original_header: str, cleaned_header: str,
                              keywords: List[str], patterns: List[str]) -> float:
        """Calculate match score for a header against field criteria"""
        score = 0.0
        header_lower = original_header.lower()
        
        # Exact keyword match (highest score)
        for keyword in keywords:
            if keyword == cleaned_header:
                score += 1.0
            elif keyword in cleaned_header:
                score += 0.8
            elif keyword in header_lower:
                score += 0.6
        
        # Pattern matching
        for pattern in patterns:
            if re.match(pattern, header_lower):
                score += 0.5
        
        # Fuzzy string matching
        for keyword in keywords:
            similarity = SequenceMatcher(None, keyword, cleaned_header).ratio()
            if similarity > 0.7:
                score += similarity * 0.4
        
        # Length penalty for very long headers (likely to be false positives)
        if len(original_header) > 50:
            score *= 0.8
        
        return min(score, 1.0)  # Cap at 1.0
    
    def load_saved_mappings(self, csv_headers: List[str], saved_mappings: str = "{}") -> Dict[str, str]:
        """Load saved mappings for this specific CSV structure"""
        try:
            all_saved = json.loads(saved_mappings) if saved_mappings else {}
            header_key = self._generate_header_key(csv_headers)
            return all_saved.get(header_key, {})
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def save_mapping(self, csv_headers: List[str], mapping: Dict[str, str], 
                    existing_saved: str = "{}") -> str:
        """Save mapping for this CSV structure"""
        try:
            all_saved = json.loads(existing_saved) if existing_saved else {}
            header_key = self._generate_header_key(csv_headers)
            all_saved[header_key] = mapping
            return json.dumps(all_saved)
        except (json.JSONDecodeError, TypeError):
            return json.dumps({self._generate_header_key(csv_headers): mapping})
    
    def _generate_header_key(self, headers: List[str]) -> str:
        """Generate unique key for header configuration"""
        return json.dumps(sorted(headers))
    
    def create_mapping_dropdowns(self, csv_headers: List[str], 
                               saved_preferences: Optional[Dict[str, str]] = None) -> List:
        """Create dropdown components for header mapping"""
        if not csv_headers:
            return []
        
        # Get smart suggestions if no saved preferences
        if not saved_preferences:
            smart_mapping = self.smart_header_matching(csv_headers)
        else:
            smart_mapping = saved_preferences
        
        # Create dropdown options with proper typing
        dropdown_options: List[Dict[str, Any]] = [{'label': '-- Select Column --', 'value': ''}]
        dropdown_options.extend([
            {'label': header, 'value': header} for header in csv_headers
        ])
        
        dropdowns = []
        
        for internal_key, display_name in self.required_fields.items():
            # Find suggested value
            suggested_csv_header = None
            for csv_header, mapped_key in smart_mapping.items():
                if mapped_key == internal_key:
                    suggested_csv_header = csv_header
                    break
            
            # Create dropdown with confidence indicator
            confidence = self._get_mapping_confidence(suggested_csv_header or "", internal_key, csv_headers)
            confidence_indicator = self._create_confidence_indicator(confidence)
            
            dropdown = html.Div([
                html.Label(
                    [display_name, confidence_indicator],
                    style=MAPPING_STYLES['label']
                ),
                dcc.Dropdown(
                    id=f'mapping-dropdown-{internal_key}',
                    options=dropdown_options,  # type: ignore
                    value=suggested_csv_header or '',
                    style=MAPPING_STYLES['dropdown'],
                    placeholder=f"Select column for {display_name}"
                )
            ], style={'marginBottom': SPACING['sm']})
            
            dropdowns.append(dropdown)
        
        return dropdowns
    
    def _get_mapping_confidence(self, csv_header: str, internal_field: str, 
                              all_headers: List[str]) -> str:
        """Get confidence level for a mapping"""
        if not csv_header or csv_header.strip() == "":
            return 'none'
        
        cleaned_headers = {h: self._clean_header(h) for h in all_headers}
        score = self._calculate_match_score(
            csv_header,
            cleaned_headers[csv_header],
            self.field_keywords.get(internal_field, []),
            self.field_patterns.get(internal_field, [])
        )
        
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        elif score >= 0.3:
            return 'low'
        else:
            return 'none'
    
    def _create_confidence_indicator(self, confidence: str) -> html.Span:
        """Create visual confidence indicator"""
        confidence_styles = {
            'high': {'color': COLORS['success'], 'symbol': '●'},
            'medium': {'color': COLORS['warning'], 'symbol': '◐'},
            'low': {'color': COLORS['critical'], 'symbol': '○'},
            'none': {'color': COLORS['text_secondary'], 'symbol': '○'}
        }
        
        style_info = confidence_styles.get(confidence, confidence_styles['none'])
        
        return html.Span(
            f" {style_info['symbol']}",
            style={
                'color': style_info['color'],
                'fontWeight': 'bold',
                'marginLeft': '5px'
            },
            title=f"Confidence: {confidence.title()}"
        )
    
    def create_mapping_validation_message(self, mapping: Dict[str, str], 
                                        csv_headers: List[str]) -> html.Div:
        """Create validation message for current mapping"""
        missing_fields = []
        duplicate_mappings = []
        invalid_headers = []
        
        # Check for missing required fields
        mapped_fields = set(mapping.values())
        for field in self.required_fields.keys():
            if field not in mapped_fields:
                missing_fields.append(self.required_fields[field])
        
        # Check for duplicate mappings
        header_counts = {}
        for csv_header in mapping.keys():
            if csv_header in header_counts:
                header_counts[csv_header] += 1
            else:
                header_counts[csv_header] = 1
        
        for header, count in header_counts.items():
            if count > 1:
                duplicate_mappings.append(header)
        
        # Check for invalid CSV headers
        for csv_header in mapping.keys():
            if csv_header and csv_header not in csv_headers:
                invalid_headers.append(csv_header)
        
        # Generate message
        if not missing_fields and not duplicate_mappings and not invalid_headers:
            return html.Div(
                "✓ All required fields mapped successfully!",
                style={
                    'color': COLORS['success'],
                    'padding': SPACING['sm'],
                    'textAlign': 'center',
                    'fontWeight': 'bold'
                }
            )
        
        issues = []
        if missing_fields:
            issues.append(f"Missing: {', '.join(missing_fields)}")
        if duplicate_mappings:
            issues.append(f"Duplicate mappings: {', '.join(duplicate_mappings)}")
        if invalid_headers:
            issues.append(f"Invalid headers: {', '.join(invalid_headers)}")
        
        return html.Div(
            f"⚠️ Issues: {'; '.join(issues)}",
            style={
                'color': COLORS['warning'],
                'padding': SPACING['sm'],
                'textAlign': 'center',
                'fontWeight': 'bold'
            }
        )


def create_mapping_component():
    """Factory function to create mapping component instance"""
    return SmartMappingComponent()
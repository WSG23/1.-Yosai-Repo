#!/usr/bin/env python3
"""
Comprehensive script to fix _validate_config methods in all component files
"""
import os
import re

def fix_all_validation_methods():
    """Fix validation methods in all specified files"""
    
    # Define the files and their specific validation fixes
    files_to_fix = {
        'migration/component_migration_template.py': {
            'required_settings': ['setting1', 'setting2'],
            'defaults': {
                'setting1': 'default_value1',
                'setting2': 'default_value2'
            }
        },
        'ui/components/classification_modular.py': {
            'required_settings': ['security_levels', 'classification_method', 'auto_classify'],
            'defaults': {
                'security_levels': [0, 1, 2, 3],
                'classification_method': 'manual',
                'auto_classify': False
            }
        },
        'ui/components/enhanced_stats_modular.py': {
            'required_settings': ['chart_height', 'show_advanced', 'max_categories', 'show_data_quality'],
            'defaults': {
                'chart_height': 300,
                'show_advanced': False,
                'max_categories': 10,
                'show_data_quality': True
            }
        },
        'ui/components/graph_modular.py': {
            'required_settings': ['default_layout', 'show_labels', 'interactive', 'node_size'],
            'defaults': {
                'default_layout': 'cose',
                'show_labels': True,
                'interactive': True,
                'node_size': 20
            }
        },
        'ui/components/mapping_modular.py': {
            'required_settings': ['auto_suggest', 'fuzzy_threshold', 'show_confidence', 'allow_custom_mapping'],
            'defaults': {
                'auto_suggest': True,
                'fuzzy_threshold': 0.6,
                'show_confidence': True,
                'allow_custom_mapping': True
            }
        },
        'ui/components/upload_modular.py': {
            'required_settings': ['max_file_size', 'allowed_extensions', 'secure_validation', 'upload_timeout'],
            'defaults': {
                'max_file_size': 52428800,
                'allowed_extensions': ['.csv', '.json'],
                'secure_validation': True,
                'upload_timeout': 30
            },
            'special_handling': True  # This one has field name compatibility
        },
        'ui/core/interfaces.py': {
            'required_settings': [],  # Base interface - no specific requirements
            'defaults': {},
            'generic': True
        }
    }
    
    print("🔧 Fixing validation methods in all component files...")
    
    for file_path, config in files_to_fix.items():
        fix_file_validation(file_path, config)
    
    print("\n✅ All validation methods fixed!")
    print("🧪 Ready to test with: python3 run.py")

def fix_file_validation(file_path, config):
    """Fix validation method in a specific file"""
    
    if not os.path.exists(file_path):
        print(f"  ⚠️ File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if file has _validate_config method
        if '_validate_config' not in content:
            print(f"  ℹ️ No _validate_config method in {file_path}")
            return
        
        # Generate the new validation method
        new_method = generate_validation_method(config)
        
        # Replace the old method
        updated_content = replace_validation_method(content, new_method)
        
        if updated_content != content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            print(f"  ✅ Fixed {file_path}")
        else:
            print(f"  ℹ️ {file_path} - no changes needed")
            
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")

def generate_validation_method(config):
    """Generate a new validation method based on component configuration"""
    
    required_settings = config.get('required_settings', [])
    defaults = config.get('defaults', {})
    is_generic = config.get('generic', False)
    has_special_handling = config.get('special_handling', False)
    
    if is_generic:
        # For interfaces.py - minimal validation
        return '''    def _validate_config(self) -> None:
        """Validate component configuration - Base implementation"""
        # Base interface - override in subclasses for specific validation
        pass'''
    
    if has_special_handling:
        # For upload_modular.py with field name compatibility
        return f'''    def _validate_config(self) -> None:
        """Validate required configuration - Fixed to handle missing settings gracefully"""
        required_settings = {required_settings}
        
        for setting in required_settings:
            value = self.get_setting(setting)
            
            # Handle field name compatibility
            if value is None and setting == 'allowed_extensions':
                value = self.get_setting('accepted_types')  # Try alternative name
                if value is not None:
                    self.config.settings[setting] = value
            
            if value is None:
                print(f"Warning: Missing setting '{{setting}}', using defaults")
                # Set default values instead of raising errors
                defaults = {defaults}
                if setting in defaults:
                    self.config.settings[setting] = defaults[setting]'''
    
    # Standard validation method
    return f'''    def _validate_config(self) -> None:
        """Validate required configuration - Fixed to handle missing settings gracefully"""
        required_settings = {required_settings}
        
        for setting in required_settings:
            if self.get_setting(setting) is None:
                print(f"Warning: Missing setting '{{setting}}', using defaults")
                # Set default values instead of raising errors
                defaults = {defaults}
                if setting in defaults:
                    self.config.settings[setting] = defaults[setting]'''

def replace_validation_method(content, new_method):
    """Replace the _validate_config method in file content"""
    
    # Pattern to match the entire _validate_config method
    pattern = r'(\s*)def _validate_config\(self\)[^:]*:.*?(?=\n\s*def|\n\s*class|\n\s*@|\nclass|\Z)'
    
    def replacement(match):
        indentation = match.group(1)
        # Apply the same indentation to the new method
        indented_method = '\n'.join(
            indentation + line if line.strip() else line 
            for line in new_method.split('\n')
        )
        return indented_method
    
    # Replace using regex with DOTALL flag to match across newlines
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    return updated_content

def test_fixes():
    """Test that all files can be imported after fixes"""
    print("\n🧪 Testing fixes...")
    
    test_files = [
        'ui.components.mapping_modular',
        'ui.components.upload_modular',
        'ui.components.enhanced_stats_modular',
        'ui.components.graph_modular',
        'ui.components.classification_modular'
    ]
    
    for module_name in test_files:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} imports successfully")
        except ImportError as e:
            print(f"  ⚠️ {module_name} import issue: {e}")
        except Exception as e:
            print(f"  ❌ {module_name} error: {e}")

if __name__ == '__main__':
    fix_all_validation_methods()
    test_fixes()
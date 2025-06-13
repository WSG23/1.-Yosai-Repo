#!/usr/bin/env python
"""
Validation script for modular component migration
"""
import os
import sys
import importlib

def validate_migration():
    """Validate that migration completed successfully"""
    
    print("🔍 Validating modular component migration...")
    
    # Check core infrastructure
    core_files = [
        'ui/core/interfaces.py',
        'ui/core/config_manager.py', 
        'ui/core/dependency_injection.py',
        'ui/core/component_registry.py'
    ]
    
    print("\n1. Checking core infrastructure...")
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            return False
    
    # Check configuration files
    config_files = [
        'config/theme.json',
        'config/icons.json',
        'config/components.json'
    ]
    
    print("\n2. Checking configuration files...")
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            return False
    
    # Check modular components
    modular_components = [
        'ui.components.upload_modular',
        # Add others as they are created
    ]
    
    print("\n3. Checking modular components...")
    for module_name in modular_components:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name} - IMPORT ERROR: {e}")
            return False
    
    # Test registry
    print("\n4. Testing component registry...")
    try:
        from ui.core.component_registry import get_registry
        registry = get_registry()
        print("  ✅ Registry initialized successfully")
    except Exception as e:
        print(f"  ❌ Registry error: {e}")
        return False
    
    print("\n✅ Migration validation completed successfully!")
    return True

if __name__ == '__main__':
    success = validate_migration()
    sys.exit(0 if success else 1)

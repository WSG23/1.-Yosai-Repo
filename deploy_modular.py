#!/usr/bin/env python
"""
Deployment script for modular application
"""
import shutil
import os
from datetime import datetime

def deploy_modular_app():
    """Deploy the modular application"""
    
    print("�� Deploying modular application...")
    
    # Backup original files
    backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if os.path.exists('app.py'):
        backup_name = f"app_original_{backup_time}.py"
        shutil.copy('app.py', backup_name)
        print(f"  ✅ Backed up original app.py to {backup_name}")
    
    if os.path.exists('app_factory.py'):
        backup_name = f"app_factory_original_{backup_time}.py"
        shutil.copy('app_factory.py', backup_name)
        print(f"  ✅ Backed up original app_factory.py to {backup_name}")
    
    # Replace app.py with modular version
    if os.path.exists('app_modular.py'):
        shutil.copy('app_modular.py', 'app.py')
        print("  ✅ Replaced app.py with modular version")
    
    # Update app_factory.py to use modular components
    create_modular_app_factory()
    print("  ✅ Updated app_factory.py for modular components")
    
    # Create legacy directory for old components
    if not os.path.exists('ui/components/legacy'):
        os.makedirs('ui/components/legacy')
    
    # Move legacy components
    legacy_files = [
        'ui/components/upload_legacy.py',
        'ui/components/mapping_legacy.py',
        'ui/components/enhanced_stats_legacy.py',
        'ui/components/graph_legacy.py'
    ]
    
    for file_path in legacy_files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            target = f"ui/components/legacy/{filename}"
            shutil.move(file_path, target)
            print(f"  ✅ Moved {file_path} to legacy folder")
    
    print("\n✅ Deployment completed successfully!")
    print("  📁 Legacy components moved to ui/components/legacy/")
    print("  🔄 Original files backed up")
    print("  🚀 Modular app connected to run.py")

def create_modular_app_factory():
    """Create updated app_factory.py that uses modular components"""
    
    factory_content = '''# app_factory.py - Updated for modular components
"""
Application factory for modular Dash application
"""
import dash
import dash_bootstrap_components as dbc
from dash import html
import logging
import os

# Import the modular app creation function
from app_modular import create_modular_app

def create_app(mode='development'):
    """
    Create Dash application using modular components
    
    Args:
        mode: 'development' or 'production'
    """
    
    # Configure logging
    log_level = logging.DEBUG if mode == 'development' else logging.INFO
    logging.basicConfig(level=log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Creating application in {mode} mode with modular components")
    
    # Create the modular app
    app = create_modular_app()
    
    # Configure based on mode
    if mode == 'production':
        app.enable_dev_tools(debug=False)
        logger.info("Production mode: Dev tools disabled")
    else:
        app.enable_dev_tools(debug=True, dev_tools_hot_reload=True)
        logger.info("Development mode: Dev tools enabled")
    
    return app
'''
    
    with open('app_factory.py', 'w') as f:
        f.write(factory_content)

if __name__ == '__main__':
    deploy_modular_app()

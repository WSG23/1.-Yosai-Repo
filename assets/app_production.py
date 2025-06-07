# app_production.py - Production-ready Yōsai Intel Dashboard
import dash
import sys
import os
import logging
from waitress import serve

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash_bootstrap_components as dbc

# Import configuration
from config.settings import get_settings
from config.app_config import get_config

# Import UI components and handlers
from ui.components.upload import create_enhanced_upload_component
from ui.components.mapping import create_mapping_component
from ui.components.classification import create_classification_component
from ui.components.upload_handlers import create_upload_handlers
from ui.components.mapping_handlers import create_mapping_handlers
from ui.components.classification_handlers import create_classification_handlers

# Import layout
from ui.pages.main_page import create_main_layout

# Logging setup
from utils.logging_config import setup_application_logging, get_logger

def create_production_app():
    """Create and configure the production Dash application"""
    
    # Setup logging for production
    setup_application_logging()
    logger = get_logger(__name__)
    
    logger.info("🚀 Initializing Yōsai Intel Dashboard (Production Mode)")
    
    # Create Dash app with production settings
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder="assets",
        external_stylesheets=[dbc.themes.DARKLY]
    )
    
    # Asset URLs
    ICON_UPLOAD_DEFAULT = app.get_asset_url('upload_file_csv_icon.png')
    ICON_UPLOAD_SUCCESS = app.get_asset_url('upload_file_csv_icon_success.png') 
    ICON_UPLOAD_FAIL = app.get_asset_url('upload_file_csv_icon_fail.png')
    MAIN_LOGO_PATH = app.get_asset_url('logo_white.png')
    
    # Create main layout
    app.layout = create_main_layout(
        app_instance=app,
        main_logo_path=MAIN_LOGO_PATH,
        icon_upload_default=ICON_UPLOAD_DEFAULT
    )
    
    # Placeholder for registering callbacks using handler factories
    logger.info("✅ Production app created successfully")
    return app

if __name__ == "__main__":
    app = create_production_app()
    app.run_server(debug=False, host='0.0.0.0', port=8050)

# app_factory.py - Updated for modular components
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

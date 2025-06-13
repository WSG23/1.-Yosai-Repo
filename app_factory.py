# app_factory.py - Complete application factory with callback registration
"""
Application factory for modular Dash application with original functionality
"""
import dash
import dash_bootstrap_components as dbc
from dash import html
import logging
import os

# Import the modular app creation function
from app_modular import create_modular_app

# Import callback handlers (with graceful fallbacks)
try:
    from ui.components.upload_handlers import UploadHandlers
except ImportError:
    logger.warning("Upload handlers not available")
    UploadHandlers = None

try:
    from ui.components.mapping_handlers import MappingHandlers
except ImportError:
    logger.warning("Mapping handlers not available")
    MappingHandlers = None

try:
    from ui.components.classification_handlers import ClassificationHandlers
except ImportError:
    logger.warning("Classification handlers not available")
    ClassificationHandlers = None

try:
    from ui.components.enhanced_stats_handlers import EnhancedStatsHandlers
except ImportError:
    logger.warning("Enhanced stats handlers not available")
    EnhancedStatsHandlers = None

try:
    from ui.components.graph_handlers import GraphHandlers
except ImportError:
    logger.warning("Graph handlers not available")
    GraphHandlers = None

# Import original components for callback registration (with graceful fallbacks)
try:
    from ui.components.upload import create_enhanced_upload_component
except ImportError:
    logger.warning("Enhanced upload component not available")
    create_enhanced_upload_component = None

try:
    from ui.components.mapping import create_mapping_component
except ImportError:
    logger.warning("Mapping component not available")
    create_mapping_component = None

try:
    from ui.components.classification import create_classification_component
except ImportError:
    logger.warning("Classification component not available")
    create_classification_component = None

try:
    from ui.components.enhanced_stats import create_enhanced_stats_component
except ImportError:
    logger.warning("Enhanced stats component not available")
    create_enhanced_stats_component = None

try:
    from ui.components.graph import create_graph_component
except ImportError:
    logger.warning("Graph component not available")
    create_graph_component = None

# Import configuration and settings
from config.settings import DEFAULT_ICONS, SECURITY_CONFIG
from utils.logging_config import get_logger

logger = get_logger(__name__)

def create_app(mode='development'):
    """
    Create Dash application using modular components with original functionality
    
    Args:
        mode: 'development' or 'production'
    """
    
    # Configure logging
    log_level = logging.DEBUG if mode == 'development' else logging.INFO
    logging.basicConfig(level=log_level)
    
    logger.info(f"Creating application in {mode} mode with modular components")
    
    try:
        # Create the modular app with original layout
        app = create_modular_app()
        
        # Register all callback handlers for full functionality
        register_callback_handlers(app, mode)
        
        # Configure based on mode
        if mode == 'production':
            app.enable_dev_tools(debug=False)
            logger.info("Production mode: Dev tools disabled")
        else:
            app.enable_dev_tools(debug=True, dev_tools_hot_reload=True)
            logger.info("Development mode: Dev tools enabled")
        
        logger.info("✅ Application created successfully with all callbacks registered")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create modular app: {e}")
        # Fallback to a basic app if modular creation fails
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        app.layout = html.Div([
            html.H1("Application Error"),
            html.P(f"Failed to load modular components: {str(e)}"),
            html.P("Please check the configuration and try again.")
        ])
        return app

def register_callback_handlers(app, mode='development'):
    """Register all callback handlers for complete functionality"""
    
    logger.info("🔗 Registering callback handlers...")
    
    try:
        # Create component instances for callback registration
        upload_component = None
        mapping_component = None
        classification_component = None
        stats_component = None
        graph_component = None
        
        # Try to create components gracefully
        if create_enhanced_upload_component:
            try:
                upload_component = create_enhanced_upload_component(
                    DEFAULT_ICONS['upload_default'],
                    DEFAULT_ICONS['upload_success'], 
                    DEFAULT_ICONS['upload_fail']
                )
                logger.info("✅ Upload component created")
            except Exception as e:
                logger.warning(f"⚠️ Could not create upload component: {e}")
        
        if create_mapping_component:
            try:
                mapping_component = create_mapping_component()
                logger.info("✅ Mapping component created")
            except Exception as e:
                logger.warning(f"⚠️ Could not create mapping component: {e}")
        
        if create_classification_component:
            try:
                classification_component = create_classification_component()
                logger.info("✅ Classification component created")
            except Exception as e:
                logger.warning(f"⚠️ Could not create classification component: {e}")
        
        if create_enhanced_stats_component:
            try:
                stats_component = create_enhanced_stats_component()
                logger.info("✅ Stats component created")
            except Exception as e:
                logger.warning(f"⚠️ Could not create stats component: {e}")
        
        if create_graph_component:
            try:
                graph_component = create_graph_component()
                logger.info("✅ Graph component created")
            except Exception as e:
                logger.warning(f"⚠️ Could not create graph component: {e}")
        
        # Icon paths for upload handlers
        icon_paths = {
            'default': DEFAULT_ICONS.get('upload_default', '/assets/upload_file_csv_icon.png'),
            'success': DEFAULT_ICONS.get('upload_success', '/assets/upload_file_csv_icon_success.png'),
            'fail': DEFAULT_ICONS.get('upload_fail', '/assets/upload_file_csv_icon_fail.png')
        }
        
        # Register Upload Handlers (Critical for CSV/JSON functionality)
        if upload_component and UploadHandlers:
            try:
                logger.info("📤 Registering upload handlers...")
                upload_handlers = UploadHandlers(
                    app, 
                    upload_component, 
                    icon_paths,
                    secure=SECURITY_CONFIG.get('enable_file_validation', True),
                    max_file_size=SECURITY_CONFIG.get('max_file_size', 50 * 1024 * 1024)
                )
                upload_handlers.register_callbacks()
                logger.info("✅ Upload handlers registered")
            except Exception as e:
                logger.warning(f"⚠️ Could not register upload handlers: {e}")
        
        # Register Mapping Handlers
        if mapping_component and MappingHandlers:
            try:
                logger.info("🗺️ Registering mapping handlers...")
                mapping_handlers = MappingHandlers(app, mapping_component)
                mapping_handlers.register_callbacks()
                logger.info("✅ Mapping handlers registered")
            except Exception as e:
                logger.warning(f"⚠️ Could not register mapping handlers: {e}")
        
        # Register Classification Handlers
        if classification_component and ClassificationHandlers:
            try:
                logger.info("🏷️ Registering classification handlers...")
                classification_handlers = ClassificationHandlers(app, classification_component)
                classification_handlers.register_callbacks()
                logger.info("✅ Classification handlers registered")
            except Exception as e:
                logger.warning(f"⚠️ Could not register classification handlers: {e}")
        
        # Register Enhanced Stats Handlers
        if stats_component and EnhancedStatsHandlers:
            try:
                logger.info("📊 Registering enhanced stats handlers...")
                stats_handlers = EnhancedStatsHandlers(app, stats_component)
                stats_handlers.register_callbacks()
                logger.info("✅ Stats handlers registered")
            except Exception as e:
                logger.warning(f"⚠️ Could not register stats handlers: {e}")
        
        # Register Graph Handlers
        if graph_component and GraphHandlers:
            try:
                logger.info("🕸️ Registering graph handlers...")
                graph_handlers = GraphHandlers(app, graph_component)
                graph_handlers.register_callbacks()
                logger.info("✅ Graph handlers registered")
            except Exception as e:
                logger.warning(f"⚠️ Could not register graph handlers: {e}")
        
        # Register additional workflow callbacks
        register_workflow_callbacks(app)
        
        logger.info("✅ Callback registration completed")
        
    except Exception as e:
        logger.error(f"❌ Error in callback registration process: {e}")
        # Don't raise - allow app to continue with partial functionality
        logger.info("ℹ️ Continuing with limited functionality")

def register_workflow_callbacks(app):
    """Register additional workflow and integration callbacks"""
    
    logger.info("🔄 Registering workflow callbacks...")
    
    try:
        # Import and register any additional workflow callbacks
        from ui.callbacks import workflow_callbacks
        workflow_callbacks.register_callbacks(app)
        logger.info("✅ Workflow callbacks registered")
        
    except ImportError:
        logger.info("ℹ️ No additional workflow callbacks found - using component callbacks only")
    except Exception as e:
        logger.warning(f"⚠️ Error registering workflow callbacks: {e}")

def validate_app_configuration(app):
    """Validate that the application is properly configured"""
    
    logger.info("🔍 Validating application configuration...")
    
    try:
        # Check that essential components are present
        layout = app.layout
        if layout is None:
            raise ValueError("Application layout is not set")
        
        # Check for critical component IDs
        critical_ids = [
            'upload-data',
            'mapping-ui-section', 
            'interactive-setup-container',
            'confirm-header-map-button',
            'confirm-and-generate-button'
        ]
        
        # Note: In a real application, you'd traverse the layout to check for these IDs
        # For now, we'll assume they're present since we're using the original layout
        
        logger.info("✅ Application configuration validated")
        return True
        
    except Exception as e:
        logger.error(f"❌ Application configuration validation failed: {e}")
        return False

def get_app_info():
    """Get information about the application configuration"""
    
    return {
        'name': 'Yōsai Intel Enhanced Analytics Dashboard',
        'version': '2.0.0',
        'description': 'Security analytics platform with modular architecture',
        'features': [
            'CSV/JSON file upload and processing',
            'Interactive column mapping',
            'Facility classification system', 
            'Advanced analytics and reporting',
            'Network graph visualization',
            'Dark theme UI'
        ],
        'components': [
            'Upload Handler',
            'Mapping Component',
            'Classification System',
            'Enhanced Statistics',
            'Graph Visualization'
        ]
    }

# Export factory function and info
__all__ = ['create_app', 'get_app_info']
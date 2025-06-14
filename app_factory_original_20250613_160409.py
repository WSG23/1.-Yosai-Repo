# app_factory.py
"""
Unified Yōsai Application Factory
Single source for both development and production app creation
"""

import sys
import os
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration imports
from config.settings import get_config, get_ui_config
from utils.logging_config import setup_application_logging, get_logger

# Import dash_cytoscape for graph elements
try:
    import dash_cytoscape as cyto
    CYTOSCAPE_AVAILABLE = True
except ImportError:
    cyto = None  # type: ignore[assignment]
    CYTOSCAPE_AVAILABLE = False

# Type-safe JSON serialization (moved from app.py)
def make_json_serializable(data: Any) -> Any:
    """Convert numpy data types to native Python types for JSON serialization."""
    import numpy as np
    import pandas as pd
    
    if isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()
    elif isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    return data

class AppFactory:
    """Factory for creating Dash applications with different configurations"""
    
    def __init__(self):
        self.config = get_config()
        self.ui_config = get_ui_config()
        self.components_available = {}
        self._detect_components()
    
    def _detect_components(self):
        """Detect available UI components"""
        print("🔍 Detecting available components...")
        
        # Enhanced stats component
        try:
            from ui.components.enhanced_stats import create_enhanced_stats_component
            self.components_available["enhanced_stats"] = True
            print("   ✅ Enhanced stats component available")
        except ImportError as e:
            print(f"   ⚠️ Enhanced stats component not available: {e}")
            self.components_available["enhanced_stats"] = False
        
        # Upload component
        try:
            from ui.components.upload import create_enhanced_upload_component
            self.components_available["upload"] = True
            print("   ✅ Upload component available")
        except ImportError as e:
            print(f"   ⚠️ Upload component not available: {e}")
            self.components_available["upload"] = False
        
        # Classification component
        try:
            from ui.components.classification import create_classification_component
            self.components_available["classification"] = True
            print("   ✅ Classification component available")
        except ImportError as e:
            print(f"   ⚠️ Classification component not available: {e}")
            self.components_available["classification"] = False
        
        # Main layout
        try:
            from ui.pages.main_page import create_main_layout
            self.components_available["main_layout"] = True
            print("   ✅ Main layout available")
        except ImportError as e:
            print(f"   ⚠️ Main layout not available: {e}")
            self.components_available["main_layout"] = False
        
        # Cytoscape for graphs
        try:
            import dash_cytoscape as cyto
            self.components_available["cytoscape"] = True
            print("   ✅ Cytoscape available")
        except ImportError as e:
            print(f"   ⚠️ Cytoscape not available: {e}")
            self.components_available["cytoscape"] = False
        
        # Plotly for charts
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            self.components_available["plotly"] = True
            print("   ✅ Plotly available")
        except ImportError as e:
            print(f"   ⚠️ Plotly not available: {e}")
            self.components_available["plotly"] = False
    
    def create_app(self, mode: str = "development") -> dash.Dash:
        """
        Create Dash application configured for the specified mode
        
        Args:
            mode: "development" or "production"
        
        Returns:
            Configured Dash application
        """
        is_production = mode.lower() in ("production", "prod")
        
        # Setup logging based on mode
        if is_production:
            setup_application_logging(log_level="INFO", log_file="logs/app.log")
            logger = get_logger(__name__)
            logger.info("🚀 Initializing Yōsai Intel Dashboard (Production Mode)")
        else:
            setup_application_logging(log_level="DEBUG")
            logger = get_logger(__name__)
            logger.info("🛠️ Initializing Yōsai Intel Dashboard (Development Mode)")
        
        # Create Dash app with mode-specific settings
        app_config = self._get_app_config(is_production)
        app = dash.Dash(**app_config)
        
        # Set server reference
        assert app.server is not None
        app.server.config.update(self._get_server_config(is_production))
        
        # Get asset URLs
        asset_urls = self._get_asset_urls(app)
        
        # Create layout
        try:
            app.layout = self._create_layout(app, asset_urls, is_production)
            logger.info("✅ Layout created successfully")
        except Exception as e:
            logger.error(f"❌ Layout creation failed: {e}")
            app.layout = self._create_fallback_layout(asset_urls)
            logger.info("🔄 Using fallback layout")
        
        # Register callbacks
        try:
            self._register_callbacks(app, asset_urls, is_production)
            logger.info("✅ Callbacks registered successfully")
        except Exception as e:
            logger.error(f"❌ Callback registration failed: {e}")
            logger.error(traceback.format_exc())
            # Continue with app creation even if callbacks fail
        
        logger.info(f"🎉 Yōsai Dashboard created successfully - Mode: {mode}")
        return app
    
    def _get_app_config(self, is_production: bool) -> Dict[str, Any]:
        """Get Dash app configuration based on mode"""
        config = {
            "suppress_callback_exceptions": True,
            "assets_folder": "assets",
            "external_stylesheets": [dbc.themes.DARKLY],
            "meta_tags": [
                {"name": "viewport", "content": "width=device-width, initial-scale=1"},
                {
                    "name": "description", 
                    "content": "Yōsai Enhanced Analytics Dashboard"
                },
            ],
        }
        

        # Development tools are configured when running the server
        # via run.py. The Dash constructor only contains core settings.

        return config
    
    def _get_server_config(self, is_production: bool) -> Dict[str, Any]:
        """Get Flask server configuration based on mode"""
        config: Dict[str, Any] = {
            "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
        }

        if is_production:
            extra: Dict[str, Any] = {
                "SESSION_COOKIE_SECURE": True,
                "SESSION_COOKIE_HTTPONLY": True,
                "SESSION_COOKIE_SAMESITE": "Lax",
            }
            config.update(extra)

        return config
    
    def _get_asset_urls(self, app: dash.Dash) -> Dict[str, str]:
        """Get asset URLs for the application"""
        return {
            "upload_default": app.get_asset_url("upload_file_csv_icon.png"),
            "upload_success": app.get_asset_url("upload_file_csv_icon_success.png"),
            "upload_fail": app.get_asset_url("upload_file_csv_icon_fail.png"),
            "main_logo": app.get_asset_url("logo_white.png"),
        }
    
    def _create_layout(self, app: dash.Dash, asset_urls: Dict[str, str], is_production: bool):
        """Create the main application layout"""
        
        # Try to use the existing layout creation function
        if self.components_available.get("main_layout"):
            try:
                from ui.pages.main_page import create_main_layout
                return self._create_enhanced_layout(app, asset_urls, create_main_layout)
            except Exception as e:
                print(f"❌ Enhanced layout creation failed: {e}")
        
        # Try to use the fixed layout function from current app.py
        try:
            # Import the existing layout function
            from app import create_fixed_layout_with_required_elements
            return create_fixed_layout_with_required_elements(
                app, asset_urls["main_logo"], asset_urls["upload_default"]
            )
        except Exception as e:
            print(f"❌ Fixed layout creation failed: {e}")
            return self._create_fallback_layout(asset_urls)
    
    def _create_enhanced_layout(self, app: dash.Dash, asset_urls: Dict[str, str], create_main_layout):
        """Create enhanced layout with all required elements"""
        
        # Create base layout
        base_layout = create_main_layout(app, asset_urls["main_logo"], asset_urls["upload_default"])
        
        # Add required data stores and missing elements
        required_stores = [
            dcc.Store(id="uploaded-file-store"),
            dcc.Store(id="csv-headers-store"),
            dcc.Store(id="column-mapping-store", storage_type="local"),
            dcc.Store(id="all-doors-from-csv-store"),
            dcc.Store(id="processed-data-store"),
            dcc.Store(id="device-attrs-store"),
            dcc.Store(id="manual-door-classifications-store", storage_type="local"),
            dcc.Store(id="num-floors-store", data=1),
            dcc.Store(id="stats-data-store"),
            dcc.Store(id="enhanced-stats-data-store"),
        ]
        
        # Add enhanced stats component if available
        enhanced_elements = []
        if self.components_available.get("enhanced_stats"):
            try:
                from ui.components.enhanced_stats import create_enhanced_stats_component
                stats_component = create_enhanced_stats_component()
                enhanced_elements.append(stats_component.create_enhanced_stats_container())
            except Exception as e:
                print(f"⚠️ Could not create enhanced stats: {e}")
        
        # Missing callback placeholders
        callback_placeholders = [
            html.P(id="entry-exit-ratio", children="Entry/Exit: N/A", style={"display": "none"}),
            html.P(id="weekend-vs-weekday", children="Weekend vs Weekday: N/A", style={"display": "none"}),
        ]

        # Add graph container that callbacks expect
        graph_containers = []
        if CYTOSCAPE_AVAILABLE:
            try:
                from ui.components.graph import create_graph_container
                graph_containers.append(create_graph_container())
                print("   ✅ Original styled graph container loaded")
            except Exception as e:
                print(f"   ⚠️ Could not load styled graph container: {e}")
                graph_containers.append(self._create_basic_graph_container())
        else:
            # Fallback without cytoscape
            graph_containers.append(html.Div(
                id="graph-output-container",
                style={"display": "none", "margin": "20px auto", "padding": "20px"},
                children=[
                    html.Div(id="onion-graph-container", children=[
                        html.H3("Security Model Visualization", style={"color": "white", "textAlign": "center"}),

                        # Hidden dummy elements for callbacks
                        dcc.Dropdown(id='graph-layout-selector', style={'display': 'none'}),
                        dcc.Checklist(id='graph-filters', style={'display': 'none'}),
                        html.Pre(id='tap-node-data-output', style={'display': 'none'}),

                        html.Div(
                            id="onion-graph",
                            style={"height": "600px", "width": "100%", "border": "1px solid #ccc"},
                            children=html.P(
                                "Graph visualization requires dash-cytoscape",
                                style={"color": "white", "textAlign": "center", "paddingTop": "250px"}
                            )
                        )
                    ])
                ]
            ))

        return html.Div([
            *required_stores,
            base_layout,
            *enhanced_elements,
            *callback_placeholders,
            *graph_containers,
        ])
    
    def _create_fallback_layout(self, asset_urls: Dict[str, str]):
        """Create a simple fallback layout when main layout fails"""
        # Try to use the original graph container even in fallback
        graph_container = None
        if CYTOSCAPE_AVAILABLE:
            try:
                from ui.components.graph import create_graph_container
                graph_container = create_graph_container()
            except Exception:
                graph_container = self._create_basic_graph_container()
        else:
            graph_container = html.Div(
                id="graph-output-container",
                style={"display": "none"},
                children=[
                    dcc.Dropdown(id='graph-layout-selector', style={'display': 'none'}),
                    dcc.Checklist(id='graph-filters', style={'display': 'none'}),
                    html.Pre(id='tap-node-data-output', style={'display': 'none'}),
                    html.Div(id="onion-graph", children="Cytoscape not available")
                ]
            )

        return html.Div([
            # Required stores
            dcc.Store(id="uploaded-file-store"),
            dcc.Store(id="csv-headers-store"),
            dcc.Store(id="column-mapping-store", storage_type="local"),
            dcc.Store(id="processed-data-store"),
            dcc.Store(id="enhanced-stats-data-store"),

            # Graph container with original styling
            graph_container,

            # Missing callback targets
            html.P(id="entry-exit-ratio", children="Entry/Exit: N/A", style={"display": "none"}),
            html.P(id="weekend-vs-weekday", children="Weekend vs Weekday: N/A", style={"display": "none"}),

            # Simple layout
            html.Div([
                html.H1("Yōsai Dashboard", style={"textAlign": "center", "color": "white"}),
                html.P("Loading components...", style={"textAlign": "center", "color": "gray"}),
                html.Div(id="upload-container"),
                html.Div(id="content-container"),
            ], style={"padding": "20px"})
        ])
    
    def _register_callbacks(self, app: dash.Dash, asset_urls: Dict[str, str], is_production: bool):
        """Register all application callbacks"""
        
        # Import and register callbacks from the existing system
        try:
            # Use the existing callback registration system
            from app import register_all_callbacks_safely
            register_all_callbacks_safely(app)
            
        except Exception as e:
            print(f"❌ Callback registration failed: {e}")
            # Try individual component registration as fallback
            self._register_fallback_callbacks(app, asset_urls)
    
    def _register_fallback_callbacks(self, app: dash.Dash, asset_urls: Dict[str, str]):
        """Register basic callbacks if main registration fails"""
        
        # Register upload handlers
        if self.components_available.get("upload"):
            try:
                from ui.components.upload_handlers import UploadHandlers
                from ui.components.upload import create_enhanced_upload_component
                
                upload_component = create_enhanced_upload_component(
                    asset_urls["upload_default"],
                    asset_urls["upload_success"],
                    asset_urls["upload_fail"],
                )

                icon_paths = {
                    "default": asset_urls["upload_default"],
                    "success": asset_urls["upload_success"],
                    "fail": asset_urls["upload_fail"],
                }

                upload_handlers = UploadHandlers(
                    app,
                    upload_component,
                    icon_paths,
                    secure=True,
                    max_file_size=50 * 1024 * 1024,
                )
                upload_handlers.register_callbacks()
                print("   ✅ Upload callbacks registered (fallback)")
                
            except Exception as e:
                print(f"   ❌ Upload callback fallback failed: {e}")
        
        # Register mapping handlers
        try:
            from ui.components.mapping_handlers import MappingHandlers
            mapping_handlers = MappingHandlers(app)
            mapping_handlers.register_callbacks()
            print("   ✅ Mapping callbacks registered (fallback)")
        except Exception as e:
            print(f"   ❌ Mapping callback fallback failed: {e}")
        
        # Register classification handlers
        try:
            from ui.components.classification_handlers import ClassificationHandlers
            classification_handlers = ClassificationHandlers(app)
            classification_handlers.register_callbacks()
            print("   ✅ Classification callbacks registered (fallback)")
        except Exception as e:
            print(f"   ❌ Classification callback fallback failed: {e}")

        # Register enhanced stats handlers
        try:
            from ui.components.enhanced_stats_handlers import EnhancedStatsHandlers
            stats_handlers = EnhancedStatsHandlers(app)
            stats_handlers.register_callbacks()
            print("   ✅ Enhanced stats callbacks registered (fallback)")
        except Exception as e:
            print(f"   ❌ Enhanced stats callback fallback failed: {e}")

        # Register graph handlers
        try:
            from ui.components.graph_handlers import GraphHandlers
            graph_handlers = GraphHandlers(app)
            graph_handlers.register_callbacks()
            print("   ✅ Graph callbacks registered (fallback)")
        except Exception as e:
            print(f"   ❌ Graph callback fallback failed: {e}")

        # Register orchestrator callbacks
        try:
            from ui.orchestrator import main_data_orchestrator, update_graph_elements, update_container_visibility, update_status_display
            print("   ✅ Orchestrator callbacks imported (fallback)")
        except Exception as e:
            print(f"   ❌ Orchestrator callback fallback failed: {e}")

    def _create_basic_graph_container(self):
        """Create basic graph container as fallback"""
        return html.Div(
            id="graph-output-container",
            style={"display": "none", "margin": "20px auto", "padding": "20px"},
            children=[
                html.H2(
                    "Area Layout Model",
                    id="area-layout-model-title",
                    style={
                        'textAlign': 'center',
                        'color': 'white',
                        'marginBottom': '20px',
                        'fontSize': '1.8rem'
                    }
                ),
                html.Div(
                    id='cytoscape-graphs-area',
                    style={
                        'width': '100%',
                        'height': '600px',
                        'display': 'flex',
                        'justify-content': 'center',
                        'align-items': 'center',
                        'background-color': '#2a2a2a',
                        'border-radius': '8px',
                        'border': '1px solid #444',
                        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                        'position': 'relative',
                        'overflow': 'hidden',
                        'margin': '20px auto'
                    },
                    children=[
                        cyto.Cytoscape(
                    id="onion-graph",
                    style={
                        'width': '100%',
                        'height': '100%',
                        'background-color': '#1a1a1a',
                        'border-radius': '6px'
                    },
                    elements=[],
                    layout={'name': 'cose'},
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'background-color': '#2a2a2a',
                                'border-color': '#444',
                                'border-width': 2,
                                'label': 'data(label)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'font-size': '12px',
                                'color': 'white',
                                'width': 60,
                                'height': 60,
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 3,
                                'line-color': '#666',
                                'target-arrow-color': '#666',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'                                    }
                                }
                            ],
                            wheelSensitivity=1
                        )
                    ]
                ),
                html.Pre(
                    id='tap-node-data-output',
                    style={
                        'border': '1px solid #444',
                        'padding': '10px',
                        'margin': '10px auto',
                        'background-color': '#2a2a2a',
                        'color': 'white',
                        'font-size': '14px',
                        'border-radius': '6px',
                        'text-align': 'center',
                        'white-space': 'pre-wrap',
                        'overflow-wrap': 'break-word',
                        'max-width': '800px'
                    },
                    children="Upload a file, map headers, (optionally classify doors), then Confirm & Generate. Tap a node for its details."
                ),
                # Hidden controls for callbacks
                dcc.Dropdown(id='graph-layout-selector', style={'display': 'none'}),
                dcc.Checklist(id='graph-filters', style={'display': 'none'}),
            ]
        )

# Factory instance
app_factory = AppFactory()

def create_app(mode: str = "development") -> dash.Dash:
    """
    Create Yōsai Dashboard application
    
    Args:
        mode: "development" or "production"
    
    Returns:
        Configured Dash application
    """
    return app_factory.create_app(mode)

# Backwards compatibility
def create_production_app() -> dash.Dash:
    """Create production app (backwards compatibility)"""
    return create_app("production")

def create_development_app() -> dash.Dash:
    """Create development app (backwards compatibility)"""
    return create_app("development")

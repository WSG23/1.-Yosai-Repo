#!/usr/bin/env python3
"""
Unified Yōsai Dashboard Runner
Single entry point for both development and production modes
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def validate_environment():
    """Validate required dependencies and environment"""
    try:
        # Check dash-cytoscape version
        import dash_cytoscape as cyto
        from packaging.version import Version
        
        if Version(cyto.__version__) < Version("0.3.0"):
            raise RuntimeError(
                f"dash-cytoscape>=0.3.0 required, found {cyto.__version__}. "
                "Please run 'pip install -r requirements.txt'"
            )
        print(f"✅ dash-cytoscape {cyto.__version__} OK")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Environment validation warning: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Yōsai Analytics Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Development mode (default)
  python run.py dev                # Development mode explicitly
  python run.py prod               # Production mode
  MODE=prod python run.py          # Production mode via environment
  python run.py --host 0.0.0.0    # Custom host
  python run.py --port 8080       # Custom port
  python run.py --debug           # Force debug mode
        """
    )
    
    parser.add_argument(
        "mode", 
        nargs="?", 
        choices=["dev", "development", "prod", "production"],
        default=None,
        help="Application mode (default: from MODE env var or 'dev')"
    )
    
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to (default: 127.0.0.1 for dev, 0.0.0.0 for prod)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to bind to (default: 8050)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Force debug mode (overrides production settings)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Logging level"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes for production (Waitress)"
    )
    
    return parser.parse_args()

def determine_mode(args):
    """Determine the application mode from arguments and environment"""
    
    # Priority: CLI argument > environment variable > default
    if args.mode:
        mode = args.mode
    else:
        mode = os.getenv("MODE", "dev")
    
    # Normalize mode
    mode = mode.lower()
    if mode in ("prod", "production"):
        return "production"
    else:
        return "development"

def run_development(app, host="127.0.0.1", port=8050, debug=True, **kwargs):
    """Run application in development mode"""
    print(f"🛠️ Starting Yōsai Dashboard in DEVELOPMENT mode")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🔧 Debug: {debug}")
    print("=" * 50)
    
    app.run_server(
        debug=debug,
        host=host,
        port=port,
        dev_tools_hot_reload=True,
        dev_tools_ui=True,
        dev_tools_props_check=False,
    )

def run_production(app, host="0.0.0.0", port=8050, workers=None, **kwargs):
    """Run application in production mode using Waitress"""
    try:
        from waitress import serve
    except ImportError:
        print("❌ Waitress not installed. Installing...")
        os.system("pip install waitress")
        from waitress import serve
    
    print(f"🚀 Starting Yōsai Dashboard in PRODUCTION mode")
    print(f"📍 URL: http://{host}:{port}")
    print(f"👥 Workers: {workers or 'auto'}")
    print("=" * 50)
    
    serve_kwargs = {
        "host": host,
        "port": port,
        "url_scheme": "http",
    }
    
    if workers:
        serve_kwargs["threads"] = workers
    
    serve(app.server, **serve_kwargs)

def main():
    """Main entry point"""
    
    # Parse arguments
    args = parse_arguments()
    
    # Determine mode
    mode = determine_mode(args)
    is_production = mode == "production"
    
    # Validate environment
    validate_environment()
    
    # Create application using the unified factory
    print(f"🏗️ Creating application in {mode.upper()} mode...")
    
    try:
        from app_factory import create_app
        app = create_app(mode)
        
    except Exception as e:
        print(f"❌ Failed to create application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Determine runtime settings
    host = args.host or ("0.0.0.0" if is_production else "127.0.0.1")
    port = args.port
    debug = args.debug or not is_production
    
    # Start the application
    try:
        if is_production and not args.debug:
            run_production(
                app, 
                host=host, 
                port=port, 
                workers=args.workers
            )
        else:
            run_development(
                app, 
                host=host, 
                port=port, 
                debug=debug
            )
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

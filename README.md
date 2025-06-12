# Yōsai Dashboard

This repository contains the code for the Yōsai analytics dashboard.  Two entry points existed before (`app.py` for development and `app_production.py` for production).  A new `run.py` script now consolidates these so the application can be started with a single command.

## Usage

```bash
# Development mode (default)
python run.py

# or
MODE=dev python run.py

# Production mode
python run.py prod

# or
MODE=prod python run.py
```

The script will start the development server when run in `dev` mode.  When `prod` is specified it uses Waitress to serve the app.

See [docs/SETUP.md](docs/SETUP.md) for full installation instructions and troubleshooting tips.

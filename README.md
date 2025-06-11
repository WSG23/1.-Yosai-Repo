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

When starting the app in development you may see the startup logs printed twice.
Dash enables its reloader in debug mode which launches the server in a child
process, causing duplicate output. This is normal behaviour. To disable the
reloader and run with a single startup sequence use production mode (e.g.
`python run.py prod`) or set `FLASK_ENV=production` before running `run.py`.

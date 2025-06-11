# Yōsai Dashboard

This repository contains the code for the Yōsai analytics dashboard.  Two entry points existed before (`app.py` for development and `app_production.py` for production).  A new `run.py` script now consolidates these so the application can be started with a single command.

## Usage

```bash
# Development mode (default)
python run.py

# or explicitly specify the mode
python run.py --mode dev
# or
MODE=dev python run.py

# Production mode
python run.py --mode prod
# or
MODE=prod python run.py
```

The script starts the development server by default. When `prod` is used it launches the Waitress production server.

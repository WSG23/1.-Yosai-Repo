# Yōsai Dashboard

This repository contains the code for the Yōsai analytics dashboard.  Two entry points existed before (`app.py` for development and `app_production.py` for production).  A new `run.py` script now consolidates these so the application can be started with a single command.

## Usage

The dashboard now uses a **single entry point** (`run.py`) that automatically configures the application for different environments:

### Development Mode
```bash
# All of these start development mode
python run.py
python run.py dev
python run.py development
MODE=dev python run.py

# With custom settings
python run.py --host 0.0.0.0 --port 8080 --debug
```

### Production Mode
```bash
# All of these start production mode
python run.py prod  
python run.py production
MODE=prod python run.py

# With custom settings
python run.py prod --host 0.0.0.0 --port 8050 --workers 4
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODE` | Application mode (`dev`/`prod`) | `dev` |
| `HOST` | Host to bind to | `127.0.0.1` (dev), `0.0.0.0` (prod) |
| `PORT` | Port to bind to | `8050` |
| `DEBUG` | Enable debug mode | `true` (dev), `false` (prod) |
| `LOG_LEVEL` | Logging level | `DEBUG` (dev), `INFO` (prod) |
## Testing

A small test suite using `pytest` and `dash[testing]` ensures the application UI works as expected.  Install the additional testing dependencies and run the tests with:

```bash
pip install dash[testing] pytest
pytest
```

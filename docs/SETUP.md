# Setup Guide

This document describes how to configure and run the Yōsai dashboard.

## Prerequisites
- Python 3.11
- `pip` package manager
- Optional: Docker and Docker Compose for containerized runs

## Installation
1. Clone the repository and navigate into it.
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   python run.py
   ```
   For production mode use:
   ```bash
   python run.py prod
   ```

## Docker
Build and run the container using the provided Dockerfile:
```bash
docker build -f assets/Dockerfile -t yosai-dashboard .
docker run -p 8050:8050 yosai-dashboard
```

## Troubleshooting
- **Missing Packages**: Ensure all dependencies are installed by running `pip install -r requirements.txt`.
- **Port Already In Use**: Check that port `8050` is free or adjust the run command to use another port.
- **File Upload Issues**: Verify the file type and size match the limits defined in `config/settings.py`.


# API Overview

The application exposes a small set of REST endpoints alongside the Dash interface.
These endpoints allow integrations to check status and submit files programmatically.

## Endpoints

| Method | Path        | Description                    |
|-------|-------------|--------------------------------|
| GET   | `/health`   | Simple health check returning `OK`. |
| POST  | `/api/upload` | Upload a CSV file for processing. Expects `multipart/form-data` with a `file` field. |

All other interactions occur through the Dash UI.

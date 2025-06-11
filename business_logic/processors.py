"""Pure business logic functions for the orchestrator."""
from __future__ import annotations

from typing import Any, Dict, Tuple
import base64
import io
import json
import pandas as pd


def handle_file_upload(contents: str | None, filename: str | None, column_mapping: dict | None) -> Tuple[dict | None, list | None, None, str]:
    """Process uploaded file and extract door list."""
    if not contents or not filename:
        return None, None, None, "No file uploaded"

    try:
        content_type, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.lower().endswith(".json"):
            df = pd.read_json(io.StringIO(decoded.decode("utf-8")))
        else:
            raise ValueError("Unsupported file type")

        processed_data = {
            "filename": filename,
            "dataframe": df.to_dict("records"),
            "columns": df.columns.tolist(),
        }

        door_col = "DoorID (Device Name)"
        if isinstance(column_mapping, dict):
            mapping = column_mapping.get(json.dumps(sorted(df.columns.tolist())), {})
            for csv_col, internal in mapping.items():
                if internal == "DoorID":
                    door_col = csv_col
        doors = df[door_col].astype(str).unique().tolist() if door_col in df.columns else []
        status = f"Uploaded {filename} - {len(doors)} doors found"
        return processed_data, doors, None, status
    except Exception as exc:  # pragma: no cover - simple demo
        return None, None, None, f"Upload failed: {exc}"  # pragma: no cover


def handle_graph_generation(current_data: dict | None, _n_clicks: int | None) -> Tuple[None, None, None, str]:
    """Simulate graph generation."""
    if not current_data:
        return None, None, None, "No data to generate"
    return None, None, None, "Graph generated successfully"


def handle_mapping_confirmation(_clicks: int | None, mapping: dict | None) -> Tuple[None, None, None, str]:
    """Handle mapping confirmation - stub implementation."""
    if not mapping:
        return None, None, None, "Mapping not provided"
    return None, None, None, "Mapping confirmed"

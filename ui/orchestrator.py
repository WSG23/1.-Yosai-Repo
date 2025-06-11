"""Unified orchestrator and UI callbacks."""
from __future__ import annotations

from typing import Any, Tuple

from dash import Input, Output, State, callback, no_update

from business_logic import processors


@callback(
    [
        Output("processed-data-store", "data"),
        Output("all-doors-from-csv-store", "data"),
        Output("manual-door-classifications-store", "data"),
        Output("status-message-store", "data"),
    ],
    [
        Input("upload-data", "contents"),
        Input("confirm-and-generate-button", "n_clicks"),
        Input("confirm-header-map-button", "n_clicks"),
    ],
    [
        State("upload-data", "filename"),
        State("column-mapping-store", "data"),
        State("processed-data-store", "data"),
    ],
    prevent_initial_call=True,
)
def main_data_orchestrator(
    upload_contents: str | None,
    generate_clicks: int | None,
    mapping_clicks: int | None,
    filename: str | None,
    column_mapping: dict | None,
    current_data: dict | None,
) -> Tuple[Any, Any, Any, str]:
    ctx = callback.context  # type: ignore
    if not ctx.triggered:
        return no_update, no_update, no_update, "Ready"

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "upload-data":
        return processors.handle_file_upload(upload_contents, filename, column_mapping)
    if trigger_id == "confirm-and-generate-button":
        return processors.handle_graph_generation(current_data, generate_clicks)
    if trigger_id == "confirm-header-map-button":
        return processors.handle_mapping_confirmation(mapping_clicks, column_mapping)

    return no_update, no_update, no_update, "No action taken"


@callback(
    Output("onion-graph", "elements"),
    [
        Input("processed-data-store", "data"),
        Input("all-doors-from-csv-store", "data"),
        Input("manual-door-classifications-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_graph_elements(processed_data: dict | None, doors_data: list | None, classifications: dict | None):
    if not doors_data:
        return []
    from app import build_onion_security_model  # late import to avoid cycle

    return build_onion_security_model(doors_data, classifications or {}, processed_data)


@callback(
    Output("graph-output-container", "style"),
    Input("onion-graph", "elements"),
    prevent_initial_call=True,
)
def update_container_visibility(elements: list) -> dict:
    if elements:
        return {"display": "block", "margin": "20px auto", "padding": "20px"}
    return {"display": "none"}


@callback(
    Output("processing-status", "children"),
    Input("status-message-store", "data"),
    prevent_initial_call=True,
)
def update_status_display(status_data: Any) -> Any:
    return status_data or "Ready"

# ui/components/graph_handlers.py
"""Callbacks for graph interactions."""

from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
import json

from ui.components.graph import create_graph_component


class GraphHandlers:
    """Handle layout and filter interactions for the onion graph."""

    def __init__(self, app, graph_component=None):
        self.app = app
        self.graph_component = graph_component or create_graph_component()
        self.layout_options = self.graph_component.get_layout_options()

    def register_callbacks(self):
        """Register all graph related callbacks."""
        self._register_layout_change_callback()
        self._register_filter_callback()
        self._register_generation_callback()

    def _register_layout_change_callback(self):
        @self.app.callback(
            Output("onion-graph", "layout"),
            Input("graph-layout-selector", "value"),
            prevent_initial_call=True,
        )
        def update_layout(selected):
            return self.layout_options.get(selected, self.graph_component.default_layout)

    def _register_filter_callback(self):
        @self.app.callback(
            Output("onion-graph", "elements", allow_duplicate=True),
            Input("graph-filters", "value"),
            State("onion-graph", "elements"),
            prevent_initial_call=True,
        )
        def filter_elements(selected_filters, current_elements):
            if not current_elements:
                raise PreventUpdate

            filters = set(selected_filters or [])
            nodes = [e for e in current_elements if "source" not in e.get("data", {})]
            edges = [e for e in current_elements if "source" in e.get("data", {})]

            def node_visible(node):
                data = node.get("data", {})
                if "entrances_only" in filters and not data.get("is_entrance"):
                    return False
                if "hide_low_security" in filters and data.get("security_level", 10) < 5:
                    return False
                return True

            visible_nodes = {n["data"]["id"] for n in nodes if node_visible(n) and "id" in n.get("data", {})}

            def edge_visible(edge):
                if "critical_paths" in filters and not edge.get("data", {}).get("is_critical"):
                    return False
                src = edge.get("data", {}).get("source")
                tgt = edge.get("data", {}).get("target")
                return src in visible_nodes and tgt in visible_nodes

            filtered_nodes = [n for n in nodes if n.get("data", {}).get("id") in visible_nodes]
            filtered_edges = [e for e in edges if edge_visible(e)]
            return filtered_nodes + filtered_edges

    def _register_generation_callback(self):
        @self.app.callback(
            [
                Output("onion-graph", "elements", allow_duplicate=True),
                Output("graph-output-container", "style", allow_duplicate=True),
                # Send status updates to the shared store
                Output("status-message-store", "data", allow_duplicate=True),
            ],
            Input("confirm-and-generate-button", "n_clicks"),
            [
                State("processed-data-store", "data"),
                State("column-mapping-store", "data"),
                State("manual-door-classifications-store", "data"),
            ],
            prevent_initial_call=True,
        )
        def generate_graph_from_data(n_clicks, processed_data, mappings, classifications):
            if not n_clicks or not processed_data:
                raise PreventUpdate

            try:
                df = pd.DataFrame(processed_data.get("dataframe", []))
                if df.empty:
                    return [], {"display": "block"}, "No data to generate graph"

                door_col = "DoorID (Device Name)"
                ts_col = "Timestamp (Event Time)"
                if isinstance(mappings, dict):
                    header_key = json.dumps(sorted(processed_data.get("columns", [])))
                    mapping = mappings.get(header_key, {})
                    for csv_col, internal in mapping.items():
                        if internal == "DoorID":
                            door_col = csv_col
                        elif internal == "Timestamp":
                            ts_col = csv_col

                if ts_col in df.columns:
                    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
                    df.sort_values(ts_col, inplace=True)

                doors = df[door_col].astype(str).tolist() if door_col in df.columns else []

                nodes = []
                class_dict = classifications or {}
                if isinstance(class_dict, str):
                    class_dict = json.loads(class_dict)

                for door in df[door_col].astype(str).unique() if door_col in df.columns else []:
                    data = {"id": door, "label": door}
                    if door in class_dict:
                        c = class_dict[door]
                        data.update({
                            "floor": c.get("floor"),
                            "security_level": c.get("security_level"),
                        })
                        if c.get("is_ee"):
                            data["is_entrance"] = True
                        if c.get("is_stair"):
                            data["is_stair"] = True
                    nodes.append({"data": data})

                edges = []
                prev = None
                for door in doors:
                    if prev is not None and prev != door:
                        edge_id = f"{prev}->{door}"
                        edges.append({"data": {"id": edge_id, "source": prev, "target": door}})
                    prev = door

                unique_edges = {e["data"]["id"]: e for e in edges}

                elements = nodes + list(unique_edges.values())
                return elements, {"display": "block"}, "Analysis complete"
            except Exception:
                return [], {"display": "block"}, "Failed to generate graph"


# Factory function

def create_graph_handlers(app, graph_component=None):
    """Factory to create GraphHandlers"""
    return GraphHandlers(app, graph_component)

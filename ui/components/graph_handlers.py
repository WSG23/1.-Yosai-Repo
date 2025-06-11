from dash import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
import json


class GraphHandlers:
    """Callback handlers for Cytoscape graph exports."""

    def __init__(self, app):
        self.app = app

    def register_callbacks(self):
        self._register_png_export()
        self._register_json_export()

    def _register_png_export(self):
        @self.app.callback(
            Output("onion-graph", "generateImage"),
            Input("export-graph-png", "n_clicks"),
            prevent_initial_call=True,
        )
        def trigger_png(n_clicks):
            if not n_clicks:
                raise PreventUpdate
            # Trigger client-side generation of a PNG and store it in imageData
            return {"type": "png", "action": "store"}

        @self.app.callback(
            Output("download-graph-png", "data"),
            Input("onion-graph", "imageData"),
            prevent_initial_call=True,
        )
        def download_png(image_data):
            if not image_data:
                raise PreventUpdate
            header, encoded = image_data.split(",", 1)
            return dict(content=base64.b64decode(encoded), filename="graph.png")

    def _register_json_export(self):
        @self.app.callback(
            Output("download-graph-json", "data"),
            Input("export-graph-json", "n_clicks"),
            State("onion-graph", "elements"),
            prevent_initial_call=True,
        )
        def export_json(n_clicks, elements):
            if not n_clicks:
                raise PreventUpdate
            data = json.dumps(elements or [], indent=2)
            return dict(content=data, filename="graph.json")


def create_graph_handlers(app):
    """Factory function to create graph handlers."""
    return GraphHandlers(app)

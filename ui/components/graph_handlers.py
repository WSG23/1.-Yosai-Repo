# ui/components/graph_handlers.py
"""Callbacks for graph interactions."""

from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate

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


# Factory function

def create_graph_handlers(app, graph_component=None):
    """Factory to create GraphHandlers"""
    return GraphHandlers(app, graph_component)

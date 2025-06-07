# styles/graph_styles.py
"""
Graph styling configuration for Cytoscape components
"""

from ui.themes.style_config import COLORS, SPACING, BORDER_RADIUS, SHADOWS, TYPOGRAPHY

# Cytoscape graph styles
GRAPH_STYLES = [
    # Node styles
    {
        'selector': 'node',
        'style': {
            'background-color': COLORS['surface'],
            'border-color': COLORS['border'],
            'border-width': 2,
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-family': 'Inter, sans-serif',
            'color': COLORS['text_primary'],  # Changed from 'text_light'
            'width': 60,
            'height': 60,
            'font-weight': 500
        }
    },
    
    # Core/Central nodes
    {
        'selector': 'node[type = "core"]',
        'style': {
            'background-color': COLORS['accent'],
            'border-color': COLORS['accent'],
            'color': 'white',
            'width': 80,
            'height': 80,
            'font-size': '14px',
            'font-weight': 600
        }
    },
    
    # Entrance nodes
    {
        'selector': 'node[type = "entrance"]',
        'style': {
            'background-color': COLORS['success'],
            'border-color': COLORS['success'],
            'color': 'white',
            'shape': 'rectangle',
            'width': 70,
            'height': 50
        }
    },
    
    # Security layer nodes
    {
        'selector': 'node[type = "security"]',
        'style': {
            'background-color': COLORS['warning'],
            'border-color': COLORS['warning'],
            'color': 'white',
            'shape': 'diamond',
            'width': 65,
            'height': 65
        }
    },
    
    # Critical asset nodes
    {
        'selector': 'node[type = "critical"]',
        'style': {
            'background-color': COLORS['critical'],
            'border-color': COLORS['critical'],
            'color': 'white',
            'shape': 'octagon',
            'width': 75,
            'height': 75,
            'font-weight': 700
        }
    },
    
    # Edge styles
    {
        'selector': 'edge',
        'style': {
            'line-color': COLORS['border'],
            'target-arrow-color': COLORS['border'],
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'width': 2,
            'arrow-scale': 1.2
        }
    },
    
    # Access path edges
    {
        'selector': 'edge[type = "access"]',
        'style': {
            'line-color': COLORS['success'],
            'target-arrow-color': COLORS['success'],
            'width': 3
        }
    },
    
    # Security boundary edges
    {
        'selector': 'edge[type = "security"]',
        'style': {
            'line-color': COLORS['warning'],
            'target-arrow-color': COLORS['warning'],
            'line-style': 'dashed',
            'width': 2
        }
    },
    
    # Critical path edges
    {
        'selector': 'edge[type = "critical"]',
        'style': {
            'line-color': COLORS['critical'],
            'target-arrow-color': COLORS['critical'],
            'width': 4,
            'line-style': 'solid'
        }
    },
    
    # Hover states
    {
        'selector': 'node:active',  # Changed from node:hover which is invalid
        'style': {
            'border-width': 4,
            'border-color': COLORS['accent'],
            'z-index': 999
        }
    },
    
    {
        'selector': 'edge:active',  # Changed from edge:hover which is invalid  
        'style': {
            'width': 4,
            'line-color': COLORS['accent'],
            'target-arrow-color': COLORS['accent'],
            'z-index': 999
        }
    },
    
    # Selected states
    {
        'selector': 'node:selected',
        'style': {
            'border-width': 5,
            'border-color': COLORS['accent'],
            'box-shadow': '0 0 20px rgba(33, 150, 243, 0.4)',  # Fixed: use rgba instead of hex+alpha
            'z-index': 1000
        }
    },
    
    {
        'selector': 'edge:selected',
        'style': {
            'width': 5,
            'line-color': COLORS['accent'],
            'target-arrow-color': COLORS['accent'],
            'z-index': 1000
        }
    }
]

# Graph container styles
GRAPH_CONTAINER_STYLE = {
    'width': '100%',
    'height': '600px',
    'background-color': COLORS['background'],
    'border-radius': BORDER_RADIUS['lg'],
    'border': f"1px solid {COLORS['border']}",
    'box-shadow': SHADOWS['md'],
    'position': 'relative',
    'overflow': 'hidden'
}

# Graph layout configurations
LAYOUT_OPTIONS = {
    'concentric': {
        'name': 'concentric',
        'concentric': lambda node: node.data('importance', 1),
        'levelWidth': lambda nodes: 2,
        'minNodeSpacing': 100,
        'spacingFactor': 1.5,
        'animate': True,
        'animationDuration': 1000
    },
    
    'cose': {
        'name': 'cose',
        'idealEdgeLength': 150,
        'nodeOverlap': 20,
        'refresh': 20,
        'fit': True,
        'padding': 50,
        'randomize': False,
        'componentSpacing': 100,
        'nodeRepulsion': 400000,
        'edgeElasticity': 100,
        'nestingFactor': 5,
        'gravity': 80,
        'numIter': 1000,
        'initialTemp': 200,
        'coolingFactor': 0.95,
        'minTemp': 1.0,
        'animate': True,
        'animationDuration': 1000
    },
    
    'circle': {
        'name': 'circle',
        'radius': 200,
        'spacingFactor': 1.5,
        'animate': True,
        'animationDuration': 1000
    },
    
    'grid': {
        'name': 'grid',
        'rows': 3,
        'cols': 3,
        'spacingFactor': 1.5,
        'animate': True,
        'animationDuration': 1000
    }
}

# Legend styles
LEGEND_STYLE = {
    'position': 'absolute',
    'top': '10px',
    'right': '10px',
    'background': COLORS['surface'],
    'border': f"1px solid {COLORS['border']}",
    'border-radius': BORDER_RADIUS['md'],
    'padding': SPACING['base'],
    'font-size': TYPOGRAPHY['text_sm'],
    'color': COLORS['text_secondary'],
    'max-width': '200px',
    'z-index': 1000,
    'box-shadow': SHADOWS['sm']
}

# Centered graph box style
centered_graph_box_style = {
    'width': '100%',
    'height': '600px',
    'display': 'flex',
    'justify-content': 'center',
    'align-items': 'center',
    'background-color': COLORS['surface'],
    'border-radius': BORDER_RADIUS['lg'],
    'border': f"1px solid {COLORS['border']}",
    'box-shadow': SHADOWS['md'],
    'position': 'relative',
    'overflow': 'hidden',
    'margin': f"{SPACING['lg']} auto"
}

# Cytoscape inside box style
cytoscape_inside_box_style = {
    'width': '100%',
    'height': '100%',
    'background-color': COLORS['background'],
    'border-radius': BORDER_RADIUS['md']
}

# Tap node data centered style
tap_node_data_centered_style = {
    'border': f"1px solid {COLORS['border']}",
    'padding': SPACING['base'],
    'margin': f"{SPACING['base']} auto",
    'background-color': COLORS['surface'],
    'color': COLORS['text_secondary'],
    'font-size': TYPOGRAPHY['text_sm'],
    'border-radius': BORDER_RADIUS['md'],
    'text-align': 'center',
    'white-space': 'pre-wrap',
    'overflow-wrap': 'break-word',
    'max-width': '800px'
}

# Actual default stylesheet for graph (same as GRAPH_STYLES)
actual_default_stylesheet_for_graph = GRAPH_STYLES

# Select component overrides
select_control_style = {
    'background-color': COLORS['surface'],
    'border-color': COLORS['border'],
    'color': COLORS['text_primary'],
    'transition': f'all {SPACING["base"]}'
}

select_control_hover_style = {
    'border-color': COLORS['accent']
}

select_menu_style = {
    'background-color': COLORS['surface'],
    'border': f"1px solid {COLORS['border']}",
    'border-radius': BORDER_RADIUS['md'],
    'box-shadow': SHADOWS['lg'],
    'color': COLORS['text_primary']
}

select_option_style = {
    'background': 'transparent',
    'color': COLORS['text_primary'],
    'transition': f'all {SPACING["base"]}'
}

select_option_hover_style = {
    'background-color': COLORS['accent'],
    'color': 'white'
}

# Standard dropdown overrides
dropdown_style = {
    'background-color': COLORS['surface'],
    'border-color': COLORS['border'],
    'color': COLORS['text_primary']
}

dropdown_menu_style = {
    'background-color': COLORS['surface'],
    'border-color': COLORS['border'],
    'border-radius': BORDER_RADIUS['md'],
    'box-shadow': SHADOWS['lg']
}

dropdown_item_style = {
    'color': COLORS['text_primary'],
    'background-color': 'transparent'
}

dropdown_item_hover_style = {
    'background-color': COLORS['accent'],
    'color': 'white'
}

# Upload icon image style
upload_icon_img_style = {
    'width': '96px',  # Increased from 64px
    'height': '96px',  # Increased from 64px
    'opacity': '0.7',
    'transition': f'all {SPACING["base"]}',
    'filter': 'brightness(0.8)',
    'margin': 'auto'
}

# Graph loading styles
graph_loading_style = {
    'display': 'flex',
    'flex-direction': 'column',
    'align-items': 'center',
    'justify-content': 'center',
    'height': '100%',
    'color': COLORS['text_secondary'],
    'font-size': TYPOGRAPHY['text_lg']
}

# Export all styles
__all__ = [
    'GRAPH_STYLES',
    'GRAPH_CONTAINER_STYLE', 
    'LAYOUT_OPTIONS',
    'LEGEND_STYLE',
    'centered_graph_box_style',
    'cytoscape_inside_box_style',
    'tap_node_data_centered_style',
    'actual_default_stylesheet_for_graph',
    'upload_icon_img_style',
    'graph_loading_style',
    'select_control_style',
    'select_control_hover_style',
    'select_menu_style',
    'select_option_style', 
    'select_option_hover_style',
    'dropdown_style',
    'dropdown_menu_style',
    'dropdown_item_style',
    'dropdown_item_hover_style'
]
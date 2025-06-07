# styles/style_config.py (FIXED - Moved enhanced definitions after base definitions)
"""
Comprehensive style configuration with consistent background colors
"""

# Color palette - UPDATED for consistency
COLORS = {
    # Primary colors
    'primary': '#1B2A47',
    'accent': '#2196F3',
    'accent_light': '#42A5F5',
    
    # Status colors
    'success': '#2DBE6C',
    'warning': '#FFB020',
    'critical': '#E02020',
    'info': '#2196F3',
    
    # Background colors - UPDATED for consistency
    'background': '#0F1419',        # Main background - dark blue-gray
    'surface': '#1A2332',           # Card/component surfaces - slightly lighter
    'surface_elevated': '#1E2936',  # Elevated surfaces (modals, dropdowns)
    'border': '#2D3748',            # Border color
    
    # Text colors
    'text_primary': '#F7FAFC',      # Primary text - white
    'text_secondary': '#E2E8F0',    # Secondary text - light gray
    'text_tertiary': '#A0AEC0',     # Tertiary text - medium gray
    'text_on_accent': '#FFFFFF',    # Text on accent backgrounds
}

# Animation durations
ANIMATIONS = {
    'fast': '0.15s',
    'normal': '0.3s',
    'slow': '0.5s'
}

# Typography (BASE DEFINITION - moved up)
TYPOGRAPHY = {
    # Font sizes
    'text_xs': '0.75rem',
    'text_sm': '0.875rem',
    'text_base': '1rem',
    'text_lg': '1.125rem',
    'text_xl': '1.25rem',
    'text_2xl': '1.5rem',
    'text_3xl': '1.875rem',
    'text_4xl': '2.25rem',
    
    # Font weights
    'font_light': '300',
    'font_normal': '400',
    'font_medium': '500',
    'font_semibold': '600',
    'font_bold': '700',
    
    # Line heights
    'leading_tight': '1.25',
    'leading_normal': '1.5',
    'leading_relaxed': '1.75',
}

# Spacing (BASE DEFINITION - moved up)
SPACING = {
    'xs': '0.25rem',
    'sm': '0.5rem',
    'base': '1rem',
    'md': '1.25rem',  # New: 20px spacing step
    'lg': '1.5rem',
    'xl': '2rem',
    '2xl': '3rem',
    '3xl': '4rem'
}

# Border radius
BORDER_RADIUS = {
    'sm': '0.125rem',
    'md': '0.375rem',
    'lg': '0.5rem',
    'xl': '0.75rem',
    '2xl': '1rem',
    'full': '9999px'
}

# Shadows (BASE DEFINITION - moved up)
SHADOWS = {
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    'outline': '0 0 0 3px rgba(33, 150, 243, 0.5)'  # Focus outline
}

# Enhanced Typography - Building on existing
ENHANCED_TYPOGRAPHY = {
    **TYPOGRAPHY,
    'text_hero': '3.5rem',      # Hero text
    'text_display': '2.75rem',  # Display headers
    'text_subtitle': '1.375rem', # Subtitles
    'text_caption': '0.8125rem', # Captions
    
    # Enhanced line heights for better readability
    'leading_hero': '1.1',
    'leading_display': '1.2',
    'leading_body': '1.6',
    
    # Letter spacing for emphasis
    'tracking_wide': '0.025em',
    'tracking_wider': '0.05em',
    'tracking_widest': '0.1em',
}

# Enhanced Spacing System - Building on existing
ENHANCED_SPACING = {
    **SPACING,
    # Micro spacing for fine control
    'xxs': '0.125rem',   # 2px
    'micro': '0.1875rem', # 3px
    # Larger spacing for sections
    '4xl': '5rem',       # 80px
    '5xl': '6rem',       # 96px
    '6xl': '8rem',       # 128px
}

# Enhanced Shadows with more depth options
ENHANCED_SHADOWS = {
    **SHADOWS,
    # Additional shadow layers for depth
    'xs': '0 1px 1px 0 rgba(0, 0, 0, 0.05)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    '3xl': '0 35px 60px -12px rgba(0, 0, 0, 0.35)',
    
    # Colored shadows for accent elements
    'accent': '0 10px 25px -5px rgba(33, 150, 243, 0.25)',
    'success': '0 10px 25px -5px rgba(45, 190, 108, 0.25)',
    'warning': '0 10px 25px -5px rgba(255, 176, 32, 0.25)',
    'critical': '0 10px 25px -5px rgba(224, 32, 32, 0.25)',
}

# Component styles - UPDATED with new color scheme
COMPONENT_STYLES = {
    'card': {
        'background-color': COLORS['surface'],
        'border': f"1px solid {COLORS['border']}",
        'border-radius': BORDER_RADIUS['xl'],
        'box-shadow': SHADOWS['lg'],
        'padding': SPACING['xl']
    },
    'card_elevated': {
        'background-color': COLORS['surface_elevated'],
        'border': f"1px solid {COLORS['border']}",
        'border-radius': BORDER_RADIUS['xl'],
        'box-shadow': SHADOWS['xl'],
        'padding': SPACING['xl']
    },
    'button_primary': {
        'background-color': COLORS['accent'],
        'color': COLORS['text_on_accent'],
        'border': 'none',
        'padding': f"{SPACING['sm']} {SPACING['lg']}",
        'border-radius': BORDER_RADIUS['lg'],
        'font-weight': TYPOGRAPHY['font_semibold'],
        'cursor': 'pointer',
        'transition': f'all {ANIMATIONS["fast"]}',
        'box-shadow': SHADOWS['md']
    },
    'button_secondary': {
        'background-color': 'transparent',
        'color': COLORS['text_secondary'],
        'border': f"1px solid {COLORS['border']}",
        'padding': f"{SPACING['sm']} {SPACING['lg']}",
        'border-radius': BORDER_RADIUS['lg'],
        'font-weight': TYPOGRAPHY['font_medium'],
        'cursor': 'pointer',
        'transition': f'all {ANIMATIONS["fast"]}'
    },
    'button_success': {
        'background-color': COLORS['success'],
        'color': COLORS['text_on_accent'],
        'border': 'none',
        'padding': f"{SPACING['sm']} {SPACING['lg']}",
        'border-radius': BORDER_RADIUS['lg'],
        'font-weight': TYPOGRAPHY['font_semibold'],
        'cursor': 'pointer',
        'transition': f'all {ANIMATIONS["fast"]}',
        'box-shadow': SHADOWS['md']
    },
    'input': {
        'background-color': COLORS['surface'],
        'border': f"1px solid {COLORS['border']}",
        'border-radius': BORDER_RADIUS['md'],
        'padding': SPACING['sm'],
        'color': COLORS['text_primary'],
        'font-size': TYPOGRAPHY['text_base'],
        'transition': f'border-color {ANIMATIONS["fast"]}'
    }
}

# UI visibility settings - UPDATED with consistent background
UI_VISIBILITY = {
    # Boolean visibility flags
    'show_upload_section': True,
    'show_mapping_section': True,
    'show_classification_section': True,
    'show_graph_section': True,
    'show_stats_section': True,
    'show_controls_section': True,
    'show_debug_info': False,
    'show_advanced_options': False,
    
    # CSS Style objects for components
    'hide': {'display': 'none'},
    'show_block': {
        'display': 'block',
        'animation': f'fadeIn {ANIMATIONS["normal"]}',
    },
    'show_flex': {
        'display': 'flex',
        'animation': f'slideUp {ANIMATIONS["normal"]}',
    },
    'show_flex_stats': {
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-around',
        'gap': SPACING['lg'],
        'marginBottom': SPACING['2xl'],
        'animation': f'fadeIn {ANIMATIONS["normal"]}',
    },
    'show_header': {
        'display': 'flex',
        'flexDirection': 'row',
        'alignItems': 'center',
        'padding': f"{SPACING['lg']} {SPACING['xl']}",
        'backgroundColor': COLORS['background'],  # UPDATED to match main background
        'borderBottom': f'1px solid {COLORS["border"]}',
        'boxShadow': SHADOWS["sm"],
        'marginBottom': SPACING['xl'],
        'backdropFilter': 'blur(10px)',
    }
}

# UI components configuration
UI_COMPONENTS = {
    'upload': {
        'enabled': True,
        'accept_types': ['.csv'],
        'max_file_size': '10MB',
        'multiple_files': False,
        'icon_size': '120px',  # NEW: Larger icon size
        'container_width': '70%',  # NEW: Wider container
        'border_thickness': '3px'  # NEW: Thicker border
    },
    'mapping': {
        'enabled': True,
        'required_fields': ['timestamp', 'user_id', 'door_id', 'event_type'],
        'optional_fields': ['floor', 'building', 'access_level']
    },
    'classification': {
        'enabled': True,
        'card_style': {
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['md'],
            'border': f"1px solid {COLORS['border']}",
            'boxShadow': SHADOWS['sm'],
            'transition': 'all 0.2s ease'
        },
        'pill_style': {
            'backgroundColor': COLORS['surface'],
            'color': COLORS['text_secondary'],
            'borderRadius': BORDER_RADIUS['full'],
            'border': f"1px solid {COLORS['border']}",
            'cursor': 'pointer',
            'transition': 'all 0.2s ease'
        },
        'pill_style_active': {
            'backgroundColor': COLORS['accent'],
            'color': 'white',
            'borderColor': COLORS['accent']
        },
        'auto_classify': True,
        'security_levels': ['Public', 'Restricted', 'Highly Restricted'],
        'default_level': 'Public'
    },
    'graph': {
        'enabled': True,
        'default_layout': 'cose',
        'show_legend': True,
        'interactive': True,
        'export_formats': ['png', 'json']
    },
    'stats': {
        'enabled': True,
        'show_summaries': True,
        'show_charts': True,
        'refresh_interval': 5000
    }
}

# Layout configuration
LAYOUT_CONFIG = {
    'container_padding': '0',  # UPDATED: No padding for full-width background
    'section_spacing': SPACING['xl'],
    'max_width': '1200px',
    'responsive_breakpoints': {
        'mobile': '768px',
        'tablet': '1024px',
        'desktop': '1200px'
    }
}

# Centralized style definitions for UI components
UPLOAD_STYLES = {
    'icon': {
        'width': '120px',
        'height': '120px',
        'marginBottom': SPACING['base'],
        'opacity': '0.8',
        'transition': f'all {ANIMATIONS["normal"]}'
    },
    'content': {
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'height': '100%',
        'padding': SPACING['base']
    },
    'base': {
        'width': UI_COMPONENTS['upload']['container_width'],
        'maxWidth': '600px',
        'minHeight': '180px',
        'borderRadius': BORDER_RADIUS['lg'],
        'textAlign': 'center',
        'margin': f"{SPACING['base']} auto",
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease'
    },
    'states': {
        'initial': {
            'border': f'2px dashed {COLORS["border"]}',
            'backgroundColor': COLORS['surface']
        },
        'success': {
            'border': f'2px solid {COLORS["success"]}',
            'backgroundColor': f"{COLORS['success']}10"
        },
        'error': {
            'border': f'2px solid {COLORS["critical"]}',
            'backgroundColor': f"{COLORS['critical']}10"
        }
    },
    'interactive_container': {
        'padding': SPACING['lg'],
        'backgroundColor': COLORS['surface'],
        'borderRadius': BORDER_RADIUS['lg'],
        'margin': f"{SPACING['lg']} auto",
        'width': '85%',
        'maxWidth': '1000px',
        'border': f"1px solid {COLORS['border']}"
    },
    'generate_button': {
        'marginTop': SPACING['lg']
    }
}

MAPPING_STYLES = {
    'section': {
        'display': 'block',
        'width': '70%',
        'maxWidth': '600px',
        'margin': '0 auto',
        'padding': '1.2rem',
        'backgroundColor': COLORS['surface'],
        'borderRadius': BORDER_RADIUS['md'],
        'boxShadow': SHADOWS['sm'],
        'border': f"1px solid {COLORS['border']}"
    },
    'confirm_button': {
        'marginTop': '15px',
        'padding': '8px 16px',
        'border': 'none',
        'borderRadius': BORDER_RADIUS['sm'],
        'backgroundColor': COLORS['accent'],
        'color': 'white',
        'fontSize': '0.9rem',
        'fontWeight': 'bold',
        'cursor': 'pointer',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'display': 'block',
        'transition': 'background-color 0.3s ease'
    },
    'dropdown': {
        'width': '100%',
        'marginBottom': '4px',
        'backgroundColor': COLORS['background'],
        'color': COLORS['text_primary'],
        'borderColor': COLORS['border'],
        'fontSize': '0.9rem'
    },
    'label': {
        'marginBottom': '4px',
        'fontWeight': 'bold',
        'color': COLORS['text_primary'],
        'display': 'block',
        'fontSize': '0.9rem'
    }
}

CLASSIFICATION_STYLES = {
    'setup_card': {
        'padding': '20px',
        'backgroundColor': COLORS['surface'],
        'borderRadius': BORDER_RADIUS['lg'],
        'marginBottom': '20px',
        'border': f"1px solid {COLORS['border']}",
        'maxWidth': '550px',
        'margin': '0 auto 20px auto'
    },
    'classification_card': {
        'padding': '20px',
        'backgroundColor': COLORS['surface'],
        'borderRadius': BORDER_RADIUS['lg'],
        'border': f"1px solid {COLORS['border']}",
        'maxWidth': '900px',
        'margin': '0 auto'
    }
}

# Enhanced Component Styles - Building on existing card styles
ENHANCED_COMPONENT_STYLES = {
    **COMPONENT_STYLES,
    
    # Enhanced Card Variants
    'card_premium': {
        'background-color': COLORS['surface_elevated'],
        'border': f"1px solid {COLORS['border']}",
        'border-radius': BORDER_RADIUS['2xl'],
        'box-shadow': ENHANCED_SHADOWS['2xl'],
        'padding': ENHANCED_SPACING['2xl'],
        'backdrop-filter': 'blur(20px)',
        'transition': f'all {ANIMATIONS["normal"]}',
    },
    
    'card_interactive': {
        'background-color': COLORS['surface'],
        'border': f"1px solid {COLORS['border']}",
        'border-radius': BORDER_RADIUS['xl'],
        'box-shadow': SHADOWS['lg'],
        'padding': SPACING['xl'],
        'transition': f'all {ANIMATIONS["normal"]}',
        'cursor': 'pointer',
    },
    
    'card_floating': {
        'background-color': COLORS['surface_elevated'],
        'border': 'none',
        'border-radius': BORDER_RADIUS['2xl'],
        'box-shadow': ENHANCED_SHADOWS['xl'],
        'padding': ENHANCED_SPACING['2xl'],
        'transform': 'translateZ(0)',
        'transition': f'all {ANIMATIONS["normal"]}',
    },
    
    # Enhanced Button Variants
    'button_premium': {
        'background': f'linear-gradient(135deg, {COLORS["accent"]}, {COLORS["accent_light"]})',
        'color': COLORS['text_on_accent'],
        'border': 'none',
        'padding': f"{ENHANCED_SPACING['md']} {ENHANCED_SPACING['2xl']}",
        'border-radius': BORDER_RADIUS['xl'],
        'font-weight': TYPOGRAPHY['font_semibold'],
        'font-size': TYPOGRAPHY['text_lg'],
        'cursor': 'pointer',
        'transition': f'all {ANIMATIONS["normal"]}',
        'box-shadow': ENHANCED_SHADOWS['accent'],
        'letter-spacing': ENHANCED_TYPOGRAPHY['tracking_wide'],
    },
    
    'button_ghost': {
        'background-color': 'transparent',
        'color': COLORS['text_secondary'],
        'border': f"1px solid transparent",
        'padding': f"{SPACING['sm']} {SPACING['lg']}",
        'border-radius': BORDER_RADIUS['lg'],
        'font-weight': TYPOGRAPHY['font_medium'],
        'cursor': 'pointer',
        'transition': f'all {ANIMATIONS["fast"]}',
    },
}

# Enhanced style generator functions
def get_upload_style(state="initial"):
    """Return upload container style for a given state."""
    return {**UPLOAD_STYLES['base'], **UPLOAD_STYLES['states'].get(state, {})}


def get_interactive_setup_style(visible=False):
    """Style for the interactive setup container."""
    style = UPLOAD_STYLES['interactive_container'].copy()
    style['display'] = 'block' if visible else 'none'
    return style


def get_validation_message_style(status="info"):
    """Return mapping validation message style."""
    color_map = {
        'info': COLORS['text_secondary'],
        'warning': COLORS['warning'],
        'error': COLORS['critical'],
        'success': COLORS['success']
    }
    return {
        'marginTop': '8px',
        'padding': '8px',
        'borderRadius': '4px',
        'backgroundColor': f"{color_map[status]}20",
        'border': f"1px solid {color_map[status]}",
        'color': color_map[status],
        'fontSize': '0.85rem',
        'textAlign': 'center'
    }

def get_enhanced_card_style(variant='default', interactive=False, loading=False):
    """Enhanced card style generator"""
    base_styles = {
        'default': COMPONENT_STYLES['card'],
        'elevated': COMPONENT_STYLES['card_elevated'], 
        'premium': ENHANCED_COMPONENT_STYLES['card_premium'],
        'floating': ENHANCED_COMPONENT_STYLES['card_floating'],
        'interactive': ENHANCED_COMPONENT_STYLES['card_interactive'],
    }
    
    style = base_styles.get(variant, base_styles['default']).copy()
    
    if interactive:
        style.update({
            'cursor': 'pointer',
            'transition': f'all {ANIMATIONS["normal"]}',
        })
    
    if loading:
        style.update({
            'position': 'relative',
            'overflow': 'hidden',
        })
    
    return style

def get_enhanced_button_style(variant='primary', size='default', loading=False):
    """Enhanced button style generator"""
    base_styles = {
        'primary': COMPONENT_STYLES['button_primary'],
        'secondary': COMPONENT_STYLES['button_secondary'],
        'success': COMPONENT_STYLES['button_success'],
        'premium': ENHANCED_COMPONENT_STYLES['button_premium'],
        'ghost': ENHANCED_COMPONENT_STYLES['button_ghost'],
    }
    
    size_styles = {
        'small': {
            'padding': f"{SPACING['xs']} {SPACING['sm']}",
            'font-size': TYPOGRAPHY['text_sm'],
        },
        'default': {},
        'large': {
            'padding': f"{ENHANCED_SPACING['md']} {ENHANCED_SPACING['2xl']}",
            'font-size': TYPOGRAPHY['text_lg'],
        }
    }
    
    style = base_styles.get(variant, base_styles['primary']).copy()
    style.update(size_styles.get(size, {}))
    
    if loading:
        style.update({
            'position': 'relative',
            'pointer-events': 'none',
        })
    
    return style

def get_loading_skeleton_style(width='100%', height='20px'):
    """Generate skeleton loading style"""
    return {
        'background': f'linear-gradient(90deg, {COLORS["surface"]} 25%, {COLORS["border"]} 50%, {COLORS["surface"]} 75%)',
        'background-size': '200% 100%',
        'animation': 'shimmer 1.5s infinite',
        'border-radius': BORDER_RADIUS['md'],
        'width': width,
        'height': height,
    }

# CSS Animations (can be added to CSS file)
CSS_ANIMATIONS = """
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.hover-lift {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.loading-shimmer {
    background: linear-gradient(90deg, 
        transparent, 
        rgba(33, 150, 243, 0.4), 
        transparent
    );
    animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
"""

# Utility Functions
def get_hover_style(base_style, hover_color=None):
    """Generate hover styles for interactive elements"""
    hover_style = base_style.copy()
    if hover_color:
        hover_style["backgroundColor"] = hover_color
    else:
        hover_style["opacity"] = "0.8"
    hover_style["transform"] = "translateY(-1px)"
    return hover_style

def get_focus_style(base_style):
    """Generate focus styles for form elements"""
    focus_style = base_style.copy()
    focus_style["borderColor"] = COLORS["accent"]
    focus_style["boxShadow"] = SHADOWS["outline"]
    return focus_style

def get_disabled_style(base_style):
    """Generate disabled styles for elements"""
    disabled_style = base_style.copy()
    disabled_style["opacity"] = "0.5"
    disabled_style["cursor"] = "not-allowed"
    disabled_style["pointerEvents"] = "none"
    return disabled_style

# Export all public variables and functions
__all__ = [
    # Base style constants
    'COLORS',
    'ANIMATIONS', 
    'TYPOGRAPHY',
    'SPACING',
    'BORDER_RADIUS',
    'SHADOWS',
    'COMPONENT_STYLES',
    'UPLOAD_STYLES',
    'MAPPING_STYLES',
    'CLASSIFICATION_STYLES',
    'UI_VISIBILITY',
    'UI_COMPONENTS',
    'LAYOUT_CONFIG',
    'CSS_ANIMATIONS',
    
    # Enhanced style constants
    'ENHANCED_TYPOGRAPHY',
    'ENHANCED_SPACING', 
    'ENHANCED_SHADOWS',
    'ENHANCED_COMPONENT_STYLES',
    
    # Style generator functions
    'get_enhanced_card_style',
    'get_enhanced_button_style',
    'get_loading_skeleton_style',
    'get_upload_style',
    'get_interactive_setup_style',
    'get_validation_message_style',
    'get_hover_style',
    'get_focus_style',
    'get_disabled_style'
]

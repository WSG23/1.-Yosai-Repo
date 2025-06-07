# ui/components/common.py
"""
Common UI components for enhanced UX
Loading states, notifications, modals, etc.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from ui.themes.style_config import COLORS, ANIMATIONS, TYPOGRAPHY, SPACING, BORDER_RADIUS, SHADOWS


class LoadingComponent:
    """Loading states and progress indicators"""
    
    @staticmethod
    def create_spinner(size="md", color=None):
        """Creates a loading spinner"""
        sizes = {"sm": "1rem", "md": "2rem", "lg": "3rem"}
        
        return html.Div([
            html.Div(style={
                'width': sizes.get(size, "2rem"),
                'height': sizes.get(size, "2rem"),
                'border': f'2px solid {COLORS["border"]}',
                'borderTop': f'2px solid {color or COLORS["accent"]}',
                'borderRadius': '50%',
                'animation': f'spin {ANIMATIONS["normal"]} linear infinite'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'padding': SPACING['lg']
        })
    
    @staticmethod
    def create_skeleton_card():
        """Creates a skeleton loading card"""
        return html.Div([
            html.Div(style={
                'height': '1rem',
                'backgroundColor': COLORS['border'],
                'borderRadius': BORDER_RADIUS['md'],
                'marginBottom': SPACING['base'],
                'animation': f'pulse {ANIMATIONS["slow"]} infinite'
            }),
            html.Div(style={
                'height': '0.75rem',
                'backgroundColor': COLORS['border'],
                'borderRadius': BORDER_RADIUS['md'],
                'marginBottom': SPACING['base'],
                'width': '80%',
                'animation': f'pulse {ANIMATIONS["slow"]} infinite'
            }),
            html.Div(style={
                'height': '0.75rem',
                'backgroundColor': COLORS['border'],
                'borderRadius': BORDER_RADIUS['md'],
                'width': '60%',
                'animation': f'pulse {ANIMATIONS["slow"]} infinite'
            })
        ], style={
            'padding': SPACING['lg'],
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['lg'],
            'border': f"1px solid {COLORS['border']}"
        })
    
    @staticmethod
    def create_progress_bar(progress=0, show_percentage=True, label=None):
        """Creates an enhanced progress bar"""
        return html.Div([
            # Label
            label and html.Div([
                html.Span(label, style={
                    'fontSize': TYPOGRAPHY['text_sm'],
                    'fontWeight': TYPOGRAPHY['font_medium'],
                    'color': COLORS['text_secondary']
                }),
                show_percentage and html.Span(f"{progress}%", style={
                    'fontSize': TYPOGRAPHY['text_sm'],
                    'fontWeight': TYPOGRAPHY['font_semibold'],
                    'color': COLORS['accent']
                })
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'marginBottom': SPACING['xs']
            }),
            
            # Progress bar
            html.Div([
                html.Div(style={
                    'width': f'{max(0, min(100, progress))}%',
                    'height': '100%',
                    'backgroundColor': COLORS['accent'],
                    'borderRadius': BORDER_RADIUS['full'],
                    'transition': f'width {ANIMATIONS["normal"]}',
                    'background': f'linear-gradient(90deg, {COLORS["accent"]}, {COLORS["accent_light"]})',
                    'position': 'relative',
                    'overflow': 'hidden'
                })
            ], style={
                'width': '100%',
                'height': '8px',
                'backgroundColor': COLORS['border'],
                'borderRadius': BORDER_RADIUS['full'],
                'overflow': 'hidden'
            })
        ])
    
    @staticmethod
    def create_loading_overlay(message="Loading...", show=True):
        """Creates a full-screen loading overlay"""
        return html.Div([
            html.Div([
                LoadingComponent.create_spinner("lg"),
                html.P(message, style={
                    'marginTop': SPACING['lg'],
                    'fontSize': TYPOGRAPHY['text_lg'],
                    'color': COLORS['text_primary'],
                    'textAlign': 'center',
                    'margin': '0'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'center',
                'padding': SPACING['2xl'],
                'backgroundColor': COLORS['surface'],
                'borderRadius': BORDER_RADIUS['xl'],
                'boxShadow': SHADOWS['xl'],
                'border': f"1px solid {COLORS['border']}"
            })
        ], style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'backgroundColor': 'rgba(15, 20, 25, 0.8)',
            'backdropFilter': 'blur(4px)',
            'display': 'flex' if show else 'none',
            'alignItems': 'center',
            'justifyContent': 'center',
            'zIndex': '9999',
            'animation': f'fadeIn {ANIMATIONS["fast"]}'
        }, id='loading-overlay')


class NotificationComponent:
    """Toast notifications and alerts"""
    
    @staticmethod
    def create_toast(message, type="info", duration=5000, show=True):
        """Creates a toast notification"""
        type_config = {
            "success": {"icon": "✅", "color": COLORS['success']},
            "error": {"icon": "❌", "color": COLORS['critical']},
            "warning": {"icon": "⚠️", "color": COLORS['warning']},
            "info": {"icon": "ℹ️", "color": COLORS['accent']}
        }
        
        config = type_config.get(type, type_config["info"])
        
        return html.Div([
            html.Div([
                html.Span(config["icon"], style={'marginRight': SPACING['base'], 'fontSize': TYPOGRAPHY['text_lg']}),
                html.Span(message, style={'flex': '1', 'fontSize': TYPOGRAPHY['text_base']}),
                html.Button("×", style={
                    'background': 'none',
                    'border': 'none',
                    'color': COLORS['text_secondary'],
                    'fontSize': TYPOGRAPHY['text_xl'],
                    'cursor': 'pointer',
                    'padding': '0',
                    'marginLeft': SPACING['base']
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': SPACING['lg'],
                'backgroundColor': f"{config['color']}15",
                'border': f"1px solid {config['color']}40",
                'borderLeft': f"4px solid {config['color']}",
                'borderRadius': BORDER_RADIUS['md'],
                'color': config['color'],
                'boxShadow': SHADOWS['md'],
                'animation': f'slideDown {ANIMATIONS["normal"]}'
            })
        ], style={
            'position': 'fixed',
            'top': SPACING['xl'],
            'right': SPACING['xl'],
            'zIndex': '9998',
            'maxWidth': '400px',
            'display': 'block' if show else 'none'
        })
    
    @staticmethod
    def create_alert_banner(message, type="info", dismissible=True):
        """Creates an alert banner"""
        type_config = {
            "success": {"bg": f"{COLORS['success']}15", "border": COLORS['success'], "text": COLORS['success']},
            "error": {"bg": f"{COLORS['critical']}15", "border": COLORS['critical'], "text": COLORS['critical']},
            "warning": {"bg": f"{COLORS['warning']}15", "border": COLORS['warning'], "text": COLORS['warning']},
            "info": {"bg": f"{COLORS['accent']}15", "border": COLORS['accent'], "text": COLORS['accent']}
        }
        
        config = type_config.get(type, type_config["info"])
        
        return html.Div([
            html.Div([
                html.Span(message, style={'flex': '1'}),
                dismissible and html.Button("×", style={
                    'background': 'none',
                    'border': 'none',
                    'color': config['text'],
                    'fontSize': TYPOGRAPHY['text_lg'],
                    'cursor': 'pointer',
                    'padding': '0'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between'
            })
        ], style={
            'padding': SPACING['lg'],
            'backgroundColor': config['bg'],
            'border': f"1px solid {config['border']}40",
            'borderLeft': f"4px solid {config['border']}",
            'borderRadius': BORDER_RADIUS['md'],
            'color': config['text'],
            'marginBottom': SPACING['lg'],
            'animation': f'fadeIn {ANIMATIONS["normal"]}'
        })


class ModalComponent:
    """Modal dialogs and overlays"""
    
    @staticmethod
    def create_modal(title, content, show=False, size="md"):
        """Creates a modal dialog"""
        sizes = {
            "sm": "400px",
            "md": "600px", 
            "lg": "800px",
            "xl": "1000px"
        }
        
        return html.Div([
            html.Div([
                # Header
                html.Div([
                    html.H3(title, style={
                        'margin': '0',
                        'fontSize': TYPOGRAPHY['text_xl'],
                        'fontWeight': TYPOGRAPHY['font_semibold'],
                        'color': COLORS['text_primary']
                    }),
                    html.Button("×", style={
                        'background': 'none',
                        'border': 'none',
                        'fontSize': TYPOGRAPHY['text_2xl'],
                        'color': COLORS['text_secondary'],
                        'cursor': 'pointer',
                        'padding': '0',
                        'lineHeight': '1'
                    })
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'padding': SPACING['xl'],
                    'borderBottom': f"1px solid {COLORS['border']}"
                }),
                
                # Content
                html.Div(content, style={
                    'padding': SPACING['xl'],
                    'maxHeight': '60vh',
                    'overflowY': 'auto'
                }),
                
                # Footer (optional)
                html.Div([
                    html.Button("Cancel", style={
                        'backgroundColor': 'transparent',
                        'border': f"1px solid {COLORS['border']}",
                        'color': COLORS['text_secondary'],
                        'padding': f"{SPACING['sm']} {SPACING['lg']}",
                        'borderRadius': BORDER_RADIUS['md'],
                        'cursor': 'pointer',
                        'marginRight': SPACING['base']
                    }),
                    html.Button("Confirm", style={
                        'backgroundColor': COLORS['accent'],
                        'border': 'none',
                        'color': COLORS['text_on_accent'],
                        'padding': f"{SPACING['sm']} {SPACING['lg']}",
                        'borderRadius': BORDER_RADIUS['md'],
                        'cursor': 'pointer'
                    })
                ], style={
                    'display': 'flex',
                    'justifyContent': 'flex-end',
                    'padding': SPACING['xl'],
                    'borderTop': f"1px solid {COLORS['border']}"
                })
                
            ], style={
                'backgroundColor': COLORS['surface'],
                'borderRadius': BORDER_RADIUS['xl'],
                'boxShadow': SHADOWS['xl'],
                'border': f"1px solid {COLORS['border']}",
                'maxWidth': sizes.get(size, "600px"),
                'width': '90%',
                'maxHeight': '90vh',
                'animation': f'slideUp {ANIMATIONS["normal"]}'
            })
        ], style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'backgroundColor': 'rgba(15, 20, 25, 0.8)',
            'backdropFilter': 'blur(4px)',
            'display': 'flex' if show else 'none',
            'alignItems': 'center',
            'justifyContent': 'center',
            'zIndex': '9999',
            'animation': f'fadeIn {ANIMATIONS["fast"]}'
        })


class StepperComponent:
    """Step indicator for multi-step processes"""
    
    @staticmethod
    def create_stepper(steps, current_step=1):
        """Creates a horizontal stepper"""
        step_elements = []
        
        for i, step in enumerate(steps, 1):
            is_current = i == current_step
            is_completed = i < current_step
            
            # Step circle
            circle_style = {
                'width': '40px',
                'height': '40px',
                'borderRadius': '50%',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'fontSize': TYPOGRAPHY['text_sm'],
                'fontWeight': TYPOGRAPHY['font_semibold'],
                'border': f"2px solid {COLORS['border']}",
                'transition': f'all {ANIMATIONS["fast"]}'
            }
            
            if is_completed:
                circle_style.update({
                    'backgroundColor': COLORS['success'],
                    'borderColor': COLORS['success'],
                    'color': COLORS['text_on_accent']
                })
                circle_content = "✓"
            elif is_current:
                circle_style.update({
                    'backgroundColor': COLORS['accent'],
                    'borderColor': COLORS['accent'],
                    'color': COLORS['text_on_accent']
                })
                circle_content = str(i)
            else:
                circle_style.update({
                    'backgroundColor': 'transparent',
                    'borderColor': COLORS['border'],
                    'color': COLORS['text_tertiary']
                })
                circle_content = str(i)
            
            step_element = html.Div([
                html.Div(circle_content, style=circle_style),
                html.Div(step, style={
                    'marginTop': SPACING['xs'],
                    'fontSize': TYPOGRAPHY['text_sm'],
                    'fontWeight': TYPOGRAPHY['font_medium'] if is_current else TYPOGRAPHY['font_normal'],
                    'color': COLORS['text_primary'] if is_current else COLORS['text_secondary'],
                    'textAlign': 'center',
                    'maxWidth': '100px'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'flex': '1'
            })
            
            step_elements.append(step_element)
            
            # Add connector line (except for last step)
            if i < len(steps):
                line_color = COLORS['success'] if is_completed else COLORS['border']
                step_elements.append(
                    html.Div(style={
                        'flex': '1',
                        'height': '2px',
                        'backgroundColor': line_color,
                        'margin': '20px 16px 0 16px',
                        'transition': f'background-color {ANIMATIONS["fast"]}'
                    })
                )
        
        return html.Div(step_elements, style={
            'display': 'flex',
            'alignItems': 'flex-start',
            'padding': SPACING['xl'],
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['lg'],
            'border': f"1px solid {COLORS['border']}",
            'marginBottom': SPACING['xl']
        })


class CardComponent:
    """Enhanced card components"""
    
    @staticmethod
    def create_feature_card(icon, title, description, action_text=None, elevated=False):
        """Creates a feature card with icon"""
        card_style = {
            'padding': SPACING['xl'],
            'backgroundColor': COLORS['surface_elevated'] if elevated else COLORS['surface'],
            'borderRadius': BORDER_RADIUS['xl'],
            'border': f"1px solid {COLORS['border']}",
            'boxShadow': SHADOWS['lg'] if elevated else SHADOWS['md'],
            'transition': f'all {ANIMATIONS["fast"]}',
            'cursor': 'pointer' if action_text else 'default',
            'height': '100%'
        }
        
        return html.Div([
            # Icon
            html.Div(icon, style={
                'fontSize': TYPOGRAPHY['text_4xl'],
                'marginBottom': SPACING['lg'],
                'textAlign': 'center'
            }),
            
            # Title
            html.H3(title, style={
                'margin': '0',
                'marginBottom': SPACING['base'],
                'fontSize': TYPOGRAPHY['text_xl'],
                'fontWeight': TYPOGRAPHY['font_semibold'],
                'color': COLORS['text_primary'],
                'textAlign': 'center'
            }),
            
            # Description
            html.P(description, style={
                'margin': '0',
                'fontSize': TYPOGRAPHY['text_base'],
                'color': COLORS['text_secondary'],
                'lineHeight': TYPOGRAPHY['leading_relaxed'],
                'textAlign': 'center',
                'marginBottom': SPACING['lg'] if action_text else '0'
            }),
            
            # Action button (optional)
            action_text and html.Button(action_text, style={
                'width': '100%',
                'padding': f"{SPACING['sm']} {SPACING['lg']}",
                'backgroundColor': 'transparent',
                'border': f"1px solid {COLORS['accent']}",
                'borderRadius': BORDER_RADIUS['md'],
                'color': COLORS['accent'],
                'fontSize': TYPOGRAPHY['text_sm'],
                'fontWeight': TYPOGRAPHY['font_medium'],
                'cursor': 'pointer',
                'transition': f'all {ANIMATIONS["fast"]}'
            })
            
        ], style=card_style, className="hover-lift")
    
    @staticmethod
    def create_stat_card(value, label, trend=None, trend_direction=None):
        """Creates a statistics card"""
        trend_color = COLORS['success'] if trend_direction == 'up' else COLORS['critical'] if trend_direction == 'down' else COLORS['text_tertiary']
        trend_icon = '↗️' if trend_direction == 'up' else '↘️' if trend_direction == 'down' else '➡️'
        
        return html.Div([
            html.Div([
                html.H2(value, style={
                    'margin': '0',
                    'fontSize': TYPOGRAPHY['text_3xl'],
                    'fontWeight': TYPOGRAPHY['font_bold'],
                    'color': COLORS['text_primary']
                }),
                trend and html.Div([
                    html.Span(trend_icon, style={'marginRight': SPACING['xs']}),
                    html.Span(trend, style={
                        'fontSize': TYPOGRAPHY['text_sm'],
                        'fontWeight': TYPOGRAPHY['font_medium'],
                        'color': trend_color
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginTop': SPACING['xs']
                })
            ]),
            html.P(label, style={
                'margin': '0',
                'marginTop': SPACING['base'],
                'fontSize': TYPOGRAPHY['text_base'],
                'color': COLORS['text_secondary'],
                'fontWeight': TYPOGRAPHY['font_medium']
            })
        ], style={
            'padding': SPACING['xl'],
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['lg'],
            'border': f"1px solid {COLORS['border']}",
            'boxShadow': SHADOWS['md'],
            'transition': f'all {ANIMATIONS["fast"]}'
        }, className="hover-lift")


class EmptyStateComponent:
    """Empty state illustrations"""
    
    @staticmethod
    def create_empty_state(icon, title, description, action_text=None):
        """Creates an empty state with optional action"""
        return html.Div([
            html.Div(icon, style={
                'fontSize': '4rem',
                'marginBottom': SPACING['xl'],
                'opacity': '0.5'
            }),
            html.H3(title, style={
                'margin': '0',
                'marginBottom': SPACING['base'],
                'fontSize': TYPOGRAPHY['text_2xl'],
                'fontWeight': TYPOGRAPHY['font_semibold'],
                'color': COLORS['text_primary']
            }),
            html.P(description, style={
                'margin': '0',
                'marginBottom': SPACING['xl'] if action_text else '0',
                'fontSize': TYPOGRAPHY['text_lg'],
                'color': COLORS['text_secondary'],
                'lineHeight': TYPOGRAPHY['leading_relaxed'],
                'maxWidth': '400px'
            }),
            action_text and html.Button(action_text, style={
                'padding': f"{SPACING['base']} {SPACING['xl']}",
                'backgroundColor': COLORS['accent'],
                'border': 'none',
                'borderRadius': BORDER_RADIUS['md'],
                'color': COLORS['text_on_accent'],
                'fontSize': TYPOGRAPHY['text_base'],
                'fontWeight': TYPOGRAPHY['font_medium'],
                'cursor': 'pointer',
                'boxShadow': SHADOWS['md'],
                'transition': f'all {ANIMATIONS["fast"]}'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
            'justifyContent': 'center',
            'textAlign': 'center',
            'padding': SPACING['3xl'],
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['xl'],
            'border': f"1px solid {COLORS['border']}",
            'minHeight': '400px'
        })


# Factory functions
def create_loading_component():
    """Factory function for loading component"""
    return LoadingComponent()

def create_notification_component():
    """Factory function for notification component"""
    return NotificationComponent()

def create_modal_component():
    """Factory function for modal component"""
    return ModalComponent()

def create_stepper_component():
    """Factory function for stepper component"""
    return StepperComponent()

def create_card_component():
    """Factory function for card component"""
    return CardComponent()

def create_empty_state_component():
    """Factory function for empty state component"""
    return EmptyStateComponent()

# Convenience functions for common use cases
def show_loading_overlay(message="Loading..."):
    """Show a loading overlay"""
    return LoadingComponent.create_loading_overlay(message, show=True)

def show_toast(message, type="info"):
    """Show a toast notification"""
    return NotificationComponent.create_toast(message, type, show=True)

def create_workflow_stepper(current_step=1):
    """Create stepper for the main workflow"""
    steps = ["Upload CSV", "Map Columns", "Classify Doors", "Generate Model"]
    return StepperComponent.create_stepper(steps, current_step)

def create_no_data_state():
    """Create a 'no data' empty state"""
    return EmptyStateComponent.create_empty_state(
        "📊",
        "No Data Available",
        "Upload a CSV file to get started with your security analysis.",
        "Upload CSV File"
    )

def create_loading_state():
    """Create a loading empty state"""
    return html.Div([
        LoadingComponent.create_spinner("lg"),
        html.H3("Processing your data...", style={
            'margin': '0',
            'marginTop': SPACING['lg'],
            'fontSize': TYPOGRAPHY['text_xl'],
            'fontWeight': TYPOGRAPHY['font_medium'],
            'color': COLORS['text_primary'],
            'textAlign': 'center'
        }),
        html.P("This may take a few moments for large datasets.", style={
            'margin': '0',
            'marginTop': SPACING['base'],
            'fontSize': TYPOGRAPHY['text_base'],
            'color': COLORS['text_secondary'],
            'textAlign': 'center'
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'padding': SPACING['3xl'],
        'backgroundColor': COLORS['surface'],
        'borderRadius': BORDER_RADIUS['xl'],
        'border': f"1px solid {COLORS['border']}",
        'minHeight': '300px'
    })

def create_error_state(error_message="Something went wrong"):
    """Create an error empty state"""
    return EmptyStateComponent.create_empty_state(
        "❌",
        "Oops! Something went wrong",
        error_message,
        "Try Again"
    )
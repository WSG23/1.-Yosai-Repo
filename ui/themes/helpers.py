from .style_config import COMPONENT_STYLES, COLORS, SPACING, BORDER_RADIUS, SHADOWS, ANIMATIONS, TYPOGRAPHY


def _convert_keys(style_dict):
    """Convert kebab-case keys to camelCase for Dash."""
    converted = {}
    for key, value in style_dict.items():
        if '-' in key:
            parts = key.split('-')
            camel = parts[0] + ''.join(p.title() for p in parts[1:])
            converted[camel] = value
        else:
            converted[key] = value
    return converted


def get_component_style(name):
    """Return component style from CONFIG with camelCase keys."""
    style = COMPONENT_STYLES.get(name, {}).copy()
    return _convert_keys(style)


def get_card_style(elevated=False):
    """Return standard card style."""
    key = 'card_elevated' if elevated else 'card'
    return get_component_style(key)


def get_button_style(variant='primary'):
    """Return standardized button style."""
    return get_component_style(f'button_{variant}')


def get_input_style():
    """Return standardized input style."""
    return get_component_style('input')


def get_card_container_style(padding=SPACING['lg'], margin_bottom=SPACING['md'], elevated=False):
    # Convert numeric values to strings
    if isinstance(margin_bottom, (int, float)):
        margin_bottom = '0' if margin_bottom == 0 else f'{margin_bottom}px'
    if isinstance(padding, (int, float)):
        padding = '0' if padding == 0 else f'{padding}px'
    
    style = get_card_style(elevated)
    style.update({'padding': padding, 'marginBottom': margin_bottom})
    return style


def get_section_header_style(font_size=TYPOGRAPHY['text_xl'], margin_bottom=SPACING['base']):
    """Standard style for section headers."""
    return {
        'color': COLORS['text_primary'],
        'fontSize': font_size,
        'marginBottom': margin_bottom,
        'textAlign': 'center'
    }

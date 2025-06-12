"""Compatibility wrapper for enhanced stats component.

This module provides backward-compatible access to the
:mod:`ui.components.enhanced_stats` implementation. Any imports of
``ui.components.stats`` will transparently use the enhanced
implementation and expose the same factory helpers.
"""

from .enhanced_stats import (
    EnhancedStatsComponent,
    create_enhanced_stats_component,
)


# Backwards compatibility aliases ------------------------------------------------
StatsComponent = EnhancedStatsComponent


def create_stats_container():
    """Create the enhanced stats container."""
    component = EnhancedStatsComponent()
    return component.create_enhanced_stats_container()


def create_custom_header(main_logo_path):
    """Create the enhanced stats header."""
    component = EnhancedStatsComponent()
    return component.create_custom_header(main_logo_path)

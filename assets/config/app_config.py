"""Backwards compatibility wrapper for application settings."""
from .settings import AppConfig, get_config

__all__ = ["AppConfig", "get_config"]

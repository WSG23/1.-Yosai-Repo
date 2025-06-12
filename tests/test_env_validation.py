#!/usr/bin/env python3
"""Test environment variable validation."""

import os
import sys
sys.path.insert(0, '.')

from config.settings import AppConfig


def test_environment_validation_basic():
    original_env = dict(os.environ)
    try:
        os.environ['PORT'] = '99999'
        config = AppConfig.from_env()
        assert config.port == 8050
    finally:
        os.environ.clear()
        os.environ.update(original_env)

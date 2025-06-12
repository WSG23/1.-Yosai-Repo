#!/usr/bin/env python3
"""Run environment variable validation tests."""

import os
import sys
sys.path.insert(0, '.')

from config.settings import test_environment_configuration

if __name__ == "__main__":
    test_environment_configuration()

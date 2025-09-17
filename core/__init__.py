"""
core/__init__.py - Core Package
הגדרת package עיקרי לליבת המערכת
"""

from .config import Config, config
from .logger import setup_logging, get_logger

# מידע על הפקג'
__version__ = "1.0.0"
__author__ = "AlgoTrade Pro"
__description__ = "Core system components for trading platform"

# Export הרכיבים העיקריים
__all__ = [
    'Config',
    'config',
    'setup_logging', 
    'get_logger'
]
"""
ui/__init__.py - UI Package
הגדרת package עיקרי לממשק המשתמש
"""

from .main_window import MainWindow

# מידע על הפקג'
__version__ = "1.0.0"
__author__ = "AlgoTrade Pro"
__description__ = "PyQt6 Trading System UI Components"

# Export החלון הראשי
__all__ = ['MainWindow']
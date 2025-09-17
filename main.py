#!/usr/bin/env python3
"""
AlgoTrade Pro - Trading System
נקודת כניסה ראשית למערכת המסחר
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir
from PyQt6.QtGui import QIcon

# הוספת התיקייה הראשית ל-path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow
from core.config import Config
from core.logger import setup_logging


def setup_application():
    """הגדרת אפליקציית PyQt6"""
    app = QApplication(sys.argv)
    
    # הגדרות בסיסיות
    app.setApplicationName("AlgoTrade Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TradingSystem")
    app.setOrganizationDomain("algotrade.pro")
    
    # הגדרת אייקון אפליקציה (אם קיים)
    icon_path = project_root / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def load_stylesheet(app):
    """טעינת QSS stylesheet"""
    try:
        style_path = project_root / "styles" / "main.qss"
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
        else:
            print(f"Warning: Style file not found at {style_path}")
    except Exception as e:
        print(f"Error loading stylesheet: {e}")


def main():
    """פונקציה ראשית"""
    try:
        # הגדרת logging
        setup_logging()
        
        # יצירת אפליקציה
        app = setup_application()
        
        # טעינת עיצוב
        load_stylesheet(app)
        
        # טעינת הגדרות
        config = Config()
        
        # יצירת החלון הראשי
        main_window = MainWindow(config)
        main_window.show()
        
        # הפעלת לולאת האירועים
        return app.exec()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Critical error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
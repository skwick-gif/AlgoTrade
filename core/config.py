"""
core/config.py - הגדרות מערכת
ניהול קונפיגורציה מרכזי למערכת המסחר
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QSettings, QStandardPaths


@dataclass
class UIConfig:
    """הגדרות ממשק משתמש"""
    theme: str = "light"
    language: str = "en"
    window_width: int = 1400
    window_height: int = 900
    remember_window_state: bool = True
    default_tab: int = 0
    sidebar_width: int = 192
    header_height: int = 64
    auto_save_layout: bool = True


@dataclass
class DataConfig:
    """הגדרות ספקי נתונים"""
    # VIX Data
    vix_provider: str = "yahoo"
    vix_fallback: list = None
    vix_update_interval: int = 60  # שניות
    
    # Market Regime
    market_provider: str = "alphavantage"
    market_fallback: list = None
    market_update_interval: int = 300  # שניות
    
    # Real-time quotes
    quotes_provider: str = "polygon"
    quotes_fallback: list = None
    quotes_update_interval: int = 1  # שנייה
    
    # Options data
    options_provider: str = "polygon"
    options_fallback: list = None
    
    def __post_init__(self):
        """הגדרות ברירת מחדל לאחר יצירה"""
        if self.vix_fallback is None:
            self.vix_fallback = ["fred", "alphavantage"]
        if self.market_fallback is None:
            self.market_fallback = ["fmp", "fred"]
        if self.quotes_fallback is None:
            self.quotes_fallback = ["alphavantage", "twelvedata"]
        if self.options_fallback is None:
            self.options_fallback = ["twelvedata"]


@dataclass
class TradingConfig:
    """הגדרות מסחר"""
    # IBKR Settings
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 7497  # TWS paper trading
    ibkr_client_id: int = 1
    ibkr_timeout: int = 30
    
    # Account Settings
    account_type: str = "paper"  # paper/live
    default_currency: str = "USD"
    
    # Risk Management
    max_position_size: float = 10000.0  # USD
    max_daily_loss: float = 1000.0      # USD
    max_positions: int = 10
    
    # Options Trading
    max_options_positions: int = 5
    min_days_to_expiry: int = 7
    max_days_to_expiry: int = 45


@dataclass
class LoggingConfig:
    """הגדרות לוגים"""
    level: str = "INFO"
    enable_file_logging: bool = True
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # לוגים נפרדים
    enable_trading_log: bool = True
    enable_data_log: bool = True
    enable_error_log: bool = True


class Config:
    """מחלקה ראשית לניהול קונפיגורציה"""
    
    def __init__(self):
        """אתחול הגדרות"""
        self.app_name = "AlgoTrade Pro"
        self.app_version = "1.0.0"
        
        # נתיבי קבצים
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
        
        # יצירת תיקיות אם לא קיימות
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # קבצי קונפיגורציה
        self.default_config_file = self.config_dir / "default_settings.json"
        self.user_config_file = self.config_dir / "user_settings.json"
        self.data_sources_file = self.config_dir / "data_sources_config.json"
        
        # QSettings לשמירת הגדרות PyQt
        self.qt_settings = QSettings(self.app_name, self.app_name)
        
        # טעינת הגדרות
        self._load_configs()
        
    def _load_configs(self):
        """טעינת כל קובצי ההגדרות"""
        # טעינת הגדרות ברירת מחדל
        self.ui = UIConfig()
        self.data = DataConfig()
        self.trading = TradingConfig()
        self.logging = LoggingConfig()
        
        # טעינת הגדרות משתמש (אם קיימות)
        self._load_user_settings()
        
        # טעינת הגדרות ספקי נתונים
        self._load_data_sources_config()
        
    def _load_user_settings(self):
        """טעינת הגדרות משתמש מקובץ JSON"""
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                
                # עדכון הגדרות לפי נתוני משתמש
                if 'ui' in user_data:
                    for key, value in user_data['ui'].items():
                        if hasattr(self.ui, key):
                            setattr(self.ui, key, value)
                            
                if 'data' in user_data:
                    for key, value in user_data['data'].items():
                        if hasattr(self.data, key):
                            setattr(self.data, key, value)
                            
                if 'trading' in user_data:
                    for key, value in user_data['trading'].items():
                        if hasattr(self.trading, key):
                            setattr(self.trading, key, value)
                            
                if 'logging' in user_data:
                    for key, value in user_data['logging'].items():
                        if hasattr(self.logging, key):
                            setattr(self.logging, key, value)
                            
            except Exception as e:
                print(f"Error loading user settings: {e}")
                
    def _load_data_sources_config(self):
        """טעינת הגדרות ספקי נתונים"""
        if self.data_sources_file.exists():
            try:
                with open(self.data_sources_file, 'r', encoding='utf-8') as f:
                    self.data_sources = json.load(f)
            except Exception as e:
                print(f"Error loading data sources config: {e}")
                self.data_sources = self._get_default_data_sources()
        else:
            self.data_sources = self._get_default_data_sources()
            self._save_data_sources_config()
            
    def _get_default_data_sources(self) -> Dict[str, Any]:
        """הגדרות ברירת מחדל לספקי נתונים"""
        return {
            "VIX": {
                "primary": "yahoo",
                "fallback": ["fred", "alphavantage"],
                "update_interval": 60,
                "enabled": True
            },
            "market_regime": {
                "primary": "alphavantage",
                "fallback": ["fmp", "fred"],
                "update_interval": 300,
                "enabled": True
            },
            "real_time_quotes": {
                "primary": "polygon",
                "fallback": ["alphavantage", "twelvedata"],
                "update_interval": 1,
                "enabled": True
            },
            "options_chain": {
                "primary": "polygon",
                "fallback": ["twelvedata"],
                "update_interval": 30,
                "enabled": True
            },
            "historical_data": {
                "primary": "alphavantage",
                "fallback": ["yahoo", "twelvedata"],
                "update_interval": 3600,
                "enabled": True
            }
        }
        
    def save_settings(self):
        """שמירת כל ההגדרות"""
        self._save_user_settings()
        self._save_qt_settings()
        
    def _save_user_settings(self):
        """שמירת הגדרות משתמש לקובץ JSON"""
        try:
            user_data = {
                'ui': asdict(self.ui),
                'data': asdict(self.data),
                'trading': asdict(self.trading),
                'logging': asdict(self.logging)
            }
            
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving user settings: {e}")
            
    def _save_data_sources_config(self):
        """שמירת הגדרות ספקי נתונים"""
        try:
            with open(self.data_sources_file, 'w', encoding='utf-8') as f:
                json.dump(self.data_sources, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data sources config: {e}")
            
    def _save_qt_settings(self):
        """שמירת הגדרות PyQt"""
        try:
            # שמירת גודל וטיב חלון
            if hasattr(self, '_main_window'):
                self.qt_settings.setValue("geometry", self._main_window.saveGeometry())
                self.qt_settings.setValue("windowState", self._main_window.saveState())
                
            # שמירת הגדרות נוספות
            self.qt_settings.setValue("current_tab", self.ui.default_tab)
            self.qt_settings.setValue("theme", self.ui.theme)
            
        except Exception as e:
            print(f"Error saving Qt settings: {e}")
            
    def load_qt_settings(self, main_window):
        """טעינת הגדרות PyQt"""
        try:
            self._main_window = main_window
            
            if self.ui.remember_window_state:
                geometry = self.qt_settings.value("geometry")
                window_state = self.qt_settings.value("windowState")
                
                if geometry:
                    main_window.restoreGeometry(geometry)
                if window_state:
                    main_window.restoreState(window_state)
                    
            # טעינת הגדרות נוספות
            self.ui.default_tab = int(self.qt_settings.value("current_tab", 0))
            self.ui.theme = self.qt_settings.value("theme", "light")
            
        except Exception as e:
            print(f"Error loading Qt settings: {e}")
            
    def get_data_source_config(self, component: str) -> Dict[str, Any]:
        """קבלת הגדרות ספק נתונים לקומפוננטה מסוימת"""
        return self.data_sources.get(component, {})
        
    def set_data_source_config(self, component: str, config: Dict[str, Any]):
        """הגדרת ספק נתונים לקומפוננטה"""
        self.data_sources[component] = config
        self._save_data_sources_config()
        
    def get_log_file_path(self, log_type: str = "application") -> Path:
        """קבלת נתיב קובץ לוג"""
        return self.logs_dir / f"{log_type}.log"
        

    def get_api_keys_json_file(self) -> Path:
        """קבלת נתיב קובץ מפתחות API בפורמט JSON"""
        return self.config_dir / "api_keys.json"

    def load_api_keys(self) -> Dict[str, str]:
        """טעינת מפתחות API מקובץ JSON לכל הספקים"""
        api_keys_path = self.get_api_keys_json_file()
        if api_keys_path.exists():
            try:
                with open(api_keys_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading API keys: {e}")
                return {}
        else:
            print(f"API keys file not found: {api_keys_path}")
            return {}
        
    def is_paper_trading(self) -> bool:
        """בדיקה אם במצב paper trading"""
        return self.trading.account_type == "paper"
        
    def get_ibkr_port(self) -> int:
        """קבלת פורט IBKR לפי סוג חשבון"""
        if self.trading.account_type == "paper":
            return 7497  # TWS Paper Trading
        else:
            return 7496  # TWS Live Trading
            
    def __str__(self) -> str:
        """יצוג טקסטואלי של ההגדרות"""
        return f"Config(app={self.app_name} v{self.app_version}, paper_trading={self.is_paper_trading()})"


# יצירת instance גלובלי
config = Config()

# Export
__all__ = ['Config', 'UIConfig', 'DataConfig', 'TradingConfig', 'LoggingConfig', 'config']
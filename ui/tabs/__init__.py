"""
ui/tabs/__init__.py - מבנה לשוניות
הגדרות וקבועים לכל 6 הלשוניות מהארטיפקט המקורי
"""

from typing import Dict, List, Any
from enum import Enum


class TabIndex(Enum):
    """אינדקסים של הלשוניות"""
    DASHBOARD = 0
    SCANNING = 1
    WATCHLIST = 2
    OPTIONS_TRADING = 3
    ANALYTICS = 4
    SETTINGS = 5


class TabNames:
    """שמות הלשוניות"""
    DASHBOARD = "Dashboard"
    SCANNING = "Scanning"
    WATCHLIST = "Watchlist"
    OPTIONS_TRADING = "Options Trading"
    ANALYTICS = "Analytics"
    SETTINGS = "Settings"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """קבלת כל שמות הלשוניות"""
        return [
            cls.DASHBOARD,
            cls.SCANNING,
            cls.WATCHLIST,
            cls.OPTIONS_TRADING,
            cls.ANALYTICS,
            cls.SETTINGS
        ]


class SidebarContent:
    """תוכן הסיידבר לכל לשונית - מהארטיפקט המקורי"""
    
    DASHBOARD = [
        "Overview",
        "Markets", 
        "Positions",
        "P&L",
        "News",
        "Alerts"
    ]
    
    SCANNING = [
        "Stock Scanner",
        "Options Scanner", 
        "Filters",
        "Results",
        "Saved Scans",
        "Export"
    ]
    
    WATCHLIST = [
        "Active List",
        "Create List",
        "Price Alerts",
        "Volume Alerts", 
        "Technical Alerts",
        "History"
    ]
    
    OPTIONS_TRADING = [
        "Strategy Builder",
        "Active Trades",
        "Strategy 1-4",
        "Backtest",
        "Settings"
    ]
    
    ANALYTICS = [
        "Performance",
        "Reports",
        "Trade History",
        "Risk Analysis",
        "Charts",
        "Export"
    ]
    
    SETTINGS = [
        "Account",
        "Data Sources",
        "API Keys",
        "Notifications",
        "Import/Export", 
        "About"
    ]
    
    @classmethod
    def get_content(cls, tab_name: str) -> List[str]:
        """קבלת תוכן סיידבר לפי שם לשונית"""
        content_map = {
            TabNames.DASHBOARD: cls.DASHBOARD,
            TabNames.SCANNING: cls.SCANNING,
            TabNames.WATCHLIST: cls.WATCHLIST,
            TabNames.OPTIONS_TRADING: cls.OPTIONS_TRADING,
            TabNames.ANALYTICS: cls.ANALYTICS,
            TabNames.SETTINGS: cls.SETTINGS
        }
        return content_map.get(tab_name, [])
    
    @classmethod
    def get_all_content(cls) -> Dict[str, List[str]]:
        """קבלת כל התוכן"""
        return {
            TabNames.DASHBOARD: cls.DASHBOARD,
            TabNames.SCANNING: cls.SCANNING,
            TabNames.WATCHLIST: cls.WATCHLIST,
            TabNames.OPTIONS_TRADING: cls.OPTIONS_TRADING,
            TabNames.ANALYTICS: cls.ANALYTICS,
            TabNames.SETTINGS: cls.SETTINGS
        }


class TabIcons:
    """אייקונים לכל לשונית (אופציונלי - לעתיד)"""
    DASHBOARD = "dashboard"
    SCANNING = "search"
    WATCHLIST = "list"
    OPTIONS_TRADING = "trending-up"
    ANALYTICS = "bar-chart"
    SETTINGS = "settings"


class TabTooltips:
    """הסברים לכל לשונית"""
    DASHBOARD = "Overview of markets, positions and P&L"
    SCANNING = "Scan stocks and options for trading opportunities"
    WATCHLIST = "Manage watchlists and alerts"
    OPTIONS_TRADING = "Options strategies and active trades"
    ANALYTICS = "Performance analysis and reports"
    SETTINGS = "Application settings and configuration"
    
    @classmethod
    def get_tooltip(cls, tab_name: str) -> str:
        """קבלת tooltip לפי שם לשונית"""
        tooltip_map = {
            TabNames.DASHBOARD: cls.DASHBOARD,
            TabNames.SCANNING: cls.SCANNING,
            TabNames.WATCHLIST: cls.WATCHLIST,
            TabNames.OPTIONS_TRADING: cls.OPTIONS_TRADING,
            TabNames.ANALYTICS: cls.ANALYTICS,
            TabNames.SETTINGS: cls.SETTINGS
        }
        return tooltip_map.get(tab_name, "")


class TabConfig:
    """הגדרות כלליות ללשוניות"""
    
    # הגדרות UI
    TAB_HEIGHT = 48
    TAB_PADDING = "12px 16px"  # py-3 px-4
    TAB_BORDER_WIDTH = 2
    
    # צבעים
    ACTIVE_COLOR = "#2563eb"      # blue-600
    INACTIVE_COLOR = "#6b7280"    # gray-500
    HOVER_COLOR = "#374151"       # gray-700
    BORDER_COLOR = "#e5e7eb"      # gray-200
    
    # אנימציות
    TRANSITION_DURATION = 200     # מילישניות
    
    @classmethod
    def get_tab_style(cls, is_active: bool = False, is_hover: bool = False) -> str:
        """קבלת CSS style לכפתור לשונית"""
        if is_active:
            return f"""
                color: {cls.ACTIVE_COLOR};
                border-bottom: {cls.TAB_BORDER_WIDTH}px solid {cls.ACTIVE_COLOR};
                background-color: transparent;
            """
        elif is_hover:
            return f"""
                color: {cls.HOVER_COLOR};
                border-bottom: {cls.TAB_BORDER_WIDTH}px solid {cls.BORDER_COLOR};
                background-color: transparent;
            """
        else:
            return f"""
                color: {cls.INACTIVE_COLOR};
                border-bottom: {cls.TAB_BORDER_WIDTH}px solid transparent;
                background-color: transparent;
            """


class TabValidator:
    """ולידציה של נתוני לשוניות"""
    
    @staticmethod
    def is_valid_tab_name(tab_name: str) -> bool:
        """בדיקה אם שם לשונית תקין"""
        return tab_name in TabNames.get_all()
    
    @staticmethod
    def is_valid_tab_index(index: int) -> bool:
        """בדיקה אם אינדקס לשונית תקין"""
        return 0 <= index < len(TabNames.get_all())
    
    @staticmethod
    def is_valid_sidebar_button(tab_name: str, button_name: str) -> bool:
        """בדיקה אם כפתור סיידבר תקין ללשונית"""
        sidebar_content = SidebarContent.get_content(tab_name)
        return button_name in sidebar_content
    
    @staticmethod
    def get_tab_name_by_index(index: int) -> str:
        """קבלת שם לשונית לפי אינדקס"""
        if TabValidator.is_valid_tab_index(index):
            return TabNames.get_all()[index]
        return ""
    
    @staticmethod
    def get_tab_index_by_name(tab_name: str) -> int:
        """קבלת אינדקס לשונית לפי שם"""
        try:
            return TabNames.get_all().index(tab_name)
        except ValueError:
            return -1


class TabManager:
    """מנהל לשוניות - עזר לניהול מצב הלשוניות"""
    
    def __init__(self):
        self.current_tab_index = 0
        self.current_sidebar_button = None
        
    def set_current_tab(self, index: int) -> bool:
        """הגדרת לשונית נוכחית"""
        if TabValidator.is_valid_tab_index(index):
            self.current_tab_index = index
            self.current_sidebar_button = None  # איפוס כפתור סיידבר
            return True
        return False
    
    def set_current_tab_by_name(self, tab_name: str) -> bool:
        """הגדרת לשונית נוכחית לפי שם"""
        index = TabValidator.get_tab_index_by_name(tab_name)
        return self.set_current_tab(index)
    
    def get_current_tab_name(self) -> str:
        """קבלת שם הלשונית הנוכחית"""
        return TabValidator.get_tab_name_by_index(self.current_tab_index)
    
    def get_current_sidebar_content(self) -> List[str]:
        """קבלת תוכן סיידבר ללשונית הנוכחית"""
        tab_name = self.get_current_tab_name()
        return SidebarContent.get_content(tab_name)
    
    def set_current_sidebar_button(self, button_name: str) -> bool:
        """הגדרת כפתור סיידבר נוכחי"""
        tab_name = self.get_current_tab_name()
        if TabValidator.is_valid_sidebar_button(tab_name, button_name):
            self.current_sidebar_button = button_name
            return True
        return False
    
    def get_current_content_title(self) -> str:
        """קבלת כותרת התוכן הנוכחי"""
        tab_name = self.get_current_tab_name()
        if self.current_sidebar_button:
            return f"{tab_name} - {self.current_sidebar_button}"
        return f"{tab_name} Content"
    
    def next_tab(self) -> bool:
        """מעבר ללשונית הבאה"""
        next_index = (self.current_tab_index + 1) % len(TabNames.get_all())
        return self.set_current_tab(next_index)
    
    def previous_tab(self) -> bool:
        """מעבר ללשונית הקודמת"""
        prev_index = (self.current_tab_index - 1) % len(TabNames.get_all())
        return self.set_current_tab(prev_index)


# יצירת instance גלובלי למנהל לשוניות
tab_manager = TabManager()

# Export כל הקלאסים והקבועים
__all__ = [
    'TabIndex',
    'TabNames', 
    'SidebarContent',
    'TabIcons',
    'TabTooltips',
    'TabConfig',
    'TabValidator',
    'TabManager',
    'tab_manager'
]
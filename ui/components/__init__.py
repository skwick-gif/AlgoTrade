"""
ui/components/__init__.py - UI Components Package
הגדרת package לכל רכיבי הממשק
"""

from .header import HeaderWidget, HeaderContainer, LogoWidget, HeaderSeparator
from .vix_gauge import VixGaugeWidget
from .market_indicator import MarketIndicatorWidget, MarketRegimeContainer, TrendingIcon
from .ibkr_status import IBKRStatusWidget, IBKRStatusContainer, WifiIcon, StatusDot

# מידע על הפקג'
__version__ = "1.0.0"
__author__ = "AlgoTrade Pro"
__description__ = "UI Components for trading interface based on React artifact"

# Export כל הרכיבים
__all__ = [
    # Header components
    'HeaderWidget',
    'HeaderContainer', 
    'LogoWidget',
    'HeaderSeparator',
    
    # VIX Gauge
    'VixGaugeWidget',
    
    # Market Indicator
    'MarketIndicatorWidget',
    'MarketRegimeContainer',
    'TrendingIcon',
    
    # IBKR Status  
    'IBKRStatusWidget',
    'IBKRStatusContainer',
    'WifiIcon',
    'StatusDot'
]
"""
data_management/providers/base_provider.py - מחלקת בסיס לכל ספקי הנתונים
הגדרת ממשק אחיד לכל 7 הספקים
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from core.logger import get_logger


@dataclass
class QuoteData:
    """נתוני ציטוט בסיסיים"""
    symbol: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה ל-dictionary"""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'volume': self.volume,
            'change': self.change,
            'change_percent': self.change_percent
        }


@dataclass
class ProviderStatus:
    """סטטוס ספק נתונים"""
    is_available: bool = True
    last_request: Optional[datetime] = None
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    quota_remaining: Optional[int] = None
    quota_limit: Optional[int] = None
    
    @property
    def quota_usage_percent(self) -> float:
        """אחוז שימוש במכסה"""
        if self.quota_limit and self.quota_remaining is not None:
            used = self.quota_limit - self.quota_remaining
            return (used / self.quota_limit) * 100
        return 0.0


class BaseProvider(ABC):
    """מחלקת בסיס לכל ספקי הנתונים"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.logger = get_logger(f"Data.{name}")
        self.status = ProviderStatus()
        
        # הגדרות rate limiting
        self.requests_per_minute = 60  # ברירת מחדל
        self.min_request_interval = 1.0  # שנייה
        self.last_request_time = 0.0
        
        # Cache פשוט
        self._cache = {}
        self.cache_ttl = 300  # 5 דקות
        
    def _update_status(self, success: bool, error_msg: str = None):
        """עדכון סטטוס הספק"""
        self.status.last_request = datetime.now()
        self.status.request_count += 1
        
        if success:
            self.status.is_available = True
        else:
            self.status.error_count += 1
            self.status.last_error = error_msg
            self.status.is_available = False
            self.logger.error(f"Provider error: {error_msg}")
    
    def _rate_limit_check(self):
        """בדיקת rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """קבלת נתונים מ-cache"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                self.logger.debug(f"Cache hit for {key}")
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """שמירה ב-cache"""
        self._cache[key] = (data, datetime.now())
        self.logger.debug(f"Cached data for {key}")
    
    def _make_request(self, cache_key: str = None) -> Any:
        """template method לביצוע בקשה"""
        # בדיקת cache
        if cache_key:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # בדיקת rate limiting
        self._rate_limit_check()
        
        try:
            # הקריאה בפועל (מומשת בכל ספק)
            data = self._fetch_data()
            
            # עדכון cache
            if cache_key and data:
                self._set_cache(cache_key, data)
            
            self._update_status(success=True)
            return data
            
        except Exception as e:
            self._update_status(success=False, error_msg=str(e))
            raise
    
    @abstractmethod
    def _fetch_data(self) -> Any:
        """קריאת נתונים בפועל - מומשת בכל ספק"""
        pass
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[QuoteData]:
        """קבלת ציטוט לסימבול"""
        pass
    
    @abstractmethod
    def get_vix(self) -> Optional[QuoteData]:
        """קבלת נתוני VIX"""
        pass
    
    def test_connection(self) -> bool:
        """בדיקת חיבור לספק"""
        try:
            # נסיון לקבל VIX כבדיקה
            vix_data = self.get_vix()
            return vix_data is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_status(self) -> ProviderStatus:
        """קבלת סטטוס הספק"""
        return self.status
    
    def reset_status(self):
        """איפוס סטטוס"""
        self.status = ProviderStatus()
        self.logger.info(f"Status reset for {self.name}")
    
    def is_healthy(self) -> bool:
        """בדיקה אם הספק תקין"""
        return (
            self.status.is_available and 
            self.status.error_count < 5 and  # פחות מ-5 שגיאות
            self.status.quota_usage_percent < 95  # פחות מ-95% מכסה
        )
    
    def __str__(self) -> str:
        """יצוג טקסטואלי"""
        return f"{self.name}(available={self.status.is_available}, requests={self.status.request_count})"
    
    def __repr__(self) -> str:
        return self.__str__()
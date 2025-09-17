"""
data_management/data_router.py - ניתוב חכם בין ספקי נתונים
בחירת ספק אוטומטית + Fallback cascade + Load balancing + Cache חכם
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import json
from pathlib import Path
from dataclasses import dataclass, asdict

from core.logger import get_logger
from core.config import config
from .providers.base_provider import BaseProvider, QuoteData
from .providers.fred_provider import FREDProvider
from .providers.yahoo_provider import YahooProvider


@dataclass
class ProviderConfig:
    """הגדרות ספק נתונים"""
    name: str
    primary: bool = False
    priority: int = 1  # נמוך = עדיפות גבוהה
    enabled: bool = True
    max_errors: int = 5
    cooldown_minutes: int = 15


@dataclass
class DataRequest:
    """בקשת נתונים"""
    data_type: str  # "VIX", "quote", "market_regime" 
    symbol: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    use_cache: bool = True
    max_age_seconds: int = 60


class DataRouter:
    """נתב נתונים חכם עם fallback ו-load balancing"""
    
    def __init__(self):
        self.logger = get_logger("DataRouter")
        
        # ספקי נתונים רשומים
        self._providers: Dict[str, BaseProvider] = {}
        self._provider_configs: Dict[str, ProviderConfig] = {}
        
        # מטמון גלובלי
        self._global_cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.default_cache_ttl = 60  # שניות
        
        # מעקב אחר כישלונות ו-cooldowns
        self._provider_cooldowns: Dict[str, datetime] = {}
        self._provider_errors: Dict[str, int] = {}
        
        # הגדרות routing לפי סוג נתונים
        self._routing_config = {
            "VIX": {
                "primary": "fred",
                "fallback": ["yahoo"],  # yahoo כ-fallback
                "cache_ttl": 300,  # 5 דקות
                "max_retries": 2
            },
            "quote": {
                "primary": "yahoo", 
                "fallback": ["yahoo"],
                "cache_ttl": 30,
                "max_retries": 2
            },
            "market_data": {
                "primary": "yahoo",
                "fallback": ["yahoo"],
                "cache_ttl": 300,  # 5 דקות
                "max_retries": 1
            }
        }
        
        self._initialize_providers()
        self.logger.info("DataRouter initialized")
    
    def _initialize_providers(self):
        """אתחול ספקי נתונים"""
        # FRED לVIX (יציב ואמין)
        try:
            self.logger.info("Initializing FRED provider...")
            from .providers.fred_provider import FREDProvider
            fred_provider = FREDProvider(config)
            self.register_provider("fred", fred_provider, is_primary=True)
            self.logger.info("FRED provider registered successfully")
            connection_test = fred_provider.test_connection()
            self.logger.info(f"FRED connection test: {'PASS' if connection_test else 'FAIL'}")
        except Exception as e:
            self.logger.error(f"Failed to initialize FRED provider: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")

        # Yahoo Finance
        try:
            self.logger.info("Initializing Yahoo Finance provider...")
            from .providers.yahoo_provider import YahooProvider
            yahoo_provider = YahooProvider(config)
            self.register_provider("yahoo", yahoo_provider, is_primary=False)
            self.logger.info("Yahoo Finance provider registered")
        except Exception as e:
            self.logger.warning(f"Yahoo Finance provider failed: {e}")

        # Finnhub
        try:
            self.logger.info("Initializing Finnhub provider...")
            from .providers.finnhub_provider import FinnhubProvider
            finnhub_provider = FinnhubProvider(config)
            self.register_provider("finnhub", finnhub_provider, is_primary=False)
            self.logger.info("Finnhub provider registered")
        except Exception as e:
            self.logger.warning(f"Finnhub provider failed: {e}")

        # Alphavantage
        try:
            self.logger.info("Initializing Alphavantage provider...")
            from .providers.alphavantage_provider import AlphavantageProvider
            alphavantage_provider = AlphavantageProvider(config)
            self.register_provider("alphavantage", alphavantage_provider, is_primary=False)
            self.logger.info("Alphavantage provider registered")
        except Exception as e:
            self.logger.warning(f"Alphavantage provider failed: {e}")

        # Polygon
        try:
            self.logger.info("Initializing Polygon provider...")
            from .providers.polygon_provider import PolygonProvider
            polygon_provider = PolygonProvider(config)
            self.register_provider("polygon", polygon_provider, is_primary=False)
            self.logger.info("Polygon provider registered")
        except Exception as e:
            self.logger.warning(f"Polygon provider failed: {e}")

        # Twelvedata
        try:
            self.logger.info("Initializing Twelvedata provider...")
            from .providers.twelvedata_provider import TwelvedataProvider
            twelvedata_provider = TwelvedataProvider(config)
            self.register_provider("twelvedata", twelvedata_provider, is_primary=False)
            self.logger.info("Twelvedata provider registered")
        except Exception as e:
            self.logger.warning(f"Twelvedata provider failed: {e}")

        # FMP
        try:
            self.logger.info("Initializing FMP provider...")
            from .providers.fmp_provider import FMPProvider
            fmp_provider = FMPProvider(config)
            self.register_provider("fmp", fmp_provider, is_primary=False)
            self.logger.info("FMP provider registered")
        except Exception as e:
            self.logger.warning(f"FMP provider failed: {e}")
    
    def register_provider(self, name: str, provider: BaseProvider, is_primary: bool = False):
        """רישום ספק נתונים"""
        self._providers[name] = provider
        
        config = ProviderConfig(
            name=name,
            primary=is_primary,
            priority=1 if is_primary else 2,
            enabled=True
        )
        self._provider_configs[name] = config
        self._provider_errors[name] = 0
        
        self.logger.info(f"Provider '{name}' registered (primary={is_primary})")
    
    def _get_cache_key(self, request: DataRequest) -> str:
        """יצירת מפתח cache"""
        base = f"{request.data_type}"
        if request.symbol:
            base += f"_{request.symbol}"
        if request.parameters:
            # מיון parameters לעקביות
            params_str = "_".join(f"{k}={v}" for k, v in sorted(request.parameters.items()))
            base += f"_{params_str}"
        return base
    
    def _get_from_cache(self, cache_key: str, max_age_seconds: int) -> Optional[Any]:
        """קבלת נתונים מ-cache"""
        if cache_key in self._global_cache:
            data, timestamp = self._global_cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()
            
            if age <= max_age_seconds:
                self.logger.debug(f"Cache hit for {cache_key} (age: {age:.1f}s)")
                return data
            else:
                # נתונים ישנים - מחיקה
                del self._global_cache[cache_key]
                self.logger.debug(f"Cache expired for {cache_key} (age: {age:.1f}s)")
        
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """שמירה ב-cache"""
        self._global_cache[cache_key] = (data, datetime.now())
        self.logger.debug(f"Cached data for {cache_key}")
    
    def _is_provider_available(self, provider_name: str) -> bool:
        """בדיקה אם ספק זמין"""
        # בדיקת cooldown
        if provider_name in self._provider_cooldowns:
            cooldown_end = self._provider_cooldowns[provider_name]
            if datetime.now() < cooldown_end:
                return False
        
        # בדיקת הגדרות
        config = self._provider_configs.get(provider_name)
        if not config or not config.enabled:
            return False
        
        # בדיקת מספר שגיאות
        error_count = self._provider_errors.get(provider_name, 0)
        if error_count >= config.max_errors:
            return False
        
        # בדיקת health של הספק
        provider = self._providers.get(provider_name)
        if provider and not provider.is_healthy():
            return False
        
        return True
    
    def _get_available_providers(self, data_type: str) -> List[str]:
        """קבלת רשימת ספקים זמינים לסוג נתונים"""
        self.logger.debug(f"Looking for providers for data_type: {data_type}")
        self.logger.debug(f"Registered providers: {list(self._providers.keys())}")
        
        routing = self._routing_config.get(data_type, {})
        primary = routing.get("primary")
        fallback = routing.get("fallback", [])
        
        self.logger.debug(f"Routing config for {data_type}: primary={primary}, fallback={fallback}")
        
        # בניית רשימה מסודרת
        provider_list = []
        if primary and self._is_provider_available(primary):
            provider_list.append(primary)
            self.logger.debug(f"Added primary provider: {primary}")
        elif primary:
            self.logger.warning(f"Primary provider '{primary}' not available")
        
        for provider_name in fallback:
            if provider_name != primary and self._is_provider_available(provider_name):
                provider_list.append(provider_name)
                self.logger.debug(f"Added fallback provider: {provider_name}")
        
        self.logger.info(f"Available providers for {data_type}: {provider_list}")
        return provider_list
    
    def _handle_provider_error(self, provider_name: str, error: Exception):
        """טיפול בשגיאת ספק"""
        self._provider_errors[provider_name] = self._provider_errors.get(provider_name, 0) + 1
        
        config = self._provider_configs.get(provider_name)
        if config and self._provider_errors[provider_name] >= config.max_errors:
            # הכנסה ל-cooldown
            cooldown_end = datetime.now() + timedelta(minutes=config.cooldown_minutes)
            self._provider_cooldowns[provider_name] = cooldown_end
            
            self.logger.warning(f"Provider '{provider_name}' in cooldown until {cooldown_end}")
        
        self.logger.error(f"Provider '{provider_name}' error: {error}")
    
    def _execute_request(self, provider_name: str, request: DataRequest) -> Optional[Any]:
        """ביצוע בקשה לספק ספציפי"""
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        try:
            if request.data_type == "VIX":
                return provider.get_vix()
            elif request.data_type == "quote":
                if not request.symbol:
                    raise ValueError("Symbol required for quote request")
                return provider.get_quote(request.symbol)
            elif request.data_type == "market_data":
                if hasattr(provider, 'get_market_data'):
                    return provider.get_market_data()
                else:
                    raise NotImplementedError(f"Provider '{provider_name}' doesn't support market_data")
            else:
                raise ValueError(f"Unsupported data type: {request.data_type}")
                
        except Exception as e:
            self._handle_provider_error(provider_name, e)
            raise
    
    def get_data(self, request: DataRequest) -> Optional[Any]:
        """קבלת נתונים עם routing אוטומטי"""
        # בדיקת cache
        if request.use_cache:
            cache_key = self._get_cache_key(request)
            cached_data = self._get_from_cache(cache_key, request.max_age_seconds)
            if cached_data:
                return cached_data
        
        # קבלת ספקים זמינים
        available_providers = self._get_available_providers(request.data_type)
        
        if not available_providers:
            self.logger.error(f"No available providers for {request.data_type}")
            return None
        
        # ניסיון לקבל נתונים מכל ספק
        routing_config = self._routing_config.get(request.data_type, {})
        max_retries = routing_config.get("max_retries", 1)
        
        for provider_name in available_providers:
            for attempt in range(max_retries + 1):
                try:
                    self.logger.debug(f"Requesting {request.data_type} from {provider_name} (attempt {attempt + 1})")
                    
                    data = self._execute_request(provider_name, request)
                    
                    if data:
                        # הצלחה - שמירה ב-cache
                        if request.use_cache:
                            cache_ttl = routing_config.get("cache_ttl", self.default_cache_ttl)
                            request.max_age_seconds = cache_ttl
                            cache_key = self._get_cache_key(request)
                            self._set_cache(cache_key, data)
                        
                        # איפוס מונה שגיאות
                        self._provider_errors[provider_name] = 0
                        
                        self.logger.info(f"Successfully got {request.data_type} from {provider_name}")
                        return data
                    
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {provider_name}: {e}")
                    if attempt == max_retries:
                        break  # עבור לספק הבא
        
        self.logger.error(f"Failed to get {request.data_type} from all available providers")
        return None
    
    # פונקציות נוחות
    def get_vix(self) -> Optional[QuoteData]:
        """קבלת נתוני VIX"""
        request = DataRequest(data_type="VIX", max_age_seconds=60)
        return self.get_data(request)
    
    def get_quote(self, symbol: str) -> Optional[QuoteData]:
        """קבלת ציטוט"""
        request = DataRequest(data_type="quote", symbol=symbol, max_age_seconds=30)
        return self.get_data(request)
    
    def get_market_data(self) -> Optional[Dict[str, QuoteData]]:
        """קבלת נתוני שוק"""
        request = DataRequest(data_type="market_data", max_age_seconds=300)
        return self.get_data(request)
    
    def test_all_providers(self) -> Dict[str, bool]:
        """בדיקת כל הספקים"""
        results = {}
        for name, provider in self._providers.items():
            try:
                results[name] = provider.test_connection()
                self.logger.info(f"Provider '{name}' test: {'PASS' if results[name] else 'FAIL'}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"Provider '{name}' test failed: {e}")
        
        return results
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """קבלת סטטוס כל הספקים"""
        status = {}
        
        for name, provider in self._providers.items():
            provider_status = provider.get_status()
            config = self._provider_configs.get(name)
            
            status[name] = {
                "available": self._is_provider_available(name),
                "healthy": provider.is_healthy(),
                "enabled": config.enabled if config else False,
                "error_count": self._provider_errors.get(name, 0),
                "request_count": provider_status.request_count,
                "last_request": provider_status.last_request.isoformat() if provider_status.last_request else None,
                "quota_usage": provider_status.quota_usage_percent,
                "in_cooldown": name in self._provider_cooldowns and datetime.now() < self._provider_cooldowns[name]
            }
        
        return status
    
    def reset_provider_errors(self, provider_name: str = None):
        """איפוס שגיאות ספק"""
        if provider_name:
            self._provider_errors[provider_name] = 0
            if provider_name in self._provider_cooldowns:
                del self._provider_cooldowns[provider_name]
            self.logger.info(f"Reset errors for provider '{provider_name}'")
        else:
            self._provider_errors.clear()
            self._provider_cooldowns.clear()
            self.logger.info("Reset errors for all providers")
    
    def clear_cache(self, pattern: str = None):
        """ניקוי cache"""
        if pattern:
            # ניקוי לפי pattern
            keys_to_remove = [k for k in self._global_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._global_cache[key]
            self.logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{pattern}'")
        else:
            # ניקוי מלא
            cache_size = len(self._global_cache)
            self._global_cache.clear()
            self.logger.info(f"Cleared entire cache ({cache_size} entries)")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """סטטיסטיקות cache"""
        now = datetime.now()
        total_entries = len(self._global_cache)
        expired_entries = 0
        
        for key, (data, timestamp) in self._global_cache.items():
            age = (now - timestamp).total_seconds()
            if age > self.default_cache_ttl:
                expired_entries += 1
        
        try:
            self.logger.info("Initializing FRED provider...")
            fred_provider = FREDProvider(config)
            self.register_provider("fred", fred_provider, is_primary=True)
            self.logger.info("FRED provider registered successfully")
            # בדיקת חיבור מיידית
            connection_test = fred_provider.test_connection()
            self.logger.info(f"FRED connection test: {'PASS' if connection_test else 'FAIL'}")
        except Exception as e:
            self.logger.error(f"Failed to initialize FRED provider: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
        # Yahoo Finance כ-fallback (אם נצליח לתקן אותו בעתיד)
        try:
            self.logger.info("Initializing Yahoo Finance provider as fallback...")
            yahoo_provider = YahooProvider(config)
            self.register_provider("yahoo", yahoo_provider, is_primary=False)
            self.logger.info("Yahoo Finance fallback registered")
        except Exception as e:
            self.logger.warning(f"Yahoo Finance fallback failed: {e}")
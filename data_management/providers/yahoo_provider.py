"""
data_management/providers/yahoo_provider.py - ספק Yahoo Finance
חיבור לYahoo Finance באמצעות yfinance לקבלת נתוני VIX בזמן אמת
"""

import yfinance as yf
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

from .base_provider import BaseProvider, QuoteData

class YahooProvider(BaseProvider):
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, period: str = None) -> Optional[pd.DataFrame]:
        """
        שליפת נתונים היסטוריים לפי טווח תאריכים או period, כולל כל הפרמטרים
        """
        import logging
        import threading
        logger = logging.getLogger("YahooProvider.get_historical_data")
        try:
            self._rate_limit_check()
            logger.info(f"[YahooProvider] מתחיל קריאת yfinance.Ticker({symbol})")
            ticker = yf.Ticker(symbol)
            result = {}
            def fetch_history():
                try:
                    kwargs = dict(interval="1d", auto_adjust=True, actions=True)
                    if period:
                        logger.info(f"[YahooProvider] קריאה עם period={period}, interval=1d, auto_adjust=True, actions=True")
                        result['history'] = ticker.history(period=period, **kwargs)
                    else:
                        logger.info(f"[YahooProvider] קריאה עם start={start_date}, end={end_date}, interval=1d, auto_adjust=True, actions=True")
                        result['history'] = ticker.history(start=start_date, end=end_date, **kwargs)
                except Exception as e:
                    result['error'] = e
            t = threading.Thread(target=fetch_history)
            t.start()
            t.join(timeout=15)
            if t.is_alive():
                logger.error(f"[YahooProvider] קריאת ticker.history נתקעה (timeout)")
                return None
            if 'error' in result:
                logger.error(f"[YahooProvider] שגיאה בקריאת ticker.history: {result['error']}")
                return None
            history = result.get('history')
            if history is None or history.empty:
                logger.warning(f"No historical data for {symbol} (period={period}, start={start_date}, end={end_date})")
                return None
            logger.info(f"Retrieved {len(history)} historical records for {symbol} (period={period}, start={start_date}, end={end_date})")
            logger.info(f"Columns: {list(history.columns)}")
            logger.info(f"Sample row: {history.iloc[0].to_dict() if len(history) > 0 else 'EMPTY'}")
            return history
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return None
    """ספק נתונים Yahoo Finance - חינמי ללא הגבלות API"""
    
    def __init__(self, config=None):
        api_key = None
        if config is not None:
            api_keys = config.load_api_keys()
            api_key = api_keys.get("yahoo")
        super().__init__(name="Yahoo Finance", api_key=api_key)
        # Yahoo Finance הוא חינמי אבל עם הגבלות
        self.requests_per_minute = 30   # נמוך יותר
        self.min_request_interval = 2.0  # 2 שניות בין בקשות
        self.cache_ttl = 300  # 5 דקות לנתונים
        self.logger.info("Yahoo Finance provider initialized")
    
    def _fetch_data(self) -> Any:
        """קריאת נתונים כללית - לא בשימוש ישיר"""
        pass
    
    def get_quote(self, symbol: str) -> Optional[QuoteData]:
        """קבלת ציטוט לסימבול כלשהו - גרסה פשוטה"""
        cache_key = f"quote_{symbol}"
        
        try:
            # בדיקת cache
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # rate limiting
            self._rate_limit_check()
            
            # יצירת ticker object פשוט
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            
            # ננסה כמה שיטות לקבלת מחיר
            current_price = None
            
            # שיטה 1: fast_info (החדשה)
            try:
                fast_info = ticker.fast_info
                if hasattr(fast_info, 'last_price'):
                    current_price = float(fast_info.last_price)
                elif hasattr(fast_info, 'lastPrice'):
                    current_price = float(fast_info.lastPrice)
                self.logger.debug(f"Got price from fast_info: {current_price}")
            except Exception as e:
                self.logger.debug(f"fast_info failed: {e}")
            
            # שיטה 2: info אם fast_info לא עבד
            if current_price is None:
                try:
                    info = ticker.info
                    if 'regularMarketPrice' in info and info['regularMarketPrice']:
                        current_price = float(info['regularMarketPrice'])
                    elif 'currentPrice' in info and info['currentPrice']:
                        current_price = float(info['currentPrice'])
                    elif 'price' in info and info['price']:
                        current_price = float(info['price'])
                    self.logger.debug(f"Got price from info: {current_price}")
                except Exception as e:
                    self.logger.debug(f"info failed: {e}")
            
            # שיטה 3: history כפתרון אחרון
            if current_price is None:
                try:
                    history = ticker.history(period="1d")
                    if not history.empty:
                        current_price = float(history['Close'].iloc[-1])
                        self.logger.debug(f"Got price from history: {current_price}")
                except Exception as e:
                    self.logger.debug(f"history failed: {e}")
            
            if current_price is None or current_price <= 0:
                raise ValueError("No valid price data found")
            
            # יצירת QuoteData
            quote = QuoteData(
                symbol=symbol,
                price=current_price,
                timestamp=datetime.now(),
                volume=None,
                change=None,
                change_percent=None
            )
            
            # שמירה ב-cache
            self._set_cache(cache_key, quote)
            
            self._update_status(success=True)
            self.logger.info(f"Retrieved quote for {symbol}: ${current_price:.2f}")
            
            return quote
            
        except Exception as e:
            error_msg = f"Failed to get quote for {symbol}: {str(e)}"
            self._update_status(success=False, error_msg=error_msg)
            self.logger.error(error_msg)
            return None
    
    def get_vix(self) -> Optional[QuoteData]:
        """קבלת נתוני VIX - הפונקציה העיקרית"""
        return self.get_quote("^VIX")
    
    def get_market_data(self) -> Dict[str, QuoteData]:
        """קבלת נתוני שוק רחבים"""
        symbols = {
            "VIX": "^VIX",
            "SPY": "SPY", 
            "QQQ": "QQQ",
            "IWM": "IWM"
        }
        
        market_data = {}
        
        for name, symbol in symbols.items():
            quote = self.get_quote(symbol)
            if quote:
                market_data[name] = quote
        
        return market_data
    
    def get_vix_historical(self, period: str = "1mo") -> Optional[pd.DataFrame]:
        """קבלת נתוני VIX היסטוריים"""
        cache_key = f"vix_historical_{period}"
        
        try:
            # בדיקת cache
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            # rate limiting  
            self._rate_limit_check()
            
            # יצירת ticker לVIX
            vix_ticker = yf.Ticker("^VIX")
            
            # קבלת נתונים היסטוריים
            history = vix_ticker.history(period=period)
            
            if history.empty:
                self.logger.warning("No historical VIX data available")
                return None
            
            # שמירה ב-cache (TTL ארוך יותר להיסטוריה)
            self._cache[cache_key] = (history, datetime.now())
            
            self._update_status(success=True)
            self.logger.debug(f"Retrieved VIX historical data: {len(history)} records")
            
            return history
            
        except Exception as e:
            error_msg = f"Failed to get VIX historical data: {str(e)}"
            self._update_status(success=False, error_msg=error_msg)
            self.logger.error(error_msg)
            return None
    
    def get_multiple_quotes(self, symbols: list) -> Dict[str, QuoteData]:
        """קבלת ציטוטים מרובים ביעילות"""
        quotes = {}
        
        # Yahoo Finance יכול לטפל במספר סימבולים בבת אחת
        try:
            # rate limiting
            self._rate_limit_check()
            
            # הורדת נתונים לכל הסימבולים
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = getattr(tickers.tickers, symbol)
                    history = ticker.history(period="1d", interval="1m")
                    
                    if not history.empty:
                        latest = history.iloc[-1]
                        current_price = float(latest['Close'])
                        volume = int(latest['Volume']) if not pd.isna(latest['Volume']) else None
                        
                        quote = QuoteData(
                            symbol=symbol,
                            price=current_price,
                            timestamp=datetime.now(),
                            volume=volume
                        )
                        
                        quotes[symbol] = quote
                        
                except Exception as e:
                    self.logger.warning(f"Failed to get data for {symbol}: {e}")
                    continue
            
            self._update_status(success=True)
            self.logger.debug(f"Retrieved {len(quotes)} quotes from {len(symbols)} symbols")
            
        except Exception as e:
            error_msg = f"Failed to get multiple quotes: {str(e)}"
            self._update_status(success=False, error_msg=error_msg)
            self.logger.error(error_msg)
        
        return quotes
    
    def test_connection(self) -> bool:
        """בדיקת חיבור ספציפית ל-Yahoo Finance"""
        try:
            # נסיון לקבל SPY כבדיקה (יותר יציב מ-VIX)
            test_quote = self.get_quote("SPY")
            
            if test_quote and test_quote.price > 0:
                self.logger.info("Yahoo Finance connection test successful")
                return True
            else:
                self.logger.error("Yahoo Finance connection test failed - no valid data")
                return False
                
        except Exception as e:
            self.logger.error(f"Yahoo Finance connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """מידע על הספק"""
        return {
            "name": self.name,
            "type": "Free",
            "rate_limit": f"{self.requests_per_minute}/minute",
            "supports": ["stocks", "indices", "VIX", "ETFs"],
            "real_time": False,  # 15-20 minute delay
            "cost": "Free",
            "reliability": "High"
        }
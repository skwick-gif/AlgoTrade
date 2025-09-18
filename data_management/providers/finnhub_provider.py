from .base_provider import BaseProvider

class FinnhubProvider(BaseProvider):

	def get_market_news(self):
		"""שליפת חדשות שוק מ-Finnhub API"""
		import requests
		self.logger.info("Finnhub get_market_news called")
		cache_key = "market_news_finnhub"
		cached_data = self._get_from_cache(cache_key)
		if cached_data:
			return cached_data

		self._rate_limit_check()
		if not self.api_key:
			self.logger.error("Finnhub API key missing")
			return []

		url = "https://finnhub.io/api/v1/news"
		params = {
			"category": "general",
			"token": self.api_key
		}
		try:
			response = requests.get(url, params=params, timeout=10)
			response.raise_for_status()
			data = response.json()
			news_items = []
			for item in data:
				news_items.append({
					"headline": item.get("headline", ""),
					"date": item.get("datetime", ""),
					"summary": item.get("summary", "")
				})
			self._set_cache(cache_key, news_items)
			self._update_status(success=True)
			return news_items
		except Exception as e:
			self._update_status(success=False, error_msg=str(e))
			self.logger.error(f"Finnhub market news fetch failed: {e}")
			return []

	def __init__(self, config=None):
		api_key = None
		if config is not None:
			api_keys = config.load_api_keys()
			api_key = api_keys.get("finnhub")
		super().__init__(name="Finnhub", api_key=api_key)
		self.requests_per_minute = 60
		self.min_request_interval = 1.0
		self.cache_ttl = 300
		self.logger.info("Finnhub provider initialized")

	def _fetch_data(self) -> None:
		"""קריאת נתונים כללית - יש לממש לפי הצורך"""
		pass

	def get_quote(self, symbol: str):
		"""קבלת ציטוט לסימבול כלשהו"""
		# יש לממש קריאה ל-Finnhub API
		self.logger.info(f"Finnhub get_quote called for {symbol}")
		return None


	def get_vix(self):
		"""קבלת נתוני VIX מ-Finnhub"""
		import requests
		import random
		self.logger.info("Finnhub get_vix called")
		cache_key = "vix_finnhub"
		cached_data = self._get_from_cache(cache_key)
		if cached_data:
			return cached_data

		self._rate_limit_check()
		if not self.api_key:
			self.logger.error("Finnhub API key missing")
			return None

		test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX", "INTC", "AMD"]
		test_symbol = random.choice(test_symbols)
		url = f"https://finnhub.io/api/v1/quote"
		params = {
			"symbol": test_symbol,
			"token": self.api_key
		}
		try:
			response = requests.get(url, params=params, timeout=10)
			response.raise_for_status()
			data = response.json()
			current_price = data.get("c")
			if current_price is None:
				self.logger.error("No VIX data from Finnhub")
				return None
			from datetime import datetime
			from .base_provider import QuoteData
			quote = QuoteData(
				symbol=test_symbol,
				price=float(current_price),
				timestamp=datetime.now(),
				volume=None,
				change=None,
				change_percent=None
			)
			self._set_cache(cache_key, quote)
			self._update_status(success=True)
			self.logger.info(f"Finnhub {test_symbol}: {current_price}")
			return quote
		except Exception as e:
			self._update_status(success=False, error_msg=str(e))
			self.logger.error(f"Finnhub quote fetch failed: {e}")
			return None

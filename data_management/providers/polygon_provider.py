from .base_provider import BaseProvider

class PolygonProvider(BaseProvider):

	def __init__(self, config=None):
		api_key = None
		if config is not None:
			api_keys = config.load_api_keys()
			api_key = api_keys.get("polygon")
		super().__init__(name="Polygon", api_key=api_key)
		self.requests_per_minute = 60
		self.min_request_interval = 1.0
		self.cache_ttl = 300
		self.logger.info("Polygon provider initialized")

	def _fetch_data(self) -> None:
		"""קריאת נתונים כללית - יש לממש לפי הצורך"""
		pass

	def get_quote(self, symbol: str):
		"""קבלת ציטוט לסימבול כלשהו"""
		self.logger.info(f"Polygon get_quote called for {symbol}")
		return None


	def get_vix(self):
		"""קבלת נתוני VIX או סימבול רנדומלי מ-Polygon"""
		import requests
		import random
		self.logger.info("Polygon get_vix called")
		cache_key = "vix_polygon"
		cached_data = self._get_from_cache(cache_key)
		if cached_data:
			return cached_data

		self._rate_limit_check()
		if not self.api_key:
			self.logger.error("Polygon API key missing")
			return None

		test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX", "INTC", "AMD"]
		test_symbol = random.choice(test_symbols)
		url = f"https://api.polygon.io/v2/last/trade/{test_symbol}"
		params = {
			"apiKey": self.api_key
		}
		try:
			response = requests.get(url, params=params, timeout=10)
			response.raise_for_status()
			data = response.json()
			last = data.get("results", {})
			price = last.get("price")
			if price is None:
				self.logger.error("No quote data from Polygon")
				return None
			from datetime import datetime
			from .base_provider import QuoteData
			quote = QuoteData(
				symbol=test_symbol,
				price=float(price),
				timestamp=datetime.now(),
				volume=None,
				change=None,
				change_percent=None
			)
			self._set_cache(cache_key, quote)
			self._update_status(success=True)
			self.logger.info(f"Polygon {test_symbol}: {price}")
			return quote
		except Exception as e:
			self._update_status(success=False, error_msg=str(e))
			self.logger.error(f"Polygon quote fetch failed: {e}")
			return None

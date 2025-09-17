from .base_provider import BaseProvider

class FMPProvider(BaseProvider):

	def __init__(self, config=None):
		api_key = None
		if config is not None:
			api_keys = config.load_api_keys()
			api_key = api_keys.get("fmp")
		super().__init__(name="FMP", api_key=api_key)
		self.requests_per_minute = 60
		self.min_request_interval = 1.0
		self.cache_ttl = 300
		self.logger.info("FMP provider initialized")

	def _fetch_data(self) -> None:
		"""קריאת נתונים כללית - יש לממש לפי הצורך"""
		pass

	def get_quote(self, symbol: str):
		"""קבלת ציטוט לסימבול כלשהו"""
		self.logger.info(f"FMP get_quote called for {symbol}")
		return None


	def get_vix(self):
		"""קבלת נתוני VIX או סימבול רנדומלי מ-FMP"""
		import requests
		import random
		self.logger.info("FMP get_vix called")
		cache_key = "vix_fmp"
		cached_data = self._get_from_cache(cache_key)
		if cached_data:
			return cached_data

		self._rate_limit_check()
		if not self.api_key:
			self.logger.error("FMP API key missing")
			return None

		test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX", "INTC", "AMD"]
		test_symbol = random.choice(test_symbols)
		url = f"https://financialmodelingprep.com/api/v3/quote/{test_symbol}"
		params = {
			"apikey": self.api_key
		}
		try:
			response = requests.get(url, params=params, timeout=10)
			response.raise_for_status()
			data = response.json()
			if not data or not isinstance(data, list):
				self.logger.error("No quote data from FMP")
				return None
			quote_data = data[0]
			price = quote_data.get("price")
			if price is None:
				self.logger.error("No price in FMP data")
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
			self.logger.info(f"FMP {test_symbol}: {price}")
			return quote
		except Exception as e:
			self._update_status(success=False, error_msg=str(e))
			self.logger.error(f"FMP quote fetch failed: {e}")
			return None

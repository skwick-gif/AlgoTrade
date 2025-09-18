from .base_provider import BaseProvider

class FREDProvider(BaseProvider):
	def get_economic_events(self, days_ahead=30):
		"""שליפת אירועים כלכליים קרובים (החלטות ריבית, CPI, אבטלה וכו') מ-FRED API"""
		import requests
		from datetime import datetime, timedelta
		if not self.api_key:
			self.logger.error("FRED API key missing")
			return []
		today = datetime.today().date()
		end_date = today + timedelta(days=days_ahead)
		# דוגמה: החלטות ריבית, CPI, אבטלה
		series_ids = [
			("FEDFUNDS", "Fed Rate Decision"),
			("CPIAUCSL", "CPI Release"),
			("UNRATE", "Unemployment Data")
		]
		events = []
		for series_id, event_name in series_ids:
			url = "https://api.stlouisfed.org/fred/series/observations"
			params = {
				"series_id": series_id,
				"api_key": self.api_key,
				"file_type": "json",
				"sort_order": "desc",
				"limit": 2
			}
			try:
				response = requests.get(url, params=params, timeout=10)
				response.raise_for_status()
				data = response.json()
				obs = data.get("observations", [])
				if obs:
					latest = obs[-1]
					date = latest.get("date")
					value = latest.get("value")
					if date and value and value != ".":
						event_date = datetime.strptime(date, "%Y-%m-%d").date()
						if today <= event_date <= end_date:
							events.append({
								"name": event_name,
								"date": date,
								"value": value
							})
			except Exception as e:
				self.logger.error(f"FRED event fetch failed for {series_id}: {e}")
		return events

	def __init__(self, config=None):
		api_key = None
		if config is not None:
			api_keys = config.load_api_keys()
			api_key = api_keys.get("fred")
		super().__init__(name="FRED", api_key=api_key)
		self.requests_per_minute = 60
		self.min_request_interval = 1.0
		self.cache_ttl = 300
		self.logger.info("FRED provider initialized")

	def _fetch_data(self) -> None:
		"""קריאת נתונים כללית - יש לממש לפי הצורך"""
		pass

	def get_quote(self, symbol: str):
		"""קבלת ציטוט לסימבול כלשהו"""
		self.logger.info(f"FRED get_quote called for {symbol}")
		return None


	def get_vix(self):
		"""קבלת נתוני VIX מ-FRED"""
		import requests
		self.logger.info("FRED get_vix called")
		cache_key = "vix_fred"
		cached_data = self._get_from_cache(cache_key)
		if cached_data:
			return cached_data

		self._rate_limit_check()
		if not self.api_key:
			self.logger.error("FRED API key missing")
			return None

		# סדרת VIX ב-FRED: VIXCLS
		url = f"https://api.stlouisfed.org/fred/series/observations"
		params = {
			"series_id": "VIXCLS",
			"api_key": self.api_key,
			"file_type": "json",
			"limit": 1,
			"sort_order": "desc"
		}
		try:
			response = requests.get(url, params=params, timeout=10)
			response.raise_for_status()
			data = response.json()
			observations = data.get("observations", [])
			if not observations:
				self.logger.error("No VIX data from FRED")
				return None
			latest = observations[-1]
			value = latest.get("value")
			date = latest.get("date")
			if value is None or value == ".":
				self.logger.error("Invalid VIX value from FRED")
				return None
			from datetime import datetime
			from .base_provider import QuoteData
			quote = QuoteData(
				symbol="^VIX",
				price=float(value),
				timestamp=datetime.strptime(date, "%Y-%m-%d"),
				volume=None,
				change=None,
				change_percent=None
			)
			self._set_cache(cache_key, quote)
			self._update_status(success=True)
			self.logger.info(f"FRED VIX: {value} on {date}")
			return quote
		except Exception as e:
			self._update_status(success=False, error_msg=str(e))
			self.logger.error(f"FRED VIX fetch failed: {e}")
			return None

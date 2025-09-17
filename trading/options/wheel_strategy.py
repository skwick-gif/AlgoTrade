
from analytics import performance
from core.logger import logger
from data_management.data_router import DataRouter

class WheelStrategy:
	def __init__(self, account=None, ibkr_connector=None):
		self.account = account
		self.ibkr = ibkr_connector
		self.data_router = DataRouter()
		self.vix_value = None
		logger.info("WheelStrategy initialized for account %s", account)

	def update_vix(self):
		"""עדכון ערך VIX מהמערכת שלך"""
		vix_data = self.data_router.get_vix()
		self.vix_value = getattr(vix_data, 'price', None)
		logger.info(f"VIX value updated: {self.vix_value}")
		return self.vix_value

	def should_trade(self):
		"""דוגמה: החלטה האם לסחור לפי ערך VIX"""
		vix = self.update_vix()
		# דוגמה: לא לסחור אם VIX גבוה מ-30
		if vix is not None and vix > 30:
			logger.warning("VIX too high, skipping trade.")
			return False
		return True

	def execute(self, symbol):
		"""הפעלת אסטרטגיית WHEEL בפועל עבור סימול מסוים"""
		if not self.should_trade():
			logger.info("Trade skipped due to VIX filter.")
			return "המסחר בוטל עקב פילטר VIX"
		logger.info(f"Executing WHEEL strategy for symbol: {symbol}")
		# כאן תשתלב הלוגיקה מהתיק של thetagang, לדוג' פתיחת פוזיציה על symbol
		# לדוגמה:
		# position = self.ibkr.open_wheel_position(symbol)
		# return f"פוזיציה נפתחה עבור {symbol}"
		return f"בוצעה פעולה על {symbol}"

	# אפשר להוסיף פונקציות נוספות לגלגול פוזיציות, ניהול אופציות וכו'

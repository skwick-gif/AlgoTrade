
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MarketNewsWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.setup_ui()
	def setup_ui(self):
		layout = QVBoxLayout(self)
		header = QFrame()
		header.setStyleSheet("background-color: white; border-bottom: 1px solid #e5e7eb; padding: 16px;")
		header_layout = QHBoxLayout(header)
		title = QLabel("📰 Market News")
		title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
		title.setStyleSheet("color: #1f2937;")
		header_layout.addWidget(title)

		# אינדיקציה ויזואלית (עיגול ירוק/אדום)
		self.status_indicator = QLabel()
		self.status_indicator.setFixedSize(16, 16)
		self.status_indicator.setStyleSheet("border-radius: 8px; background: #d1d5db; margin-left: 8px;")
		header_layout.addStretch()
		header_layout.addWidget(self.status_indicator)
		layout.addWidget(header)

		# שליפת חדשות אמיתיות דרך DataRouter
		news_items = []
		provider_ok = False
		error_msg = None
		import sys
		import sys
		try:
			from data_management.data_router import DataRouter
			print("[MarketNewsWidget] Loading market news...", file=sys.stderr)
			router = DataRouter()
			if hasattr(router, 'get_market_news'):
				news_items = router.get_market_news()
				print(f"[MarketNewsWidget] news_items: {news_items}", file=sys.stderr)
				provider_ok = True
			else:
				print("[MarketNewsWidget] DataRouter missing get_market_news", file=sys.stderr)
				news_items = []
				provider_ok = False
		except Exception as e:
			news_items = []
			error_msg = str(e)
			provider_ok = False
			print(f"[MarketNewsWidget] Exception: {error_msg}", file=sys.stderr)

		# הבטחת הצגת הריבוע גם במקרה חריגה
		if not provider_ok and not news_items:
			msg = QLabel(f"News widget error: {error_msg if error_msg else 'Unknown error'}")
			msg.setStyleSheet("color: #dc2626; font-size: 12px; margin-top: 8px;")
			layout.addWidget(msg)

		# עדכון צבע אינדיקציה
		if provider_ok:
			self.status_indicator.setStyleSheet("border-radius: 8px; background: #22c55e; margin-left: 8px;")  # ירוק
		else:
			self.status_indicator.setStyleSheet("border-radius: 8px; background: #dc2626; margin-left: 8px;")  # אדום

		if provider_ok and news_items and len(news_items) > 0:
			from datetime import datetime
			print(f"[MarketNewsWidget] Rendering {len(news_items)} news items", file=sys.stderr)
			for item in news_items:
				box = QFrame()
				box.setStyleSheet("background: #f9fafb; border-radius: 8px; padding: 8px; margin-bottom: 6px;")
				box_layout = QHBoxLayout(box)
				lbl = QLabel(item.get("headline", ""))
				lbl.setFont(QFont("Arial", 10))
				box_layout.addWidget(lbl)
				box_layout.addStretch()
				# המרת date ממספר (timestamp) למחרוזת קריאה
				date_val = item.get("date", "")
				if isinstance(date_val, int):
					date_str = datetime.fromtimestamp(date_val).strftime("%Y-%m-%d %H:%M")
				else:
					date_str = str(date_val)
				lbl2 = QLabel(date_str)
				lbl2.setStyleSheet("color: #6b7280; font-size: 11px;")
				box_layout.addWidget(lbl2)
				lbl3 = QLabel(item.get("summary", ""))
				lbl3.setStyleSheet("font-size: 11px; font-weight: bold; color: #1976d2;")
				box_layout.addWidget(lbl3)
				layout.addWidget(box)
		elif provider_ok:
			print("[MarketNewsWidget] No market news available.", file=sys.stderr)
			msg = QLabel("No market news available.")
			msg.setStyleSheet("color: #6b7280; font-size: 12px; margin-top: 8px;")
			layout.addWidget(msg)
		else:
			print(f"[MarketNewsWidget] No connection to Market News provider. {error_msg if error_msg else ''}", file=sys.stderr)
			msg = QLabel(f"No connection to Market News provider. {error_msg if error_msg else ''}")
			msg.setStyleSheet("color: #dc2626; font-size: 12px; margin-top: 8px;")
			layout.addWidget(msg)

		layout.addStretch()

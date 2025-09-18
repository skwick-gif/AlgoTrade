
from PyQt6 import QtWidgets, QtCore
# אפשר להחליף ל-FinnhubProvider או FREDProvider לפי API


from dashboard.market_news_widget import MarketNewsWidget
from dashboard.earnings_widget import EarningsWidget
from dashboard.economic_events_widget import EconomicEventsWidget

class OverviewBoxes(QtWidgets.QWidget):
	def __init__(self, parent=None):
		import sys
		super().__init__(parent)
		layout = QtWidgets.QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(16)
		print("[OverviewBoxes] Creating MarketNewsWidget", file=sys.stderr)
		self.news = MarketNewsWidget()
		print("[OverviewBoxes] Adding MarketNewsWidget to layout", file=sys.stderr)
		layout.addWidget(self.news)
		print("[OverviewBoxes] Creating EarningsWidget", file=sys.stderr)
		self.earnings = EarningsWidget()
		print("[OverviewBoxes] Adding EarningsWidget to layout", file=sys.stderr)
		layout.addWidget(self.earnings)
		print("[OverviewBoxes] Creating EconomicEventsWidget", file=sys.stderr)
		self.economic = EconomicEventsWidget()
		print("[OverviewBoxes] Adding EconomicEventsWidget to layout", file=sys.stderr)
		layout.addWidget(self.economic)

# דוגמה לשימוש:
if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	win = QtWidgets.QWidget()
	layout = QtWidgets.QVBoxLayout(win)
	boxes = OverviewBoxes()
	layout.addWidget(boxes)
	win.show()
	app.exec()


from PyQt6 import QtWidgets
from ..components.sidebar import make_sidebar

class Tab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(make_sidebar(['Active List', 'Create List', 'Price Alerts', 'Volume Alerts', 'Technical Alerts', 'History']))
        content = QtWidgets.QLabel("Content for Watchlist Tab.Py")
        content.setStyleSheet("color:#6b7280")
        layout.addWidget(content, 1)

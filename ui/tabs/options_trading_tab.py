
from PyQt6 import QtWidgets
from ..components.sidebar import make_sidebar

class Tab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(make_sidebar(['Strategy Builder', 'Active Trades', 'Strategy 1-4', 'Backtest', 'Settings']))
        content = QtWidgets.QLabel("Content for Options Trading Tab.Py")
        content.setStyleSheet("color:#6b7280")
        layout.addWidget(content, 1)


from PyQt6 import QtWidgets
from ..components.sidebar import make_sidebar

class Tab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        sidebar_items = [
            'Strategy Builder',
            'Active Trades',
            'Strategy 1-4',
            'Strategy Monitor',
            'Backtest',
            'Settings'
        ]
    sidebar = make_sidebar(sidebar_items)
    print("Sidebar type:", type(sidebar))
    layout.addWidget(sidebar)
        content = QtWidgets.QLabel("Content for Options Trading Tab.Py")
        content.setStyleSheet("color:#6b7280")
        layout.addWidget(content, 1)

        # Add debug logging for button clicks
        def on_sidebar_click(item):
            print(f"Sidebar button clicked: {item.text()}")

        # Connect signal for QListWidget
        if hasattr(sidebar, 'itemClicked'):
            sidebar.itemClicked.connect(on_sidebar_click)

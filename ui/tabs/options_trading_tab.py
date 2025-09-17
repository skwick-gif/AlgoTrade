
from PyQt6 import QtWidgets
from ..components.sidebar import make_sidebar


class WheelStrategyWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        from trading.options.wheel_strategy import WheelStrategy
        from data_management.data_router import DataRouter
        self.strategy = WheelStrategy()
        self.data_router = DataRouter()

        layout = QtWidgets.QVBoxLayout()

        # כותרת
        title_label = QtWidgets.QLabel("Wheel Strategy - ממשק מלא")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # שדה סימול
        symbol_layout = QtWidgets.QHBoxLayout()
        symbol_label = QtWidgets.QLabel("סימול מניה:")
        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setPlaceholderText("הזן סימול (למשל AAPL)")
        symbol_layout.addWidget(symbol_label)
        symbol_layout.addWidget(self.symbol_input)
        layout.addLayout(symbol_layout)

        # ערך VIX
        self.vix_label = QtWidgets.QLabel("VIX: טוען...")
        layout.addWidget(self.vix_label)

        # סטטוס אסטרטגיה
        self.status_label = QtWidgets.QLabel("סטטוס: טוען...")
        layout.addWidget(self.status_label)

        # כפתור פעולה
        self.action_btn = QtWidgets.QPushButton("בצע פעולה (פתח פוזיציה)")
        self.action_btn.clicked.connect(self.on_action)
        layout.addWidget(self.action_btn)

        # אזור הודעות
        self.message_label = QtWidgets.QLabel("")
        self.message_label.setStyleSheet("color: red;")
        layout.addWidget(self.message_label)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        # משיכת ערך VIX
        try:
            vix_value = self.data_router.get_vix()
            self.vix_label.setText(f"VIX: {vix_value}")
        except Exception as e:
            self.vix_label.setText("VIX: שגיאה בטעינה")

        # סטטוס אסטרטגיה
        try:
            status = self.strategy.get_status()
            self.status_label.setText(f"סטטוס: {status}")
        except Exception as e:
            self.status_label.setText("סטטוס: שגיאה")

    def on_action(self):
        symbol = self.symbol_input.text().strip()
        if not symbol:
            self.message_label.setText("נא להזין סימול מניה.")
            return
        try:
            result = self.strategy.execute(symbol)
            self.message_label.setText(f"בוצע: {result}")
            self.refresh()
        except Exception as e:
            self.message_label.setText(f"שגיאה: {str(e)}")

class Tab(QtWidgets.QWidget):
    def set_content_by_name(self, name):
        if name == 'WHEEL':
            self.content_area.setCurrentWidget(self.wheel_widget)
        else:
            self.content_area.setCurrentIndex(0)
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.content_area = QtWidgets.QStackedWidget()
        default_content = QtWidgets.QLabel("Select a strategy from the sidebar.")
        default_content.setStyleSheet("color:#6b7280")
        self.content_area.addWidget(default_content)
        self.wheel_widget = WheelStrategyWidget()
        self.content_area.addWidget(self.wheel_widget)
        layout.addWidget(self.content_area, 1)

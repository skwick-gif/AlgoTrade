from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class EarningsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QFrame()
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #e5e7eb; padding: 16px;")
        header_layout = QHBoxLayout(header)
        title = QLabel("💰 Earnings")
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

        # שליפת דוחות אמיתיים דרך DataRouter
        earnings_items = []
        provider_ok = False
        error_msg = None
        try:
            from data_management.data_router import DataRouter
            router = DataRouter()
            if hasattr(router, 'get_earnings'):
                earnings_items = router.get_earnings()
                provider_ok = True
            else:
                earnings_items = []
                provider_ok = False
        except Exception as e:
            earnings_items = []
            error_msg = str(e)
            provider_ok = False

        # עדכון צבע אינדיקציה
        if provider_ok:
            self.status_indicator.setStyleSheet("border-radius: 8px; background: #22c55e; margin-left: 8px;")  # ירוק
        else:
            self.status_indicator.setStyleSheet("border-radius: 8px; background: #dc2626; margin-left: 8px;")  # אדום

        if provider_ok and earnings_items and len(earnings_items) > 0:
            for item in earnings_items:
                box = QFrame()
                box.setStyleSheet("background: #f9fafb; border-radius: 8px; padding: 8px; margin-bottom: 6px;")
                box_layout = QHBoxLayout(box)
                lbl = QLabel(item.get("company", ""))
                lbl.setFont(QFont("Arial", 10))
                box_layout.addWidget(lbl)
                box_layout.addStretch()
                lbl2 = QLabel(item.get("date", ""))
                lbl2.setStyleSheet("color: #6b7280; font-size: 11px;")
                box_layout.addWidget(lbl2)
                lbl3 = QLabel(item.get("result", ""))
                lbl3.setStyleSheet("font-size: 11px; font-weight: bold; color: #1976d2;")
                box_layout.addWidget(lbl3)
                layout.addWidget(box)
        elif provider_ok:
            msg = QLabel("No earnings reports available.")
            msg.setStyleSheet("color: #6b7280; font-size: 12px; margin-top: 8px;")
            layout.addWidget(msg)
        else:
            msg = QLabel(f"No connection to Earnings provider. {error_msg if error_msg else ''}")
            msg.setStyleSheet("color: #dc2626; font-size: 12px; margin-top: 8px;")
            layout.addWidget(msg)

        layout.addStretch()

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

class GenericTab(QtWidgets.QWidget):
    def __init__(self, tab_name, sidebar_buttons):
        super().__init__()
        self.tab_name = tab_name
        self.sidebar_buttons = sidebar_buttons
        # יצירת layout ראשי
        self.layout = QtWidgets.QVBoxLayout(self)
        # כותרת
        # הצגת כותרת רק אם לא מדובר ב-Overview בדשבורד
        if not (tab_name == 'Dashboard'):
            self.title_label = QtWidgets.QLabel(f"{tab_name}")
            self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976d2; margin: 10px;")
            self.layout.addWidget(self.title_label)
        # אזור תוכן
        self.content_area = QtWidgets.QStackedWidget()
        self.button_to_widget = {}
        # יצירת widget לכל כפתור בסיידבר
        for btn_name in sidebar_buttons:
            widget = QtWidgets.QLabel(f"תוכן עבור {tab_name} / {btn_name}")
            widget.setStyleSheet("font-size: 15px; color: #333;")
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_area.addWidget(widget)
            self.button_to_widget[btn_name] = widget
        self.layout.addWidget(self.content_area, 1)
        # הצגת תוכן ראשוני
        if sidebar_buttons:
            self.set_content_by_name(sidebar_buttons[0])

    def set_content_by_name(self, name):
        """מעבר לתוכן לפי שם כפתור"""
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"{self.tab_name} - {name}")
        # טיפול מיוחד ב-Dashboard Overview
        if self.tab_name == 'Dashboard' and name == 'Overview':
            # ניקוי תוכן קודם
            self.content_area.hide()
            # הצגת OverviewBoxes רק ב-Overview
            if not hasattr(self, 'overview_boxes'):
                from dashboard.overview import OverviewBoxes
                self.overview_boxes = OverviewBoxes()
                self.layout.addWidget(self.overview_boxes)
            self.overview_boxes.show()
            # הסתרה של כל widget אחר
            for btn_name, widget in self.button_to_widget.items():
                widget.hide()
        else:
            # הסתרת OverviewBoxes אם קיים
            if hasattr(self, 'overview_boxes'):
                self.overview_boxes.hide()
            # הצגת תוכן רגיל
            self.content_area.show()
            if name in self.button_to_widget:
                widget = self.button_to_widget[name]
                widget.show()
                self.content_area.setCurrentWidget(widget)

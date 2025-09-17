from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

class GenericTab(QtWidgets.QWidget):
    def __init__(self, tab_name, sidebar_buttons):
        super().__init__()
        self.tab_name = tab_name
        self.sidebar_buttons = sidebar_buttons
        layout = QtWidgets.QVBoxLayout(self)
        self.content_area = QtWidgets.QStackedWidget()
        self.button_to_widget = {}
        # יצירת widget לכל כפתור בסיידבר
        for btn_name in sidebar_buttons:
            widget = QtWidgets.QLabel(f"תוכן עבור {tab_name} / {btn_name}")
            widget.setStyleSheet("font-size: 15px; color: #333;")
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_area.addWidget(widget)
            self.button_to_widget[btn_name] = widget
        layout.addWidget(self.content_area, 1)
    def set_content_by_name(self, name):
        if name in self.sidebar_buttons:
            idx = self.sidebar_buttons.index(name)
            self.content_area.setCurrentIndex(idx)
        else:
            self.content_area.setCurrentIndex(0)

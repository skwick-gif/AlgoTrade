
from PyQt6 import QtWidgets
from ..components.sidebar import make_sidebar

class Tab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        sidebar_items = ['Performance', 'Reports', 'Trade History', 'Risk Analysis', 'Charts', 'Export']
        self.sidebar_buttons = []
        sidebar_widget = QtWidgets.QWidget()
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar_widget)
        for btn_name in sidebar_items:
            btn = QtWidgets.QPushButton(btn_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=btn_name, btn_ref=btn: self.on_sidebar_btn_clicked(name, btn_ref))
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)
        layout.addWidget(sidebar_widget)
        self.content_label = QtWidgets.QLabel("Content for Analytics Tab.Py")
        self.content_label.setStyleSheet("color:#6b7280")
        layout.addWidget(self.content_label, 1)

    def on_sidebar_btn_clicked(self, name, btn_ref):
        for btn in self.sidebar_buttons:
            btn.setChecked(False)
        btn_ref.setChecked(True)
        self.content_label.setText(f"Content for {name} will be displayed here")

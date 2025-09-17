from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

class IBKRLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IBKR Login")
        self.setFixedSize(320, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Account Number
        acc_layout = QHBoxLayout()
        acc_label = QLabel("Account Number:")
        self.acc_input = QLineEdit()
        self.acc_input.setMinimumHeight(28)
        acc_font = self.acc_input.font()
        acc_font.setPointSize(8)
        self.acc_input.setFont(acc_font)
        acc_layout.addWidget(acc_label)
        acc_layout.addWidget(self.acc_input)
        layout.addLayout(acc_layout)

        # Password
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setMinimumHeight(28)
        pass_font = self.pass_input.font()
        pass_font.setPointSize(8)
        self.pass_input.setFont(pass_font)
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)
        layout.addLayout(pass_layout)

        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        self.port_input = QLineEdit()
        self.port_input.setMinimumHeight(28)
        port_font = self.port_input.font()
        port_font.setPointSize(8)
        self.port_input.setFont(port_font)
        self.port_input.setPlaceholderText("e.g. 7497")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        # Login Button
        self.login_btn = QPushButton("Login")
        self.login_btn.setDefault(True)
        layout.addWidget(self.login_btn)

        # Cancel Button
        self.cancel_btn = QPushButton("Cancel")
        layout.addWidget(self.cancel_btn)

        self.login_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_credentials(self):
        return {
            'account': self.acc_input.text(),
            'password': self.pass_input.text(),
            'port': self.port_input.text()
        }

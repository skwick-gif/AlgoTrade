"""
ui/components/ibkr_status.py - IBKR connection status
מתבסס על הארטיפקט React המקורי
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen


class WifiIcon(QWidget):
    """אייקון Wifi/WifiOff - מדמה lucide-react icons"""
    
    def __init__(self, connected=True, parent=None):
        super().__init__(parent)
        self.connected = connected
        self.setFixedSize(16, 16)  # w-4 h-4
        
    def set_connected(self, connected):
        """עדכון מצב החיבור"""
        if self.connected != connected:
            self.connected = connected
            self.update()
            
    def paintEvent(self, event):
        """ציור אייקון Wifi"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # צבע לפי מצב החיבור
        color = QColor('#22c55e') if self.connected else QColor('#ef4444')  # ירוק/אדום
        pen = QPen(color)
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        if self.connected:
            # Wifi מחובר - 3 קשתות
            center_x, center_y = 8, 12
            
            # קשת חיצונית
            painter.drawArc(2, 6, 12, 12, 30 * 16, 120 * 16)
            # קשת אמצעית
            painter.drawArc(4, 8, 8, 8, 30 * 16, 120 * 16)
            # קשת פנימית
            painter.drawArc(6, 10, 4, 4, 30 * 16, 120 * 16)
            # נקודה במרכז
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(7, 13, 2, 2)
        else:
            # WifiOff - קו חוצה
            painter.drawLine(2, 2, 14, 14)
            # קשתות חצויות
            pen.setColor(QColor('#9ca3af'))  # אפור
            painter.setPen(pen)
            painter.drawArc(2, 6, 12, 12, 30 * 16, 60 * 16)
            painter.drawArc(4, 8, 8, 8, 60 * 16, 60 * 16)


class StatusDot(QWidget):
    """נקודת סטטוס עגולה"""
    
    def __init__(self, color='blue', parent=None):
        super().__init__(parent)
        self.color_name = color
        self.setFixedSize(8, 8)  # w-2 h-2
        
    def set_color(self, color):
        """עדכון צבע הנקודה"""
        if self.color_name != color:
            self.color_name = color
            self.update()
            
    def paintEvent(self, event):
        """ציור הנקודה"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # בחירת צבע
        if self.color_name == 'blue':
            color = QColor('#3b82f6')  # text-blue-500
        elif self.color_name == 'orange':
            color = QColor('#f97316')  # text-orange-500
        else:
            color = QColor('#6b7280')  # text-gray-500
            
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 8, 8)


class IBKRStatusWidget(QWidget):
    """רכיב IBKR Status - מצב חיבור + סוג חשבון"""
    
    connection_changed = pyqtSignal(bool)  # True/False לחיבור
    account_changed = pyqtSignal(str)      # 'paper'/'live'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._connected = False      # כברירת מחדל לא מחובר
        self._account_type = ''      # אין סוג חשבון עד התחברות
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        """הגדרת הממשק"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)  # space-x-2
        
        # תווית "IBKR"
        self.ibkr_label = QLabel("IBKR")
        self.ibkr_label.setObjectName("ibkrLabel")
        
        # הגדרת פונט
        font = QFont()
        font.setPointSize(10)  # text-sm
        self.ibkr_label.setFont(font)
        self.ibkr_label.setStyleSheet("color: #4b5563;")  # text-gray-600
        
        layout.addWidget(self.ibkr_label)
        
        # Container לסטטוס
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(4)  # space-x-1
        
        # אייקון Wifi
        self.wifi_icon = WifiIcon(connected=self._connected)
        status_layout.addWidget(self.wifi_icon)
        
        # Container לנקודה וטקסט חשבון
        account_widget = QWidget()
        account_layout = QHBoxLayout(account_widget)
        account_layout.setContentsMargins(0, 0, 0, 0)
        account_layout.setSpacing(4)  # space-x-1
        
        # נקודת סטטוס
        self.status_dot = StatusDot(color='blue')
        account_layout.addWidget(self.status_dot)
        
        # טקסט סוג חשבון
        self.account_label = QLabel(self._account_type.upper())
        self.account_label.setObjectName("accountLabel")
        
        # הגדרת פונט לסוג חשבון
        account_font = QFont()
        account_font.setPointSize(9)  # text-xs
        self.account_label.setFont(account_font)
        
        account_layout.addWidget(self.account_label)
        
        status_layout.addWidget(account_widget)
        layout.addWidget(status_widget)
        
        # מניעת התרחבות
        self.setSizePolicy(
            self.sizePolicy().Policy.Fixed,
            self.sizePolicy().Policy.Fixed
        )
        
    @property
    def connected(self):
        """מצב החיבור הנוכחי"""
        return self._connected
        
    @property
    def account_type(self):
        """סוג החשבון הנוכחי"""
        return self._account_type
        
    def set_connection_status(self, connected):
        """עדכון מצב החיבור"""
        if self._connected != connected:
            self._connected = connected
            self.update_display()
            self.connection_changed.emit(connected)
            
    def set_account_type(self, account_type):
        """עדכון סוג החשבון"""
        if account_type not in ['paper', 'live']:
            return
            
        if self._account_type != account_type:
            self._account_type = account_type
            self.update_display()
            self.account_changed.emit(account_type)
            
    def update_display(self):
        """עדכון התצוגה לפי המצב"""
        # עדכון אייקון Wifi
        self.wifi_icon.set_connected(self._connected)

        # עדכון נקודת סטטוס וצבע טקסט
        if not self._connected:
            self.status_dot.set_color('gray')
            text_color = '#6b7280'  # אפור
            self.account_label.setText("")
        else:
            if self._account_type == 'paper':
                self.status_dot.set_color('blue')
                text_color = '#2563eb'  # כחול
            else:
                self.status_dot.set_color('orange')
                text_color = '#ea580c'  # כתום
            self.account_label.setText(self._account_type.upper())
        self.account_label.setStyleSheet(f"color: {text_color};")
        
    def toggle_connection(self):
        """החלפת מצב חיבור (לבדיקות)"""
        self.set_connection_status(not self._connected)
        
    def toggle_account_type(self):
        """החלפת סוג חשבון (לבדיקות)"""
        new_type = 'live' if self._account_type == 'paper' else 'paper'
        self.set_account_type(new_type)
        
    def mousePressEvent(self, event):
        """לחיצה על הרכיב - פתיחת דיאלוג התחברות ל-IBKR"""
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                from ui.dialogs.ibkr_login_dialog import IBKRLoginDialog
                from brokers.interactive_brokers import IBKRConnector
                dlg = IBKRLoginDialog(self)
                if dlg.exec():
                    creds = dlg.get_credentials()
                    # יצירת מחבר (אפשר לשמור אותו ברמת אפליקציה בהמשך)
                    if not hasattr(self, '_ibkr_connector'):
                        self._ibkr_connector = IBKRConnector()
                    connector = self._ibkr_connector
                    # ניסיון התחברות
                    connected = connector.connect(
                        host='127.0.0.1',
                        port=creds['port'] or 7497,
                        account=creds['account'],
                        password=creds['password']
                    )
                    self.set_connection_status(connected)
                    # קביעת סוג חשבון לפי account
                    if connected:
                        acc_type = 'live' if creds['account'].startswith('U') else 'paper'
                        self.set_account_type(acc_type)
                    else:
                        from PyQt6.QtWidgets import QMessageBox
                        err = connector.get_status().get('error', 'Unknown error')
                        QMessageBox.critical(self, "IBKR Connection Failed", f"Failed to connect to IBKR:\n{err}")
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "IBKR Dialog Error", f"Failed to open IBKR login dialog:\n{e}")
        elif event.button() == Qt.MouseButton.RightButton:
            self.toggle_account_type()
        super().mousePressEvent(event)


class IBKRStatusContainer(QWidget):
    """Container מלא ל-IBKR Status עם תכונות נוספות"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connection_monitor()
        
    def setup_ui(self):
        """הגדרת הממשק המלא"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # רכיב הבסיס
        self.ibkr_status = IBKRStatusWidget()
        layout.addWidget(self.ibkr_status)
        
        # חיבור לאירועים
        self.ibkr_status.connection_changed.connect(self.on_connection_changed)
        self.ibkr_status.account_changed.connect(self.on_account_changed)
        
    def setup_connection_monitor(self):
        """הגדרת מעקב חיבור"""
        # טיימר לבדיקת חיבור (בעתיד - יתחבר למערכת IBKR אמיתית)
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        # לא מפעילים עדיין - רק כשיש חיבור אמיתי
        
    def check_connection(self):
        """בדיקת מצב החיבור (לעתיד)"""
        # כאן יתבצע בדיקה אמיתית של חיבור IBKR
        pass
        
    def on_connection_changed(self, connected):
        """טיפול בשינוי מצב חיבור"""
        status = "Connected" if connected else "Disconnected"
        print(f"IBKR Status: {status}")
        
    def on_account_changed(self, account_type):
        """טיפול בשינוי סוג חשבון"""
        print(f"Account type changed to: {account_type.upper()}")
        
    def get_status(self):
        """קבלת מצב מלא"""
        return {
            'connected': self.ibkr_status.connected,
            'account_type': self.ibkr_status.account_type
        }
        
    def set_connection_status(self, connected):
        """הגדרת מצב חיבור"""
        self.ibkr_status.set_connection_status(connected)
        
    def set_account_type(self, account_type):
        """הגדרת סוג חשבון"""
        self.ibkr_status.set_account_type(account_type)


# Export
__all__ = ['IBKRStatusWidget', 'IBKRStatusContainer', 'WifiIcon', 'StatusDot']
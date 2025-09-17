"""
ui/components/vix_gauge.py - VIX Display פשוט עם נתונים אמיתיים
גרסה פשוטה בלי ציור מורכב - רק טקסט
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from core.logger import get_logger


class VixDataFetcher(QThread):
    """Thread נפרד לשליפת נתוני VIX"""
    data_fetched = pyqtSignal(float)  # VIX value
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self, data_router):
        super().__init__()
        self.logger = get_logger("VixDataFetcher")
        self.should_run = True
        self.data_router = data_router

    def run(self):
        """שליפת נתוני VIX"""
        try:
            vix_data = self.data_router.get_vix()
            if vix_data and hasattr(vix_data, 'price') and vix_data.price:
                self.logger.debug(f"Fetched VIX: {vix_data.price}")
                self.data_fetched.emit(float(vix_data.price))
            else:
                self.error_occurred.emit("No VIX data available")
        except Exception as e:
            error_msg = f"Failed to fetch VIX data: {str(e)}"
            self.logger.error(error_msg)
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            self.error_occurred.emit(error_msg)

    def stop(self):
        """עצירת Thread"""
        self.should_run = False
        self.quit()
        self.wait()


class VixGaugeWidget(QWidget):
    """רכיב VIX פשוט עם נתונים אמיתיים מ-Yahoo Finance"""
    
    value_changed = pyqtSignal(float)
    data_error = pyqtSignal(str)
    
    def __init__(self, data_router, parent=None):
        super().__init__(parent)
        self._vix_value = None  # ללא ערך ברירת מחדל - רק נתונים אמיתיים
        self._is_loading = False
        self.logger = get_logger("VixGauge")
        self.data_router = data_router
        self.data_fetcher = None
        self.setup_ui()
        self.setup_data_timer()
        self.fetch_vix_data()
        
    def setup_ui(self):
        """הגדרת הממשק - הכל בשורה אחת"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # תווית VIX
        self.vix_label = QLabel("VIX")
        self.vix_label.setObjectName("vixLabel")
        font = QFont()
        font.setPointSize(10)
        self.vix_label.setFont(font)
        self.vix_label.setStyleSheet("color: #6b7280;")
        layout.addWidget(self.vix_label)

        # ערך VIX
        self.value_label = QLabel("--")
        self.value_label.setObjectName("vixValue")
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet("color: #6b7280;")
        layout.addWidget(self.value_label)

        # מצב VIX
        self.status_label = QLabel("LOADING")
        self.status_label.setObjectName("vixStatus")
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(self.status_label)

        
    def setup_data_timer(self):
        """הגדרת טיימר לעדכון נתונים"""
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.fetch_vix_data)
        # עדכון כל דקה (60,000 מילישניות)
        self.data_timer.start(60000)
        
    def fetch_vix_data(self):
        """שליפת נתוני VIX בthread נפרד"""
        if self._is_loading:
            return  # כבר טוען
        self._is_loading = True
        self.vix_label.setText("VIX...")
        self.vix_label.setStyleSheet("color: #3b82f6;")  # כחול
        # יצירת thread חדש עם data_router
        self.data_fetcher = VixDataFetcher(self.data_router)
        self.data_fetcher.data_fetched.connect(self.on_vix_data_received)
        self.data_fetcher.error_occurred.connect(self.on_vix_error)
        self.data_fetcher.finished.connect(self.on_fetch_finished)
        self.data_fetcher.start()
        
    @pyqtSlot(float)
    def on_vix_data_received(self, vix_value):
        """קבלת נתוני VIX מוצלחת"""
        self.logger.info(f"Received VIX value: {vix_value}")
        self.set_vix_value(vix_value)
        
    @pyqtSlot(str)
    def on_vix_error(self, error_message):
        """שגיאה בשליפת נתונים"""
        self.logger.error(f"VIX data error: {error_message}")
        self.data_error.emit(error_message)
        
        # עדכון UI - מצב שגיאה
        self.vix_label.setText("VIX!")
        self.vix_label.setStyleSheet("color: #ef4444;")
        self.value_label.setText("NA")
        self.value_label.setStyleSheet("color: #ef4444;")
        self.status_label.setText("NA")
        
    @pyqtSlot()
    def on_fetch_finished(self):
        """סיום שליפת נתונים"""
        self._is_loading = False
        self.vix_label.setText("VIX")
        self.vix_label.setStyleSheet("color: #6b7280;")  # חזרה לאפור
        
    @property
    def vix_value(self):
        """ערך VIX הנוכחי"""
        return self._vix_value
        
    def set_vix_value(self, value):
        """עדכון ערך VIX"""
        if value is None:
            self.value_label.setText("NA")
            self.value_label.setStyleSheet("color: #ef4444;")
            self.status_label.setText("NA")
            return
        if value == self._vix_value:
            return
        self._vix_value = max(0, min(100, value))
        self.value_label.setText(f"{self._vix_value:.1f}")
        self.value_label.setStyleSheet(f"color: {self.get_vix_color(self._vix_value)};")
        self.status_label.setText(self.get_vix_label(self._vix_value))
        self.value_changed.emit(self._vix_value)
        
    def get_vix_color(self, vix):
        """קבלת צבע לפי ערך VIX"""
        if vix < 20:
            return '#22c55e'  # ירוק
        elif vix < 30:
            return '#f59e0b'  # כתום
        else:
            return '#ef4444'  # אדום
            
    def get_vix_label(self, vix):
        """קבלת תווית מצב"""
        if vix < 12:
            return 'LOW'
        elif vix < 20:
            return 'NORMAL'
        elif vix < 30:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    def stop_data_updates(self):
        """עצירת עדכוני נתונים (לסגירת אפליקציה)"""
        if self.data_timer:
            self.data_timer.stop()
            
        if self.data_fetcher and self.data_fetcher.isRunning():
            self.data_fetcher.stop()
            
        self.logger.info("VIX data updates stopped")
        
    def closeEvent(self, event):
        """סגירת הרכיב"""
        self.stop_data_updates()
        super().closeEvent(event)


# Export
__all__ = ['VixGaugeWidget', 'VixDataFetcher']
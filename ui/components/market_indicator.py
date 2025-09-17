"""
ui/components/market_indicator.py - Market Regime indicator
מתבסס על הארטיפקט React המקורי
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPainter, QColor, QBrush, QPen
from PyQt6.QtSvg import QSvgRenderer
import io


class TrendingIcon(QWidget):
    """אייקון TrendingUp/TrendingDown - מדמה lucide-react icons"""
    
    def __init__(self, is_up=True, parent=None):
        super().__init__(parent)
        self.is_up = is_up
        self.setFixedSize(16, 16)  # w-4 h-4
        
    def set_direction(self, is_up):
        """שינוי כיוון הטרנד"""
        if self.is_up != is_up:
            self.is_up = is_up
            self.update()
        
    def paintEvent(self, event):
        """ציור האייקון"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # צבע לפי כיוון
        color = QColor('#22c55e') if self.is_up else QColor('#ef4444')  # ירוק/אדום
        pen = QPen(color)
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        if self.is_up:
            # TrendingUp - קו עולה עם חץ
            # קו עיקרי
            painter.drawLine(3, 13, 13, 3)
            # חץ
            painter.drawLine(13, 3, 10, 3)
            painter.drawLine(13, 3, 13, 6)
        else:
            # TrendingDown - קו יורד עם חץ
            # קו עיקרי
            painter.drawLine(3, 3, 13, 13)
            # חץ
            painter.drawLine(13, 13, 10, 13)
            painter.drawLine(13, 13, 13, 10)


class MarketIndicatorWidget(QWidget):
    """רכיב Market Regime indicator - Bull/Bear עם אייקון"""
    regime_changed = pyqtSignal(str)  # 'Bull' או 'Bear'

    def __init__(self, data_router=None, parent=None):
        super().__init__(parent)
        self._market_regime = 'Bull'  # ברירת מחדל מהארטיפקט
        self.data_router = data_router
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        """הגדרת הממשק"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)  # space-x-2
        
        # תווית "Market"
        self.market_label = QLabel("Market")
        self.market_label.setObjectName("marketLabel")
        
        # הגדרת פונט
        font = QFont()
        font.setPointSize(10)  # text-sm
        self.market_label.setFont(font)
        self.market_label.setStyleSheet("color: #4b5563;")  # text-gray-600
        
        layout.addWidget(self.market_label)
        
        # Container לאייקון ולטקסט
        indicator_widget = QWidget()
        indicator_layout = QHBoxLayout(indicator_widget)
        indicator_layout.setContentsMargins(0, 0, 0, 0)
        indicator_layout.setSpacing(4)  # space-x-1
        
        # אייקון טרנד
        self.trend_icon = TrendingIcon(is_up=True)
        indicator_layout.addWidget(self.trend_icon)
        
        # טקסט המצב
        self.regime_label = QLabel(self._market_regime)
        self.regime_label.setObjectName("regimeLabel")
        
        # הגדרת פונט למצב
        regime_font = QFont()
        regime_font.setPointSize(10)  # text-sm
        regime_font.setBold(True)     # font-medium
        self.regime_label.setFont(regime_font)
        
        indicator_layout.addWidget(self.regime_label)
        
        layout.addWidget(indicator_widget)
        
        # מניעת התרחבות
        self.setSizePolicy(
            self.sizePolicy().Policy.Fixed,
            self.sizePolicy().Policy.Fixed
        )
        
    @property
    def market_regime(self):
        """מצב השוק הנוכחי"""
        return self._market_regime
        
    def set_market_regime(self, regime):
        """עדכון מצב השוק"""
        if regime not in ['Bull', 'Bear']:
            return
            
        if self._market_regime != regime:
            self._market_regime = regime
            self.update_display()
            self.regime_changed.emit(regime)
            
    def update_display(self):
        """עדכון התצוגה לפי המצב"""
        is_bull = self._market_regime == 'Bull'
        
        # עדכון אייקון
        self.trend_icon.set_direction(is_bull)
        
        # עדכון טקסט וצבע
        self.regime_label.setText(self._market_regime)
        
        if is_bull:
            color = '#16a34a'  # text-green-600
        else:
            color = '#dc2626'  # text-red-600
            
        self.regime_label.setStyleSheet(f"color: {color};")
        
    def toggle_regime(self):
        """החלפת מצב השוק (לבדיקות)"""
        new_regime = 'Bear' if self._market_regime == 'Bull' else 'Bull'
        self.set_market_regime(new_regime)
        
    def mousePressEvent(self, event):
        """לחיצה על הרכיב - החלפת מצב (לבדיקות)"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_regime()
        super().mousePressEvent(event)


class MarketRegimeContainer(QWidget):
    """Container מלא למצב השוק עם תכונות נוספות"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """הגדרת הממשק המלא"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # רכיב הבסיס
        self.market_indicator = MarketIndicatorWidget()
        layout.addWidget(self.market_indicator)
        
        # חיבור לאירועים
        self.market_indicator.regime_changed.connect(self.on_regime_changed)
        
    def on_regime_changed(self, regime):
        """טיפול בשינוי מצב השוק"""
        print(f"Market regime changed to: {regime}")
        
    def get_market_regime(self):
        """קבלת מצב השוק הנוכחי"""
        return self.market_indicator.market_regime
        
    def set_market_regime(self, regime):
        """הגדרת מצב השוק"""
        self.market_indicator.set_market_regime(regime)


# Export
__all__ = ['MarketIndicatorWidget', 'MarketRegimeContainer', 'TrendingIcon']
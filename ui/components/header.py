"""
ui/components/header.py - רכיב Header עם לוגו ושם אפליקציה
מתבסס על הארטיפקט React המקורי
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtSvg import QSvgRenderer
import io


class LogoWidget(QWidget):
    """רכיב לוגו - מדמה את האייקון TrendingUp מ-lucide-react"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)  # w-8 h-8 = 32px
        
    def paintEvent(self, event):
        """ציור הלוגו"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # רקע כחול
        painter.fillRect(self.rect(), QColor(37, 99, 235))  # bg-blue-600
        
        # ציור אייקון TrendingUp פשוט
        painter.setPen(QColor(255, 255, 255))  # text-white
        painter.setBrush(QColor(255, 255, 255))
        
        # קו עולה (מדמה TrendingUp)
        points = [
            (8, 20),   # נקודה שמאלית נמוכה
            (12, 16),  # נקודה באמצע
            (16, 12),  # נקודה ימנית גבוהה
            (20, 16),  # נקודה ימנית
            (24, 12)   # נקודה סופית
        ]
        
        # ציור הקו
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], 
                           points[i+1][0], points[i+1][1])
            
        # ציור נקודות
        for x, y in points:
            painter.drawEllipse(x-2, y-2, 4, 4)


class HeaderWidget(QWidget):
    """רכיב Header עם לוגו ושם אפליקציה"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """הגדרת הממשק"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)  # space-x-3 = 12px
        
        # לוגו
        self.logo = LogoWidget()
        layout.addWidget(self.logo)
        
        # שם האפליקציה
        self.app_name = QLabel("AlgoTrade Pro")
        self.app_name.setObjectName("appTitle")
        
        # הגדרת פונט לכותרת
        font = QFont()
        font.setPointSize(18)  # text-xl
        font.setBold(True)     # font-semibold
        self.app_name.setFont(font)
        
        # צבע הטקסט
        self.app_name.setStyleSheet("color: #1f2937;")  # text-gray-800
        
        layout.addWidget(self.app_name)
        
        # מניעת התרחבות
        self.setSizePolicy(
            self.sizePolicy().Policy.Fixed,
            self.sizePolicy().Policy.Fixed
        )


class HeaderSeparator(QFrame):
    """קו הפרדה אנכי בין רכיבי Header"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        self.setStyleSheet("color: #e5e7eb;")  # border-gray-200


class HeaderContainer(QWidget):
    """Container מלא ל-Header עם כל הרכיבים"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """הגדרת הממשק המלא"""
        # Layout ראשי
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)  # px-6 py-4
        main_layout.setSpacing(32)  # space-x-8
        
        # אזור שמאלי - לוגו ושם
        left_area = QWidget()
        left_layout = QHBoxLayout(left_area)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)  # space-x-3
        
        # רכיב Header בסיסי
        self.header_widget = HeaderWidget()
        left_layout.addWidget(self.header_widget)
        
        main_layout.addWidget(left_area)
        
        # Stretch למילוי החלל
        main_layout.addStretch()
        
        # הגדרת גובה קבוע
        self.setFixedHeight(64)
        
        # רקע ולבן עם גבול
        self.setStyleSheet("""
            HeaderContainer {
                background-color: white;
                border-bottom: 1px solid #e5e7eb;
            }
        """)


# Export הרכיב הראשי
__all__ = ['HeaderWidget', 'HeaderContainer', 'LogoWidget', 'HeaderSeparator']
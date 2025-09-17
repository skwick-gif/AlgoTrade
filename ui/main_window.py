"""
ui/main_window.py - החלון הראשי של מערכת המסחר
מתבסס על הארטיפקט React המקורי
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QStackedWidget, QFrame, QLabel, QPushButton,
    QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor


from ui.components.header import HeaderWidget
from ui.components.vix_gauge import VixGaugeWidget
from ui.components.market_indicator import MarketIndicatorWidget
from ui.components.ibkr_status import IBKRStatusWidget


class SidebarWidget(QWidget):
    def update_buttons(self, buttons):
        # ניקוי כפתורים קיימים
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # יצירת כפתורים חדשים
        for btn_name in buttons:
            btn = QPushButton(btn_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=btn_name: self.button_clicked.emit(name))
            self.buttons_layout.addWidget(btn)
    """Sidebar עם כפתורים דינמיים לכל לשונית"""
    button_clicked = pyqtSignal(str)  # שם הכפתור שנלחץ

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)
        self.buttons_widget = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_widget)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(4)
        layout.addWidget(self.buttons_widget)
        layout.addStretch()
        self.setFixedWidth(192)

class ContentWidget(QWidget):
    """אזור התוכן הראשי"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        self.title_label = QLabel("Dashboard Content")
        self.title_label.setObjectName("contentTitle")
        layout.addWidget(self.title_label)
        self.content_label = QLabel("Content for Dashboard will be displayed here")
        self.content_label.setObjectName("contentPlaceholder")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.content_label, 1)

    def update_content(self, tab_name, sidebar_button=None):
        if sidebar_button:
            self.title_label.setText(f"{tab_name} - {sidebar_button}")
            self.content_label.setText(f"Content for {sidebar_button} will be displayed here")
        else:
            self.title_label.setText(f"{tab_name} Content")
            self.content_label.setText(f"Content for {tab_name} will be displayed here")
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """הגדרת הממשק"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # כותרת
        self.title_label = QLabel("Dashboard Content")
        self.title_label.setObjectName("contentTitle")
        layout.addWidget(self.title_label)
        
        # תוכן ריק (זמני)
        self.content_label = QLabel("Content for Dashboard will be displayed here")
        self.content_label.setObjectName("contentPlaceholder")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.content_label, 1)
        
    def update_content(self, tab_name, sidebar_button=None):
        """עדכון התוכן לפי לשונית וכפתור sidebar נבחרים"""
        if sidebar_button:
            self.title_label.setText(f"{tab_name} - {sidebar_button}")
            self.content_label.setText(f"Content for {sidebar_button} will be displayed here")
        else:
            self.title_label.setText(f"{tab_name} Content")
            self.content_label.setText(f"Content for {tab_name} will be displayed here")


class MainWindow(QMainWindow):
    """החלון הראשי - מתבסס על הארטיפקט React"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        
        # נתונים מהארטיפקט המקורי
        self.tabs = [
            'Dashboard', 'Scanning', 'Watchlist', 
            'Options Trading', 'Analytics', 'Settings'
        ]
        
        self.sidebar_content = {
            'Dashboard': ['Overview', 'Markets', 'Positions', 'P&L', 'News', 'Alerts'],
            'Scanning': ['Stock Scanner', 'Options Scanner', 'Filters', 'Results', 'Saved Scans', 'Export'],
            'Watchlist': ['Active List', 'Create List', 'Price Alerts', 'Volume Alerts', 'Technical Alerts', 'History'],
            'Options Trading': [
                'Strategy Builder',
                'Active Trades',
                'WHEEL',
                'STRADDLE',
                'COVERED CALL',
                'IRON CONDOR',
                'Backtest',
                'Settings'
            ],
            'Analytics': ['Performance', 'Reports', 'Trade History', 'Risk Analysis', 'Charts', 'Export'],
            'Settings': ['Account', 'Data Sources', 'API Keys', 'Notifications', 'Import/Export', 'About']
        }
        
        self.current_tab_index = 0
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
        
    def setup_ui(self):
        """הגדרת הממשק הראשי"""
        self.setWindowTitle("AlgoTrade Pro")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Widget מרכזי
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout ראשי
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header = self.create_header()
        main_layout.addWidget(self.header)

        # Tabs
        self.tab_widget = self.create_tabs()
        main_layout.addWidget(self.tab_widget)

        # אזור תוכן עם sidebar
        content_splitter = self.create_content_area()
        main_layout.addWidget(content_splitter, 1)

    def create_header(self):
        """יצירת ה-Header עם כל הרכיבים"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(64)  # py-4 = 16px * 2 + content

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 16, 24, 16)

        # לוגו ושם אפליקציה
        logo_widget = HeaderWidget()
        header_layout.addWidget(logo_widget)

        header_layout.addStretch()

        # יצירת instance אחיד של DataRouter
        from data_management.data_router import DataRouter
        self.data_router = DataRouter()

        # VIX Gauge
        self.vix_gauge = VixGaugeWidget(data_router=self.data_router)
        header_layout.addWidget(self.vix_gauge)

        # רווח
        header_layout.addSpacing(32)

        # Market Indicator
        self.market_indicator = MarketIndicatorWidget(data_router=self.data_router)
        header_layout.addWidget(self.market_indicator)

        # רווח
        header_layout.addSpacing(32)

        # IBKR Status
        self.ibkr_status = IBKRStatusWidget()
        header_layout.addWidget(self.ibkr_status)

        return header_frame
        
    def create_tabs(self):
        """יצירת לשוניות"""
        tab_frame = QFrame()
        tab_frame.setObjectName("tabFrame")
        
        tab_layout = QHBoxLayout(tab_frame)
        tab_layout.setContentsMargins(24, 0, 24, 0)
        tab_layout.setSpacing(0)
        
        # יצירת כפתורי לשוניות
        self.tab_buttons = []
        for i, tab_name in enumerate(self.tabs):
            btn = QPushButton(tab_name)
            btn.setObjectName("tabButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            self.tab_buttons.append(btn)
            tab_layout.addWidget(btn)
            
        tab_layout.addStretch()
        
        # בחירת הלשונית הראשונה
        self.tab_buttons[0].setChecked(True)
        
        return tab_frame
        
    def create_content_area(self):
        """יצירת אזור התוכן עם sidebar"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.setObjectName("sidebar")
        splitter.addWidget(self.sidebar)
        
        # Content area
        self.content_widget = ContentWidget()
        self.content_widget.setObjectName("contentArea")
        splitter.addWidget(self.content_widget)
        
        # יחסי רוחב: sidebar קבוע, content גמיש
        splitter.setSizes([192, 1000])
        splitter.setChildrenCollapsible(False)
        
        # עדכון sidebar ראשוני
        self.update_sidebar_content()
        
        return splitter
        
    def setup_connections(self):
        """הגדרת חיבורים בין רכיבים"""
        # sidebar button clicks
        self.sidebar.button_clicked.connect(self.on_sidebar_button_clicked)
        
    def setup_timers(self):
        """הגדרת טיימרים לעדכון נתונים"""
        # עדכון VIX כל דקה
        self.vix_timer = QTimer()
        self.vix_timer.timeout.connect(self.update_vix_data)
        self.vix_timer.start(60000)  # 60 שניות
        
        # עדכון Market Regime כל 5 דקות
        self.market_timer = QTimer()
        self.market_timer.timeout.connect(self.update_market_data)
        self.market_timer.start(300000)  # 5 דקות
        
    def switch_tab(self, index):
        """מעבר בין לשוניות"""
        if index == self.current_tab_index:
            return
            
        # עדכון כפתורי לשוניות
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)
            
        self.current_tab_index = index
        self.update_sidebar_content()
        self.update_content()
        
    def update_sidebar_content(self):
        """עדכון תוכן ה-sidebar לפי לשונית נבחרת"""
        current_tab_name = self.tabs[self.current_tab_index]
        buttons = self.sidebar_content.get(current_tab_name, [])
        self.sidebar.update_buttons(buttons)
        
    def update_content(self):
        """עדכון התוכן הראשי"""
        current_tab_name = self.tabs[self.current_tab_index]
        self.content_widget.update_content(current_tab_name)
        
    def on_sidebar_button_clicked(self, button_name):
        """טיפול בלחיצה על כפתור sidebar"""
        current_tab_name = self.tabs[self.current_tab_index]
        self.content_widget.update_content(current_tab_name, button_name)
        
    def update_vix_data(self):
        """עדכון נתוני VIX אמיתיים"""
        try:
            from data_management.data_router import DataRouter
            dr = DataRouter()
            vix_data = dr.get_vix()
            if vix_data and hasattr(vix_data, 'price') and vix_data.price:
                self.vix_gauge.set_vix_value(vix_data.price)
                # הצגת מקור הנתון (ספק) אם קיים
                provider_name = getattr(vix_data, 'provider', None)
                if provider_name:
                    self.vix_gauge.status_label.setText(str(provider_name))
                else:
                    self.vix_gauge.status_label.setText(self.vix_gauge.get_vix_label(vix_data.price))
            else:
                self.vix_gauge.set_vix_value(0)
                self.vix_gauge.status_label.setText("NO DATA")
        except Exception as e:
            self.vix_gauge.set_vix_value(0)
            self.vix_gauge.status_label.setText("ERROR")
            import traceback
            self.vix_gauge.logger.error(f"VIX update error: {e}\n{traceback.format_exc()}")
        
    def update_market_data(self):
        """עדכון מצב שוק אמיתי"""
        try:
            from data_management.data_router import DataRouter
            dr = DataRouter()
            market_data = dr.get_market_data()
            # נניח שמתקבל dict עם 'regime': 'Bull'/'Bear'
            regime = None
            if market_data:
                # אם התקבל dict עם מפתח 'regime'
                if isinstance(market_data, dict) and 'regime' in market_data:
                    regime = market_data['regime']
                # אם התקבל אובייקט עם attribute 'regime'
                elif hasattr(market_data, 'regime'):
                    regime = getattr(market_data, 'regime')
            if regime in ['Bull', 'Bear']:
                self.market_indicator.set_market_regime(regime)
            else:
                self.market_indicator.set_market_regime('Bear')  # ברירת מחדל
        except Exception as e:
            self.market_indicator.set_market_regime('Bear')
            import traceback
            if hasattr(self.market_indicator, 'logger'):
                self.market_indicator.logger.error(f"Market regime update error: {e}\n{traceback.format_exc()}")
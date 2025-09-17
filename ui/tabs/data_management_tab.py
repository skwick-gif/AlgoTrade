from PyQt6 import QtWidgets, QtCore

class DataManagementTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.current_sidebar_btn = "ניהול דאטה מניות"
        # Stacked widget for content
        self.stacked = QtWidgets.QStackedWidget()
        # Stocks data widget
        self.stocks_widget = QtWidgets.QWidget()
        stocks_layout = QtWidgets.QVBoxLayout(self.stocks_widget)
        stocks_layout.setContentsMargins(40, 20, 40, 20)

        # שורת כותרת + כפתורים
        title_row = QtWidgets.QHBoxLayout()
        stocks_title = QtWidgets.QLabel("ניהול נתונים מניות - הורדה ועדכון דאטה")
        stocks_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_row.addWidget(stocks_title, 1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.download_year_btn = QtWidgets.QPushButton("הורד שנה אחורה")
        self.download_year_btn.setFixedWidth(120)
        self.download_day_btn = QtWidgets.QPushButton("הורד יום אחרון")
        self.download_day_btn.setFixedWidth(120)
        btns_row = QtWidgets.QHBoxLayout()
        btns_row.addWidget(self.download_year_btn)
        btns_row.addWidget(self.download_day_btn)
        btns_row.setSpacing(8)
        btns_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        title_row.addLayout(btns_row)
        stocks_layout.addLayout(title_row)

        symbols_label = QtWidgets.QLabel("סימבולים (מופרדים בפסיק):")
        stocks_layout.addWidget(symbols_label)
        self.symbols_input = QtWidgets.QLineEdit()
        self.symbols_input.setPlaceholderText("AAPL, MSFT, TSLA")
        stocks_layout.addWidget(self.symbols_input)

        # שורת טווח תאריכים מפוצלת + כפתור
        date_row = QtWidgets.QHBoxLayout()
        date_range_label = QtWidgets.QLabel("טווח תאריכים להורדה:")
        date_row.addWidget(date_range_label)
        self.date_from = QtWidgets.QLineEdit()
        self.date_from.setPlaceholderText("מתאריך (dd-mm-yyyy)")
        self.date_from.setFixedWidth(120)
        date_row.addWidget(self.date_from)
        self.date_to = QtWidgets.QLineEdit()
        self.date_to.setPlaceholderText("עד תאריך (dd-mm-yyyy)")
        self.date_to.setFixedWidth(120)
        date_row.addWidget(self.date_to)
        self.download_range_btn = QtWidgets.QPushButton("הורד לפי טווח")
        self.download_range_btn.setFixedWidth(110)
        date_row.addWidget(self.download_range_btn)
        date_row.setSpacing(8)
        date_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        stocks_layout.addLayout(date_row)

        self.show_data_btn = QtWidgets.QPushButton("הצג נתונים")
        stocks_layout.addWidget(self.show_data_btn)
        self.show_data_btn.clicked.connect(self.show_data_table)
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: #1976d2; margin-top: 16px;")
        stocks_layout.addWidget(self.status_label)
        self.files_label = QtWidgets.QLabel("קבצים קיימים:")
        stocks_layout.addWidget(self.files_label)
        self.files_list = QtWidgets.QListWidget()
        stocks_layout.addWidget(self.files_list)

        # Options data widget (placeholder)
        self.options_widget = QtWidgets.QWidget()
        options_layout = QtWidgets.QVBoxLayout(self.options_widget)
        options_layout.setContentsMargins(40, 20, 40, 20)
        options_title = QtWidgets.QLabel("ניהול נתונים אופציות - בקרוב")
        options_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 12px;")
        options_layout.addWidget(options_title)
        options_layout.addStretch()
        self.stacked.addWidget(self.stocks_widget)
        self.stacked.addWidget(self.options_widget)
        self.stacked.setCurrentWidget(self.stocks_widget)

        # הצגת תוכן ראשוני
        self.show_stocks()
        # טען קבצים קיימים
        self.refresh_files_list()
        # חיבור כפתורים
        self.download_year_btn.clicked.connect(self.download_year)
        self.download_day_btn.clicked.connect(self.download_day)
        self.download_range_btn.clicked.connect(self.download_range)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.stacked)

    def set_content_by_name(self, name):
        if name == "ניהול דאטה מניות":
            self.stacked.setCurrentWidget(self.stocks_widget)
        elif name == "ניהול דאטה אופציות":
            self.stacked.setCurrentWidget(self.options_widget)

    def show_stocks(self):
        self.stacked.setCurrentWidget(self.stocks_widget)

    def show_options(self):
        self.stacked.setCurrentWidget(self.options_widget)

    def refresh_files_list(self):
        # Stub: implement file list refresh logic if needed
        pass

    def show_data_table(self):
        from data_management.stock_db import StockDB
        symbol = self.symbols_input.text().strip().upper()
        if not symbol:
            self.status_label.setText("יש להזין סימבול להצגה")
            return
        start_date = self.date_from.text().strip()
        end_date = self.date_to.text().strip()
        import re
        pattern = r"^(\d{2}-\d{2}-\d{4})$"
        if not re.match(pattern, start_date) or not re.match(pattern, end_date):
            self.status_label.setText("פורמט תאריך לא תקין. יש להזין: dd-mm-yyyy")
            return
        db = StockDB()
        rows = db.query(symbol, start_date, end_date)
        db.close()
        if not rows:
            self.status_label.setText("שגיאה בהורדת נתונים לשנה אחורה")
            return
        # Remove old table if exists
        if hasattr(self, 'data_table'):
            self.stocks_widget.layout().removeWidget(self.data_table)
            self.data_table.deleteLater()
        # Create table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(["Symbol", "Date", "Open", "High", "Low", "Close", "Volume", "Adj Close"])
        table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row.get("symbol", ""))))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row.get("date", ""))))
            table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(row.get("open", ""))))
            table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row.get("high", ""))))
            table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(row.get("low", ""))))
            table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(row.get("close", ""))))
            table.setItem(i, 6, QtWidgets.QTableWidgetItem(str(row.get("volume", ""))))
            table.setItem(i, 7, QtWidgets.QTableWidgetItem(str(row.get("adj_close", ""))))
        table.resizeColumnsToContents()
        self.stocks_widget.layout().addWidget(table)
        self.data_table = table
        self.status_label.setText(f"הוצגו {len(rows)} רשומות עבור {symbol}")
        self.refresh_files_list()
        # אם לא התקבלו נתונים
        if not rows:
            self.status_label.setText("שגיאה בהורדת נתונים לשנה אחורה")
            return
    def download_year(self):
        from data_management.data_router import DataRouter
        from data_management.stock_db import StockDB
        import datetime
        self.status_label.setText("מוריד נתונים לשנה אחורה...")
        router = DataRouter()
        db = StockDB()
        symbols = self.symbols_input.text().strip()
        if not symbols:
            symbols = "AAPL"
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)
        results = []
        for symbol in symbol_list:
            try:
                if hasattr(router, 'get_historical_data'):
                    data = router.get_historical_data(symbol, start_date.isoformat(), end_date.isoformat())
                else:
                    data = router.get_quote(symbol)
            except Exception:
                data = None
            # נניח ש-data הוא רשימה של dict או אובייקט אחד
            rows = []
            if isinstance(data, list):
                for item in data:
                    if hasattr(item, 'to_dict'):
                        rows.append(item.to_dict())
                    elif isinstance(item, dict):
                        rows.append(item)
            elif hasattr(data, 'to_dict'):
                rows.append(data.to_dict())
            elif isinstance(data, dict):
                rows.append(data)
            if rows:
                # Try to get provider name from router or data
                provider_name = None
                if hasattr(router, 'last_provider'):
                    provider_name = getattr(router, 'last_provider', None)
                if not provider_name and rows and 'provider' in rows[0]:
                    provider_name = rows[0].get('provider')
                db.insert_rows(rows, provider=provider_name)
                results.append(symbol)
        db.close()
        if results:
            self.status_label.setText(f"הורדה הושלמה ושמורה ל-SQLite עבור: {', '.join(results)}")
        else:
            self.status_label.setText("שגיאה בהורדת נתונים לשנה אחורה")

    def download_day(self):
        from data_management.data_router import DataRouter
        import json, os, datetime
        self.status_label.setText("מוריד נתונים ליום אחרון...")
        router = DataRouter()
        symbols = self.symbols_input.text().strip()
        if not symbols:
            symbols = "AAPL"
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        date_str = datetime.date.today().isoformat()
        results = []
        for symbol in symbol_list:
            data = router.get_quote(symbol)
            if data:
                data_dict = data.to_dict() if hasattr(data, 'to_dict') else data
                file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_management', f"{symbol}_{date_str}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_dict, f, ensure_ascii=False, indent=2)
                results.append(symbol)
        if results:
            self.status_label.setText(f"הורדה הושלמה עבור: {', '.join(results)}")
            self.refresh_files_list()
        else:
            self.status_label.setText("שגיאה בהורדת נתונים ליום אחרון")

    def download_range(self):
        import re, json, os
        start_date = self.date_from.text().strip()
        end_date = self.date_to.text().strip()
        pattern = r"^(\d{2}-\d{2}-\d{4})$"
        if not re.match(pattern, start_date) or not re.match(pattern, end_date):
            self.status_label.setText("פורמט תאריך לא תקין. יש להזין: dd-mm-yyyy")
            return
        symbols = self.symbols_input.text().strip()
        if not symbols:
            symbols = "AAPL"
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        self.status_label.setText(f"מוריד נתונים מ-{start_date} עד {end_date} עבור {', '.join(symbol_list)}...")
        from data_management.data_router import DataRouter
        router = DataRouter()
        results = []
        for symbol in symbol_list:
            # כאן אפשר להרחיב ל-API שמקבל טווח תאריכים
            data = router.get_quote(symbol)
            if data:
                data_dict = data.to_dict() if hasattr(data, 'to_dict') else data
                file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_management', f"{symbol}_{start_date}_to_{end_date}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_dict, f, ensure_ascii=False, indent=2)
                results.append(symbol)
        if results:
            self.status_label.setText(f"הורדה הושלמה עבור: {', '.join(results)}")
            self.refresh_files_list()
        else:
            self.status_label.setText("שגיאה בהורדת נתונים לטווח")

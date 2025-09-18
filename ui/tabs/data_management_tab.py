from PyQt6 import QtWidgets, QtCore

class DataManagementTab(QtWidgets.QWidget):
    def download_range(self):
        from data_management.data_router import DataRouter
        from data_management.stock_db import StockDB
        import datetime, pandas as pd
        self.status_label.setText("מוריד נתונים לטווח תאריכים...")
        router = DataRouter()
        db = StockDB()
        symbols = self.symbols_input.text().strip()
        if not symbols:
            symbols = "AAPL"
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        start_date = self.date_from.text().strip()
        end_date = self.date_to.text().strip()
        # המרה לפורמט ISO
        try:
            start_dt = datetime.datetime.strptime(start_date, "%d-%m-%Y")
            end_dt = datetime.datetime.strptime(end_date, "%d-%m-%Y")
        except Exception:
            self.status_label.setText("פורמט תאריך לא תקין. יש להזין: dd-mm-yyyy")
            return
        results = []
        provider_order = ["yahoo", "finnhub", "alphavantage", "polygon", "twelvedata", "fmp"]
        for symbol in symbol_list:
            got_data = False
            for provider_name in provider_order:
                try:
                    if hasattr(router, 'get_historical_data'):
                        data = router.get_historical_data(symbol, start_dt.date().isoformat(), end_dt.date().isoformat(), provider=provider_name)
                    else:
                        data = router.get_quote(symbol, provider=provider_name)
                except Exception as e:
                    self.status_label.setText(f"שגיאה ({provider_name}) עבור {symbol}: {e}")
                    continue
                if isinstance(data, pd.DataFrame):
                    if data.empty:
                        self.status_label.setText(f"אין נתונים זמינים עבור {symbol} ({provider_name})")
                        continue
                    rows = data.to_dict('records')
                else:
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
                if not rows:
                    self.status_label.setText(f"לא התקבלו נתונים עבור {symbol} ({provider_name})")
                    continue
                db.insert_rows(rows, provider=provider_name)
                results.append(symbol)
                got_data = True
                break
            if not got_data:
                self.status_label.setText(f"לא נמצאו נתונים עבור {symbol} בכל הספקים")
        db.close()
        if results:
            self.status_label.setText(f"הורדה הושלמה ושמורה ל-SQLite עבור: {', '.join(results)}")
        else:
            self.status_label.setText("שגיאה בהורדת נתונים לטווח תאריכים")
    # הגדרה אחת בלבד ל-__init__ ולמבנה המחלקה
    def __init__(self):
        super().__init__()
        self.current_sidebar_btn = "ניהול דאטה מניות"
        self.stacked = QtWidgets.QStackedWidget()
        self.stocks_widget = QtWidgets.QWidget()
        stocks_layout = QtWidgets.QVBoxLayout(self.stocks_widget)
        stocks_layout.setContentsMargins(40, 20, 40, 20)
        title_row = QtWidgets.QHBoxLayout()
        stocks_title = QtWidgets.QLabel("ניהול נתונים מניות - הורדה ועדכון דאטה")
        stocks_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_row.addWidget(stocks_title, 1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.download_year_btn = QtWidgets.QPushButton("הורד שנה אחורה")
        self.download_year_btn.setFixedWidth(120)
        self.download_day_btn = QtWidgets.QPushButton("הורד יום אחרון")
        self.download_day_btn.setFixedWidth(120)
        self.resume_btn = QtWidgets.QPushButton("Resume הורדה")
        self.resume_btn.setFixedWidth(120)
        btns_row = QtWidgets.QHBoxLayout()
        btns_row.addWidget(self.download_year_btn)
        btns_row.addWidget(self.download_day_btn)
        btns_row.addWidget(self.resume_btn)
        btns_row.setSpacing(8)
        btns_row.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        title_row.addLayout(btns_row)
        stocks_layout.addLayout(title_row)
        symbols_label = QtWidgets.QLabel("סימבולים (מופרדים בפסיק):")
        stocks_layout.addWidget(symbols_label)
        self.symbols_input = QtWidgets.QLineEdit()
        self.symbols_input.setPlaceholderText("AAPL, MSFT, TSLA")
        stocks_layout.addWidget(self.symbols_input)
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
        files_row = QtWidgets.QHBoxLayout()
        files_row.addWidget(self.files_label)
        self.browse_btn = QtWidgets.QPushButton("Browse")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.browse_download_folder)
        files_row.addWidget(self.browse_btn)
        files_row.addStretch()
        stocks_layout.addLayout(files_row)
        self.files_list = QtWidgets.QListWidget()
        stocks_layout.addWidget(self.files_list)
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
        self.show_stocks()
        self.refresh_files_list()
        self.download_year_btn.clicked.connect(self.download_year)
        self.download_day_btn.clicked.connect(self.download_day)
        self.download_range_btn.clicked.connect(self.download_range)
        self.resume_btn.clicked.connect(self.resume_download)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.stacked)
        # ...existing code...
    def resume_download(self):
        import threading, json, os
        def run_resume():
            cache_path = os.path.join(os.path.dirname(__file__), '..', 'data_management', 'resume_cache.json')
            if not os.path.exists(cache_path):
                self.status_label.setText("לא נמצא קובץ resume_cache.json")
                return
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            done = set(cache.get("done", []))
            last_ticker = cache.get("last_ticker")
            symbols = self.symbols_input.text().strip()
            if not symbols:
                symbols = "AAPL"
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
            to_do = [s for s in symbol_list if s not in done]
            if not to_do:
                self.status_label.setText("כל הסימבולים כבר טופלו!")
                return
            self.status_label.setText(f"ממשיך הורדה מ-{last_ticker or to_do[0]} ({len(to_do)} סימבולים)")
            QtWidgets.QApplication.processEvents()
            from data_management.data_router import DataRouter
            from data_management.stock_db import StockDB
            import pandas as pd
            router = DataRouter()
            db = StockDB()
            provider_order = ["yahoo", "finnhub", "alphavantage", "polygon", "twelvedata", "fmp"]
            for symbol in to_do:
                got_data = False
                for provider_name in provider_order:
                    try:
                        if provider_name == "yahoo":
                            if hasattr(router, 'get_historical_data'):
                                data = router._providers["yahoo"].get_historical_data(symbol, None, None, period="1y")
                            else:
                                data = router.get_quote(symbol, provider=provider_name)
                        elif hasattr(router, 'get_historical_data'):
                            data = router.get_historical_data(symbol, None, None, provider=provider_name)
                        else:
                            data = router.get_quote(symbol, provider=provider_name)
                    except Exception as e:
                        self.status_label.setText(f"שגיאה ({provider_name}) עבור {symbol}: {e}")
                        QtWidgets.QApplication.processEvents()
                        continue
                    if isinstance(data, pd.DataFrame):
                        if data.empty:
                            self.status_label.setText(f"אין נתונים זמינים עבור {symbol} ({provider_name})")
                            QtWidgets.QApplication.processEvents()
                            continue
                        rows = data.to_dict('records')
                    else:
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
                    if not rows:
                        self.status_label.setText(f"לא התקבלו נתונים עבור {symbol} ({provider_name})")
                        QtWidgets.QApplication.processEvents()
                        continue
                    db.insert_rows(rows, provider=provider_name)
                    got_data = True
                    break
                # עדכון cache
                done.add(symbol)
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump({"done": list(done), "last_ticker": symbol, "errors": cache.get("errors", {})}, f, ensure_ascii=False, indent=2)
                self.status_label.setText(f"הורדה הושלמה עבור {symbol}")
                QtWidgets.QApplication.processEvents()
            db.close()
            self.status_label.setText(f"הורדה הושלמה לכל הסימבולים!")
            QtWidgets.QApplication.processEvents()
        threading.Thread(target=run_resume, daemon=True).start()

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

    def get_download_folder(self):
        import os
        folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data_management', 'downloads')
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        return folder

    def refresh_files_list(self):
        import os
        folder = self.get_download_folder()
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        self.files_list.clear()
        for f in sorted(files):
            self.files_list.addItem(f)

    def browse_download_folder(self):
        import os
        folder = self.get_download_folder()
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

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
        rows = db.get_merged_rows(symbol, start_date, end_date)
        db.close()
        if not rows:
            self.status_label.setText("לא נמצאו נתונים מאוחדים לתאריכים שבחרת")
            return
        # Remove old table if exists
        if hasattr(self, 'data_table'):
            self.stocks_widget.layout().removeWidget(self.data_table)
            self.data_table.deleteLater()
        # Create table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(["Symbol", "Date", "Open", "High", "Low", "Close", "Volume", "Adj Close", "Sources"])
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
            # sources: רשימת ספקים
            sources = row.get("sources", [])
            table.setItem(i, 8, QtWidgets.QTableWidgetItem(", ".join([str(s) for s in sources])))
        table.resizeColumnsToContents()
        self.stocks_widget.layout().addWidget(table)
        self.data_table = table
        self.status_label.setText(f"הוצגו {len(rows)} רשומות מאוחדות עבור {symbol}")
        self.refresh_files_list()
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
        import pandas as pd
        provider_order = ["yahoo", "finnhub", "alphavantage", "polygon", "twelvedata", "fmp"]
        for symbol in symbol_list:
            got_data = False
            for provider_name in provider_order:
                try:
                    if hasattr(router, 'get_historical_data'):
                        data = router.get_historical_data(symbol, start_date.isoformat(), end_date.isoformat(), provider=provider_name)
                    else:
                        data = router.get_quote(symbol, provider=provider_name)
                except Exception as e:
                    self.status_label.setText(f"שגיאה ({provider_name}) עבור {symbol}: {e}")
                    continue
                # טיפול במקרה של DataFrame ריק
                if isinstance(data, pd.DataFrame):
                    if data.empty:
                        self.status_label.setText(f"אין נתונים זמינים עבור {symbol} ({provider_name})")
                        continue
                    rows = data.to_dict('records')
                else:
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
                if not rows:
                    self.status_label.setText(f"לא התקבלו נתונים עבור {symbol} ({provider_name})")
                    continue
                db.insert_rows(rows, provider=provider_name)
                results.append(symbol)
                got_data = True
                break
            if not got_data:
                self.status_label.setText(f"לא נמצאו נתונים עבור {symbol} בכל הספקים")
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
                file_path = os.path.join(self.get_download_folder(), f"{symbol}_{date_str}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_dict, f, ensure_ascii=False, indent=2)
                results.append(symbol)
        if results:
            self.status_label.setText(f"הורדה הושלמה עבור: {', '.join(results)}")
            self.refresh_files_list()
        else:
            from data_management.stock_db import StockDB
            import pandas as pd
            import logging
            logger = logging.getLogger("download_year")
            self.status_label.setText("מוריד נתונים לשנה אחורה... (פעולה עשויה להימשך מספר שניות)")
            router = DataRouter()
            db = StockDB()
            symbols = self.symbols_input.text().strip()
            if not symbols:
                symbols = "AAPL"
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
            logger.info(f"[download_year] סימבולים: {symbol_list}")
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)
            results = []
            provider_order = ["yahoo", "finnhub", "alphavantage", "polygon", "twelvedata", "fmp"]
            logger.info(f"[download_year] ספקים: {provider_order}")
            for symbol in symbol_list:
                got_data = False
                for provider_name in provider_order:
                    logger.info(f"[download_year] מנסה {symbol} דרך {provider_name}")
                    self.status_label.setText(f"מנסה להוריד {symbol} דרך {provider_name}...")
                    QtWidgets.QApplication.processEvents()
                    try:
                        if hasattr(router, 'get_historical_data'):
                            data = router.get_historical_data(symbol, start_date.isoformat(), end_date.isoformat(), provider=provider_name)
                        else:
                            data = router.get_quote(symbol, provider=provider_name)
                    except Exception as e:
                        logger.error(f"[download_year] שגיאה ({provider_name}) עבור {symbol}: {e}")
                        self.status_label.setText(f"שגיאה ({provider_name}) עבור {symbol}: {e}")
                        QtWidgets.QApplication.processEvents()
                        continue
                    # טיפול במקרה של DataFrame ריק
                    if isinstance(data, pd.DataFrame):
                        logger.info(f"[download_year] התקבל DataFrame עבור {symbol} ({provider_name}), שורות: {len(data)}")
                        if data.empty:
                            logger.warning(f"[download_year] אין נתונים זמינים עבור {symbol} ({provider_name})")
                            self.status_label.setText(f"אין נתונים זמינים עבור {symbol} ({provider_name})")
                            QtWidgets.QApplication.processEvents()
                            continue
                        rows = data.to_dict('records')
                    else:
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
                    logger.info(f"[download_year] rows: {len(rows)}")
                    if not rows:
                        logger.warning(f"[download_year] לא התקבלו נתונים עבור {symbol} ({provider_name})")
                        self.status_label.setText(f"לא התקבלו נתונים עבור {symbol} ({provider_name})")
                        QtWidgets.QApplication.processEvents()
                        continue
                    db.insert_rows(rows, provider=provider_name)
                    results.append(symbol)
                    got_data = True
                    logger.info(f"[download_year] הצלחה עבור {symbol} דרך {provider_name}")
                    break
                if not got_data:
                    logger.warning(f"[download_year] לא נמצאו נתונים עבור {symbol} בכל הספקים")
                    self.status_label.setText(f"לא נמצאו נתונים עבור {symbol} בכל הספקים")
                    QtWidgets.QApplication.processEvents()
            db.close()
            logger.info(f"[download_year] סיום, results: {results}")
            if results:
                self.status_label.setText(f"הורדה הושלמה ושמורה ל-SQLite עבור: {', '.join(results)}")
            else:
                self.status_label.setText("שגיאה בהורדת נתונים לשנה אחורה")
        # ...existing code...

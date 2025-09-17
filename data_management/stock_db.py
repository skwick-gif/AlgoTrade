import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent / "stocks.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    provider TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    adj_close REAL,
    raw_data TEXT,
    PRIMARY KEY (symbol, date, provider)
);
CREATE INDEX IF NOT EXISTS idx_symbol_date ON stocks(symbol, date);
"""

class StockDB:
    def get_merged_rows(self, symbol: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        מחזיר רשומות מאוחדות לכל סימבול-תאריך, עם מידע משולב מכל הספקים
        """
        sql = "SELECT * FROM stocks WHERE symbol = ?"
        params = [symbol]
        if start_date:
            sql += " AND date >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date <= ?"
            params.append(end_date)
        sql += " ORDER BY date ASC"
        cur = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cur.description]
        # איחוד לפי (symbol, date)
        merged = {}
        for row in cur.fetchall():
            d = dict(zip(columns, row))
            key = (d["symbol"], d["date"])
            # Parse raw_data JSON if needed
            if d.get("raw_data"):
                import json
                try:
                    d["raw_data"] = json.loads(d["raw_data"])
                except Exception:
                    pass
            if key not in merged:
                merged[key] = {**d, "sources": [d["provider"]]}
            else:
                # עדכן שדות חסרים/ריקים מהספק הנוסף
                for field in ["open", "high", "low", "close", "volume", "adj_close"]:
                    if merged[key].get(field) is None and d.get(field) is not None:
                        merged[key][field] = d[field]
                merged[key]["sources"].append(d["provider"])
                # אפשר להוסיף איחוד raw_data לפי צורך
        return list(merged.values())
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path) if db_path else str(DB_PATH)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute(CREATE_TABLE_SQL)
        self.conn.commit()

    def insert_rows(self, rows: List[Dict[str, Any]], provider: Optional[str] = None):
        import json
        sql = """
        INSERT OR REPLACE INTO stocks (symbol, date, provider, open, high, low, close, volume, adj_close, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        data = []
        for row in rows:
            symbol = row.get("symbol")
            date = row.get("date")
            open_ = row.get("open")
            high = row.get("high")
            low = row.get("low")
            close = row.get("close")
            volume = row.get("volume")
            adj_close = row.get("adj_close")
            raw_data = json.dumps(row, ensure_ascii=False)
            prov = provider if provider else row.get("provider")
            data.append((symbol, date, prov, open_, high, low, close, volume, adj_close, raw_data))
        self.conn.executemany(sql, data)
        self.conn.commit()

    def query(self, symbol: str, start_date: str = None, end_date: str = None, filters: Dict[str, Any] = None, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM stocks WHERE symbol = ?"
        params = [symbol]
        if start_date:
            sql += " AND date >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND date <= ?"
            params.append(end_date)
        if provider:
            sql += " AND provider = ?"
            params.append(provider)
        if filters:
            for k, v in filters.items():
                sql += f" AND {k} = ?"
                params.append(v)
        sql += " ORDER BY date ASC"
        cur = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            d = dict(zip(columns, row))
            # Parse raw_data JSON if needed
            if d.get("raw_data"):
                import json
                try:
                    d["raw_data"] = json.loads(d["raw_data"])
                except Exception:
                    pass
            results.append(d)
        return results

    def get_symbols(self) -> List[str]:
        cur = self.conn.execute("SELECT DISTINCT symbol FROM stocks")
        return [row[0] for row in cur.fetchall()]

    def close(self):
        self.conn.close()

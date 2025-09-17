
import sqlite3, pathlib
DB_PATH = pathlib.Path("data_management/usage_tracker.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS usage (provider TEXT, ts INTEGER, units INTEGER)")
conn.commit()

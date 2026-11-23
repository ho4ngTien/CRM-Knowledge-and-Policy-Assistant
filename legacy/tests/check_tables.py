import sys
from pathlib import Path
import sqlite3

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from legacy.s4.services.database import init_database, get_database_path

if __name__ == "__main__":
    init_database()
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row

    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()

    print("Cac bang va cot trong database:")
    for table in tables:
        t_name = table["name"]
        cols = connection.execute(f"PRAGMA table_info({t_name})").fetchall()
        col_names = [f"{c['name']} ({c['type']})" for c in cols]
        print(f"- {t_name}: {', '.join(col_names)}")

    connection.close()

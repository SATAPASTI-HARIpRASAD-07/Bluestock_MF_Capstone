import sys, os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
from db.loader import DatabaseBuilder

def main():
    builder = DatabaseBuilder()
    builder.build_database()

    conn = sqlite3.connect('db/nifty100.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]
    print(f"Built Tables ({len(tables)}):", sorted(tables))
    for t in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  - Table {t}: {cursor.fetchone()[0]} rows")
    conn.close()

if __name__ == "__main__":
    main()

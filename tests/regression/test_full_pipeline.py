import os
import sqlite3
from db.loader import DatabaseBuilder

def test_full_pipeline_build():
    builder = DatabaseBuilder(db_path="db/nifty100.db")
    builder.build_database()

    assert os.path.exists("db/nifty100.db")

    conn = sqlite3.connect("db/nifty100.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM companies")
    comp_cnt = cursor.fetchone()[0]
    conn.close()

    assert comp_cnt == 92

import sqlite3

conn = sqlite3.connect('backend/db.sqlite3')
cursor = conn.cursor()

# Get all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", [t[0] for t in tables])

# Search for user/accounts tables
user_tables = [t[0] for t in tables if 'user' in t[0] or 'account' in t[0]]
print("User-related tables:", user_tables)

for table in user_tables:
    try:
        columns = [c[1] for c in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
        print(f"\nColumns in {table}:", columns)
        rows = cursor.execute(f"SELECT * FROM {table}").fetchall()
        print(f"Rows in {table} ({len(rows)}):")
        for r in rows:
            print("  ", r)
    except Exception as e:
        print(f"Error reading {table}: {e}")

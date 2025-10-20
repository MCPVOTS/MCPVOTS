import sqlite3
import os

db_path = 'ethermax_whales.db'
print(f'Database exists: {os.path.exists(db_path)}')
print(f'Database size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes')
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'Tables ({len(tables)}):')
for table in tables:
    print(f'  - {table[0]}')
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f'    Records: {count}')

print()

# Check our_trades table structure
cursor.execute("PRAGMA table_info(our_trades)")
columns = cursor.fetchall()
print('our_trades table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print()

# Check if there are any trades
cursor.execute("SELECT * FROM our_trades ORDER BY timestamp DESC LIMIT 1")
last_trade = cursor.fetchone()
if last_trade:
    print(f'Last trade: {last_trade}')
else:
    print('No trades yet (bot will start logging when it trades)')

conn.close()
print()
print('✓ Database is working and ready!')

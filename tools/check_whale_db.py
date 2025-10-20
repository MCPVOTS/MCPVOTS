import sqlite3

db = sqlite3.connect('data/ethermax_whales.db')
cursor = db.cursor()

print('='*60)
print('ETHERMAX WHALE DATABASE STATUS')
print('='*60)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f'\nTables: {tables}')

cursor.execute('SELECT COUNT(*) FROM whale_wallets')
print(f'Whales tracked: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM whale_trades')
print(f'Trades logged: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM trading_patterns')
print(f'Patterns detected: {cursor.fetchone()[0]}')

db.close()
print('='*60)

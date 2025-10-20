#!/usr/bin/env python3
"""
Script to read memories from the MAXX MCP memory database
"""

import sqlite3
import json
from datetime import datetime

def read_memories():
    # Connect to the memory database
    conn = sqlite3.connect('data/maxx_memory.db')
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_vectors'")
    if not cursor.fetchone():
        print('❌ No memory_vectors table found. Database may be empty.')
        conn.close()
        return

    # Get total count
    cursor.execute('SELECT COUNT(*) FROM memory_vectors')
    count = cursor.fetchone()[0]
    print(f'📊 Total memories stored: {count}')
    print()

    # Query all memories
    cursor.execute('SELECT id, content, metadata, timestamp, category FROM memory_vectors ORDER BY timestamp DESC LIMIT 20')
    rows = cursor.fetchall()

    if not rows:
        print('📭 No memories found in the database.')
    else:
        print('🧠 Recent memories:')
        print('=' * 80)

        for row in rows:
            memory_id, content, metadata_json, timestamp, category = row
            metadata = json.loads(metadata_json) if metadata_json else {}
            dt = datetime.fromtimestamp(timestamp)

            print(f'🆔 ID: {memory_id}')
            print(f'📁 Category: {category}')
            print(f'🕒 Time: {dt.strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'📝 Content: {content[:200]}...' if len(content) > 200 else f'📝 Content: {content}')
            if metadata:
                print(f'🏷️  Metadata: {json.dumps(metadata, indent=2)}')
            print('-' * 40)

    # Show category breakdown
    print()
    print('📈 Category breakdown:')
    cursor.execute('SELECT category, COUNT(*) FROM memory_vectors GROUP BY category ORDER BY COUNT(*) DESC')
    categories = cursor.fetchall()
    for category, count in categories:
        print(f'  {category}: {count} memories')

    conn.close()

if __name__ == "__main__":
    read_memories()

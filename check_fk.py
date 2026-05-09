import sqlite3

conn = sqlite3.connect("data/zalpha_metadata.db")
cursor = conn.cursor()

print("=== gates 表外键 ===")
cursor.execute("PRAGMA foreign_key_list(gates)")
fks = cursor.fetchall()
for fk in fks:
    print(f"  FK: id={fk[0]}, seq={fk[1]}, table='{fk[2]}', from='{fk[3]}', to='{fk[4]}', on_update={fk[5]}, on_delete={fk[6]}, match={fk[7]}")

print("\n=== task_files 表外键 ===")
cursor.execute("PRAGMA foreign_key_list(task_files)")
fks = cursor.fetchall()
for fk in fks:
    print(f"  FK: id={fk[0]}, seq={fk[1]}, table='{fk[2]}', from='{fk[3]}', to='{fk[4]}', on_update={fk[5]}, on_delete={fk[6]}, match={fk[7]}")

print("\n=== events 表外键 ===")
cursor.execute("PRAGMA foreign_key_list(events)")
fks = cursor.fetchall()
for fk in fks:
    print(f"  FK: id={fk[0]}, seq={fk[1]}, table='{fk[2]}', from='{fk[3]}', to='{fk[4]}', on_update={fk[5]}, on_delete={fk[6]}, match={fk[7]}")

print("\n=== 所有表的 CREATE SQL（含外键定义）===")
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('gates', 'task_files', 'events')")
for row in cursor.fetchall():
    print(f"\n--- {row[0]} ---")
    print(row[1])

conn.close()

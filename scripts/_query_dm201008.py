"""查询DM-201008任务卡状态."""
import sqlite3

DB_PATH = r"D:\ZephyrAlpha\data\databases\governance.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(tasks)")
    cols = cur.fetchall()
    print("tasks columns:")
    for c in cols:
        print(f"  {c[1]} ({c[2]})")

    cur.execute("SELECT task_id, title, status, completed_at FROM tasks WHERE task_id = 'DM-201008'")
    row = cur.fetchone()
    if row:
        print(f"\nTask: {row[0]}")
        print(f"  Title: {row[1]}")
        print(f"  Status: {row[2]}")
        print(f"  Completed_at: {row[3]}")
    else:
        print("DM-201008 not found")

    conn.close()

if __name__ == "__main__":
    main()

import sqlite3
conn = sqlite3.connect("data/e2e_test/vms_metadata.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT rowid, content, collection FROM vms_documents LIMIT 5").fetchall()
print("=== vms_documents ===")
for r in rows:
    print(f"  rowid={r['rowid']} col={r['collection']} content={r['content'][:60]}")
fts_count = conn.execute("SELECT COUNT(*) FROM vms_documents_fts").fetchone()[0]
doc_count = conn.execute("SELECT COUNT(*) FROM vms_documents").fetchone()[0]
print(f"\nDocs total: {doc_count}")
print(f"FTS5 total: {fts_count}")
if fts_count > 0:
    hits = conn.execute("SELECT * FROM vms_documents_fts WHERE vms_documents_fts MATCH 'FAISS' LIMIT 5").fetchall()
    print(f"FTS5 MATCH 'FAISS': {len(hits)} hits")
else:
    print("FTS5 is EMPTY - triggers not working!")
    triggers = conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()
    print(f"Triggers: {[t['name'] for t in triggers]}")
conn.close()
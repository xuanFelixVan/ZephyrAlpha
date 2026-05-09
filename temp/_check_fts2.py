import sqlite3
conn = sqlite3.connect("data/e2e_test/vms_metadata.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT content FROM vms_documents WHERE collection='knowledge' AND content LIKE '%FAISS%'").fetchall()
print(f"Docs containing 'FAISS': {len(rows)}")
for r in rows:
    print(f"  {r['content'][:80]}")
fts_hits = conn.execute("SELECT * FROM vms_documents_fts WHERE vms_documents_fts MATCH 'FAISS'").fetchall()
print(f"\nFTS5 MATCH 'FAISS': {len(fts_hits)} hits")
fts_hits2 = conn.execute("SELECT * FROM vms_documents_fts WHERE vms_documents_fts MATCH 'BGE-M3'").fetchall()
print(f"FTS5 MATCH 'BGE-M3': {len(fts_hits2)} hits")
fts_hits3 = conn.execute("SELECT * FROM vms_documents_fts WHERE vms_documents_fts MATCH 'Batch'").fetchall()
print(f"FTS5 MATCH 'Batch': {len(fts_hits3)} hits")
conn.close()
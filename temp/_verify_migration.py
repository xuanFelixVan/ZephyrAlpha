"""Verify migration results"""
import json
import sqlite3

db_path = "data/vector_db/vms_metadata.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

total = conn.execute("SELECT COUNT(*) as cnt FROM vms_documents").fetchone()["cnt"]
print(f"Total documents in SQLite: {total}")

by_collection = conn.execute(
    "SELECT collection, COUNT(*) as cnt FROM vms_documents GROUP BY collection"
).fetchall()
for row in by_collection:
    print(f"  {row['collection']}: {row['cnt']} docs")

dim_mismatch = conn.execute(
    "SELECT COUNT(*) as cnt FROM vms_documents WHERE metadata_json LIKE '%_migration_dim_mismatch%'"
).fetchone()["cnt"]
print(f"\nDimension mismatch (metadata-only): {dim_mismatch}")

migrated = conn.execute(
    "SELECT COUNT(*) as cnt FROM vms_documents WHERE metadata_json LIKE '%migrated_from_chromadb%'"
).fetchone()["cnt"]
print(f"Migrated from ChromaDB: {migrated}")

kb_migrated = conn.execute(
    "SELECT COUNT(*) as cnt FROM vms_documents WHERE metadata_json LIKE '%migrated_from_kb_collection%'"
).fetchone()["cnt"]
print(f"Migrated from KB ChromaDB: {kb_migrated}")

fts_count = conn.execute(
    "SELECT COUNT(*) as cnt FROM vms_documents_fts"
).fetchone()["cnt"]
print(f"\nFTS5 index entries: {fts_count}")

sample = conn.execute(
    "SELECT vector_id, content, metadata_json FROM vms_documents LIMIT 3"
).fetchall()
print("\nSample documents:")
for row in sample:
    meta = json.loads(row["metadata_json"])
    print(f"  ID={row['vector_id']}")
    print(f"    content: {row['content'][:80]}")
    print(f"    origin: {meta.get('origin', meta.get('provenance', {}).get('origin', 'N/A'))}")
    print(f"    migrated: {meta.get('migrated_from_chromadb', False)}")

conn.close()
print("\nVerification complete.")
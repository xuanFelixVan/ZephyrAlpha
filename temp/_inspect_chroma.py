import chromadb

client = chromadb.PersistentClient(path="data/vector_db")
col = client.get_collection("knowledge")
data = col.get(include=["documents", "metadatas", "embeddings"], limit=2)
print("=== VMS knowledge (sample) ===")
print(f"Total: {col.count()}")
print(f"IDs: {data['ids']}")
print(f"Docs: {[d[:60] for d in data['documents']]}")
print(f"Metadatas keys: {[list(m.keys()) for m in data['metadatas']]}")
print(f"Embedding dim: {len(data['embeddings'][0]) if data['embeddings'] else 0}")

from zephyr.shared.io.paths import VECTOR_INDEX_DIR
kb_client = chromadb.PersistentClient(path=str(VECTOR_INDEX_DIR))
kb_col = kb_client.get_collection("ke_entries")
kb_data = kb_col.get(include=["documents", "metadatas", "embeddings"], limit=2)
print()
print("=== KB ke_entries (sample) ===")
print(f"Total: {kb_col.count()}")
print(f"IDs: {kb_data['ids']}")
print(f"Docs: {[d[:60] for d in kb_data['documents']]}")
print(f"Metadatas keys: {[list(m.keys()) for m in kb_data['metadatas']]}")
print(f"Embedding dim: {len(kb_data['embeddings'][0]) if kb_data['embeddings'] else 0}")
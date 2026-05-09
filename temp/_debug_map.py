import sys, shutil
sys.path.insert(0, "src")
from pathlib import Path

p = Path("data/debug_map")
if p.exists():
    shutil.rmtree(p)
p.mkdir()

from zephyr.vector_memory.in_process_vector_memory import InProcessVectorMemory

vms = InProcessVectorMemory(persist_dir=str(p))
vms.start()
vms.init_all_collections()

docs = [
    ("采用 FAISS mmap 替代 ChromaDB", {"provenance": {"origin": "test"}}),
    ("部署 v2.3.1 到生产环境", {"provenance": {"origin": "test"}}),
    ("归并排序 O(n log n)", {"provenance": {"origin": "test"}}),
]
vids = []
for content, meta in docs:
    vid = vms.write("knowledge", content, meta)
    vids.append(vid)
    print(f"  wrote: vid={vid}, content={content[:30]}")

store = vms._metadata_store
print("\nID map:")
for row in store._conn.execute("SELECT * FROM vms_id_map").fetchall():
    print(f"  faiss_id={row[0]} vector_id={row[1]} collection={row[2]}")

print("\nDocuments:")
for row in store._conn.execute("SELECT vector_id, content FROM vms_documents").fetchall():
    print(f"  vid={row[0]} content={row[1][:30]}")

er = vms._embedding_router
import numpy as np
query_vec = er.embed("数据库迁移方案", "knowledge")
distances, ids = vms._collection_manager.search("knowledge", query_vec, k=3)
print(f"\nFAISS search: ids={list(ids)}, distances={[f'{d:.4f}' for d in distances]}")

faiss_ids = [int(fid) for fid in ids if fid >= 0]
id_map = store.get_vector_ids_by_faiss_ids(faiss_ids, "knowledge")
print(f"ID map lookup: {id_map}")

vms.shutdown()
shutil.rmtree(p, ignore_errors=True)
import sys, shutil
sys.path.insert(0, "src")
from pathlib import Path
import numpy as np

p = Path("data/debug_search")
if p.exists():
    shutil.rmtree(p)
p.mkdir()

from zephyr.vector_memory.in_process_vector_memory import InProcessVectorMemory

vms = InProcessVectorMemory(persist_dir=str(p))
vms.start()

er = vms._embedding_router
print(f"BGE-M3: {er.bge_m3_available}, dim={er.bge_m3_dim}")
print(f"bge-small: {er.bge_small_available}, dim={er.bge_small_dim}")

vms.init_all_collections()

doc1 = "采用 FAISS mmap 替代 ChromaDB 作为向量数据库后端"
doc2 = "部署 v2.3.1 到生产环境，使用零停机滚动更新策略"
doc3 = "归并排序在所有情况下都具有 O(n log n) 时间复杂度"

vms.write("knowledge", doc1, {"provenance": {"origin": "test"}})
vms.write("knowledge", doc2, {"provenance": {"origin": "test"}})
vms.write("knowledge", doc3, {"provenance": {"origin": "test"}})

print(f"\nFAISS count: {vms._collection_manager.count('knowledge')}")

query = "数据库迁移方案"
query_vec = er.embed(query, "knowledge")
print(f"\nQuery: '{query}' → embedding dim={query_vec.shape[0]}, norm={float(query_vec.dot(query_vec)):.4f}")

doc1_vec = er.embed(doc1, "knowledge")
doc2_vec = er.embed(doc2, "knowledge")
doc3_vec = er.embed(doc3, "knowledge")

cos1 = float(query_vec.dot(doc1_vec))
cos2 = float(query_vec.dot(doc2_vec))
cos3 = float(query_vec.dot(doc3_vec))
print(f"\nDirect cosine similarity:")
print(f"  query vs doc1 (FAISS/数据库): {cos1:.4f}")
print(f"  query vs doc2 (部署/生产):    {cos2:.4f}")
print(f"  query vs doc3 (归并排序):     {cos3:.4f}")

distances, ids = vms._collection_manager.search("knowledge", query_vec, k=3)
print(f"\nFAISS search results:")
for i in range(len(ids)):
    if ids[i] >= 0:
        print(f"  id={ids[i]}, distance={distances[i]:.4f}")

vms.shutdown()
shutil.rmtree(p, ignore_errors=True)
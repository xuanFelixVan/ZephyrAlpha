import sys, shutil
sys.path.insert(0, "src")
from pathlib import Path
import numpy as np

p = Path("data/debug_rrf")
if p.exists():
    shutil.rmtree(p)
p.mkdir()

from zephyr.vector_memory.in_process_vector_memory import InProcessVectorMemory

vms = InProcessVectorMemory(persist_dir=str(p))
vms.start()
vms.init_all_collections()

docs = [
    ("采用 FAISS mmap 替代 ChromaDB 作为向量数据库后端", {"provenance": {"origin": "test"}}),
    ("部署 v2.3.1 到生产环境，使用零停机滚动更新策略", {"provenance": {"origin": "test"}}),
    ("归并排序在所有情况下都具有 O(n log n) 时间复杂度", {"provenance": {"origin": "test"}}),
]
for content, meta in docs:
    vms.write("knowledge", content, meta)

from zephyr.vector_memory.hybrid_retriever import HybridRetriever
hr = vms._hybrid_retriever

dense = hr._dense_search("数据库迁移方案", "knowledge", k=10)
print("Dense search results:")
for doc_id, score, meta in dense:
    print(f"  {doc_id}: score={score:.4f}")

sparse = hr._sparse_search("数据库迁移方案", "knowledge", k=10)
print(f"\nSparse search results ({len(sparse)}):")
for doc_id, score, meta in sparse:
    print(f"  {doc_id}: score={score:.4f}")

fused = hr._rrf_fusion(dense, sparse, "knowledge")
print("\nRRF fused results:")
for doc_id, score, breakdown, meta in fused:
    print(f"  {doc_id}: rrf={score:.6f} dense={breakdown.get('dense',0):.4f} sparse={breakdown.get('sparse',0):.4f}")

vms.shutdown()
shutil.rmtree(p, ignore_errors=True)
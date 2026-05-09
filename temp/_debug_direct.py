import sys, shutil
sys.path.insert(0, "src")
from pathlib import Path

p = Path("data/debug_direct")
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

vms._hybrid_retriever = None

print("=== Direct FAISS search (bypassing HybridRetriever) ===")
results = vms.search("knowledge", "数据库迁移方案", k=3)
for r in results:
    print(f"  score={r['score']:.4f} | {r['content'][:50]}")

print()
results2 = vms.search("knowledge", "sorting algorithm", k=3)
for r in results2:
    print(f"  score={r['score']:.4f} | {r['content'][:50]}")

vms.shutdown()
shutil.rmtree(p, ignore_errors=True)
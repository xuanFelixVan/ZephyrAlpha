# [A_test] module_id: SRC-TST-0087 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-245 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.benchmarks.test_vms_full_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
FAISS + SQLite WAL 端到端完整测试
==================================
覆盖:
  1. VMS 启动 + 嵌入模型状态
  2. 8 Collection 初始化
  3. 单条写入 (含 provenance 校验)
  4. 批量写入 (add_vectors_batch)
  5. 密集向量搜索 (FAISS HNSW)
  6. 全文搜索 (SQLite FTS5 BM25)
  7. 混合检索 (HybridRetriever RRF)
  8. 元数据回调 (recall)
  9. IVF+PQ 索引创建 + 训练 + 搜索
  10. 健康检查
  11. 数据完整性 (FAISS/SQLite/ID Map 三方一致)
  12. 并发写入 (10 线程)
  13. 存储占用
  14. 关机
"""

from __future__ import annotations

import shutil
import sys
import threading
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_DIR = Path("data/e2e_test")
PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def fmt(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}us"
    if seconds < 1.0:
        return f"{seconds * 1000:.1f}ms"
    return f"{seconds:.2f}s"


def main():
    global PASS, FAIL

    print("=" * 72)
    print("  FAISS + SQLite WAL 端到端完整测试")
    print("=" * 72)

    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True)

    # =========================================================================
    # 1. VMS 启动
    # =========================================================================
    print("\n[1] VMS 启动 + 嵌入模型状态...")

    from zephyr.governance.vector_memory.in_process_vector_memory import InProcessVectorMemory

    vms = InProcessVectorMemory(persist_dir=str(TEST_DIR))
    t0 = time.perf_counter()
    vms.start()
    startup_time = time.perf_counter() - t0
    print(f"  启动耗时: {fmt(startup_time)}")

    embed_status = vms.health_check()
    check("VMS 启动成功", vms._started)
    check("嵌入模型状态可查", "embedding" in embed_status)
    print(f"  嵌入模式: {embed_status.get('embedding', 'unknown')}")
    print(f"  降级模式: {embed_status.get('degraded', 'unknown')}")

    # =========================================================================
    # 2. 8 Collection 初始化
    # =========================================================================
    print("\n[2] 8 Collection 初始化...")
    infos = vms.init_all_collections()
    check("8 Collection 全部创建", len(infos) == 8)
    for info in infos:
        check(f"  {info.name} ({info.dimension}d)", info.exists)

    # =========================================================================
    # 3. 单条写入
    # =========================================================================
    print("\n[3] 单条写入 (含 provenance)...")

    write_data = {
        "decisions": (
            "ADR-0032: 采用 FAISS mmap 替代 ChromaDB HTTP 微服务",
            {"provenance": {"origin": "architect", "source": "ADR-0032"}},
        ),
        "code_context": (
            "def search_hybrid(query, k=5): return retriever.search(query, k)",
            {"provenance": {"origin": "coder", "source": "hybrid_retriever.py"}},
        ),
        "lessons": (
            "FAISS mmap 多进程共享时，写入必须落盘才能被其他进程看到",
            {"provenance": {"origin": "engineer", "source": "incident-2026-05-09"}},
        ),
        "knowledge": (
            "BGE-M3 是 BAAI 发布的多语言嵌入模型，输出 1024 维向量",
            {"provenance": {"origin": "researcher", "source": "BAAI/bge-m3"}},
        ),
        "rules": (
            "所有 VMS 写入必须包含 provenance.origin 字段",
            {"provenance": {"origin": "governance", "source": "rule-G-001"}},
        ),
        "blueprints": (
            "VMS 蓝图 §12 定义了 ChromaDB → FAISS 的 6 步迁移方案",
            {"provenance": {"origin": "architect", "source": "VMS-blueprint"}},
        ),
        "session_snapshots": (
            "2026-05-09 Phase 2 施工完成，122/122 测试通过",
            {"provenance": {"origin": "agent", "source": "session-20260509"}},
        ),
        "execution_traces": (
            "task-migrate-chroma2faiss completed in 3.2s with 0 errors",
            {"provenance": {"origin": "orchestrator", "source": "task-migrate"}},
        ),
    }

    write_times = []
    for name, (content, meta) in write_data.items():
        t0 = time.perf_counter()
        vid = vms.write(name, content, meta)
        t = time.perf_counter() - t0
        write_times.append(t)
        check(f"write({name})", vid is not None, f"vid={vid}")

    avg_write = sum(write_times) / len(write_times)
    print(f"  平均写入延迟: {fmt(avg_write)}")

    # =========================================================================
    # 4. 批量写入
    # =========================================================================
    print("\n[4] 批量写入 (add_vectors_batch)...")

    from zephyr.governance.vector_memory.faiss_collection_manager import FAISSCollectionManager

    faiss_cm = vms._collection_manager
    meta_store = vms._metadata_store

    batch_vectors = np.random.randn(200, 1024).astype(np.float32)
    batch_vectors /= np.linalg.norm(batch_vectors, axis=1, keepdims=True) + 1e-8

    t0 = time.perf_counter()
    faiss_cm.add_vectors_batch("knowledge", batch_vectors)
    batch_time = time.perf_counter() - t0

    for i in range(200):
        vid = f"knowledge::batch::{i}"
        meta_store.add_document(
            vector_id=vid,
            collection="knowledge",
            content=f"Batch doc {i}: random knowledge entry",
            metadata={"batch_idx": i, "source": "batch_test"},
            provenance={"origin": "benchmark_batch"},
        )
        faiss_id = meta_store.get_faiss_id("knowledge")
        meta_store.map_id(vid, faiss_id, "knowledge")

    check("批量写入 200 条", batch_time < 1.0, f"time={fmt(batch_time)}")
    print(f"  批量写入 200 条: {fmt(batch_time)} ({200 / batch_time:.0f} docs/s)")

    # =========================================================================
    # 5. 密集向量搜索
    # =========================================================================
    print("\n[5] 密集向量搜索 (FAISS HNSW)...")

    query_vec = np.random.randn(1024).astype(np.float32)
    query_vec /= np.linalg.norm(query_vec) + 1e-8

    search_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        distances, ids = faiss_cm.search("knowledge", query_vec, k=10)
        search_times.append(time.perf_counter() - t0)

    avg_search = sum(search_times) / len(search_times)
    has_results = any(fid >= 0 for fid in ids)
    check("向量搜索返回结果", has_results, f"ntotal={faiss_cm.count('knowledge')}")
    check("搜索延迟 < 1ms", avg_search < 0.001, f"avg={fmt(avg_search)}")
    print(f"  平均搜索延迟: {fmt(avg_search)} (k=10, 100次)")

    # =========================================================================
    # 6. 全文搜索 (FTS5 BM25)
    # =========================================================================
    print("\n[6] 全文搜索 (SQLite FTS5 BM25)...")

    fts_tests = [
        ("BGE-M3", "knowledge", True),
        ("provenance", "rules", True),
        ("蓝图", "blueprints", True),
        ("nonexistent_xyz_12345", "knowledge", False),
    ]

    for query, collection, expect_hits in fts_tests:
        t0 = time.perf_counter()
        hits = meta_store.search_fts(query, collection, k=10)
        t = time.perf_counter() - t0
        found = len(hits) > 0
        check(
            f"FTS5 '{query}' → {collection}",
            found == expect_hits,
            f"hits={len(hits)}, expect={expect_hits}, time={fmt(t)}",
        )

    # =========================================================================
    # 7. 混合检索 (HybridRetriever)
    # =========================================================================
    print("\n[7] 混合检索 (HybridRetriever RRF)...")

    try:
        from zephyr.governance.vector_memory.hybrid_retriever import HybridRetriever

        embed_router = vms._embedding_router
        retriever = HybridRetriever(faiss_cm, embed_router, meta_store)

        t0 = time.perf_counter()
        trace = retriever.search("FAISS mmap 替代 ChromaDB", "knowledge", k=10)
        hybrid_time = time.perf_counter() - t0

        check("混合检索返回 SearchTrace", trace is not None)
        check("混合检索延迟 < 100ms", hybrid_time < 0.1, f"time={fmt(hybrid_time)}")
        print(f"  混合检索延迟: {fmt(hybrid_time)}")
        print(f"  结果数: {len(trace.results) if hasattr(trace, 'results') else 'N/A'}")
    except Exception as e:
        check("混合检索", False, str(e))

    # =========================================================================
    # 8. 元数据回调 (recall)
    # =========================================================================
    print("\n[8] 元数据回调 (recall)...")

    for name in ["decisions", "knowledge", "rules"]:
        results = vms.recall(name, k=5)
        check(f"recall({name})", len(results) > 0, f"count={len(results)}")
        if results:
            has_meta = "metadata" in results[0] or "id" in results[0]
            check("  recall 结果含元数据", has_meta)

    # =========================================================================
    # 9. IVF+PQ 索引
    # =========================================================================
    print("\n[9] IVF+PQ 索引创建 + 训练 + 搜索...")

    ivf_dir = TEST_DIR / "ivf_test"
    ivf_dir.mkdir(exist_ok=True)
    ivf_cm = FAISSCollectionManager(str(ivf_dir))

    ivf_cm.create_collection("knowledge", dim=1024, index_type="ivf_pq", strict=False)
    check("IVF+PQ Collection 创建", True)

    train_vecs = np.random.randn(5000, 1024).astype(np.float32)
    train_vecs /= np.linalg.norm(train_vecs, axis=1, keepdims=True) + 1e-8

    t0 = time.perf_counter()
    ivf_cm.add_vectors_batch("knowledge", train_vecs)
    ivf_write_time = time.perf_counter() - t0
    check(
        "IVF+PQ 批量写入 5000 条",
        ivf_cm.count("knowledge") == 5000,
        f"count={ivf_cm.count('knowledge')}, time={fmt(ivf_write_time)}",
    )

    query_ivf = np.random.randn(1024).astype(np.float32)
    query_ivf /= np.linalg.norm(query_ivf) + 1e-8

    t0 = time.perf_counter()
    for _ in range(100):
        distances, ids = ivf_cm.search("knowledge", query_ivf, k=10)
    ivf_search_time = (time.perf_counter() - t0) / 100
    has_ivf_results = any(fid >= 0 for fid in ids)
    check("IVF+PQ 搜索返回结果", has_ivf_results)
    print(f"  IVF+PQ 搜索延迟: {fmt(ivf_search_time)} (5000 vecs, k=10)")

    hnsw_cm = FAISSCollectionManager(str(ivf_dir / "hnsw_ref"))
    hnsw_cm.create_collection("knowledge", dim=1024, index_type="hnsw", strict=False)
    hnsw_cm.add_vectors_batch("knowledge", train_vecs)
    t0 = time.perf_counter()
    for _ in range(100):
        hnsw_cm.search("knowledge", query_ivf, k=10)
    hnsw_search_time = (time.perf_counter() - t0) / 100
    print(f"  HNSW   搜索延迟: {fmt(hnsw_search_time)} (5000 vecs, k=10)")

    ivf_size = (ivf_dir / "knowledge.index").stat().st_size / (1024 * 1024)
    hnsw_size = (ivf_dir / "hnsw_ref" / "knowledge.index").stat().st_size / (1024 * 1024)
    print(f"  IVF+PQ 索引大小: {ivf_size:.2f} MB")
    print(f"  HNSW   索引大小: {hnsw_size:.2f} MB")
    print(f"  压缩比: {hnsw_size / ivf_size:.1f}x")

    # =========================================================================
    # 10. 健康检查
    # =========================================================================
    print("\n[10] 健康检查...")

    health = vms.health_check()
    check("health_check 返回 status", "status" in health)
    check("health_check 返回 embedding", "embedding" in health)
    check("status = healthy", health.get("status") == "healthy", f"status={health.get('status')}")
    print(f"  status: {health.get('status')}")
    print(f"  embedding: {health.get('embedding')}")

    faiss_health = faiss_cm.health_check()
    check("FAISS health_check 含 collections", "collections" in faiss_health)
    check("FAISS health_check 含 GPU 信息", "gpu" in faiss_health)
    print(f"  GPU: {faiss_health.get('gpu')}")

    # =========================================================================
    # 11. 数据完整性
    # =========================================================================
    print("\n[11] 数据完整性 (FAISS/SQLite/ID Map)...")

    for name in ["decisions", "knowledge", "rules"]:
        faiss_count = faiss_cm.count(name)
        sqlite_count = meta_store.count_by_collection(name)
        map_count = meta_store._conn.execute("SELECT COUNT(*) FROM vms_id_map WHERE collection=?", (name,)).fetchone()[
            0
        ]
        match = faiss_count == sqlite_count == map_count
        check(f"  {name}: FAISS={faiss_count} SQLite={sqlite_count} Map={map_count}", match, "mismatch!")

    # =========================================================================
    # 12. 并发写入
    # =========================================================================
    print("\n[12] 并发写入 (10 线程)...")

    results_lock = threading.Lock()
    agent_results = []

    def agent_worker(agent_id: int):
        for i in range(5):
            content = f"Agent-{agent_id} task-{i}: concurrent write test"
            meta = {"provenance": {"origin": f"agent_{agent_id}", "source": "concurrent_test"}}
            try:
                t0 = time.perf_counter()
                vid = vms.write("knowledge", content, meta)
                t = time.perf_counter() - t0
                with results_lock:
                    agent_results.append((agent_id, True, t, vid))
            except Exception as e:
                with results_lock:
                    agent_results.append((agent_id, False, 0, str(e)))

    threads = []
    t0 = time.perf_counter()
    for aid in range(10):
        t = threading.Thread(target=agent_worker, args=(aid,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    concurrent_time = time.perf_counter() - t0

    success = sum(1 for r in agent_results if r[1])
    fail = sum(1 for r in agent_results if not r[1])
    latencies = [r[2] for r in agent_results if r[1]]
    check("10 线程并发写入零失败", fail == 0, f"fail={fail}")
    check("并发写入全部成功", success == 50, f"success={success}/50")
    print(f"  总耗时: {fmt(concurrent_time)}")
    if latencies:
        print(f"  平均延迟: {fmt(sum(latencies) / len(latencies))}")
        print(f"  最大延迟: {fmt(max(latencies))}")

    # =========================================================================
    # 13. 存储占用
    # =========================================================================
    print("\n[13] 存储占用...")

    total_size = 0
    for f in sorted(TEST_DIR.rglob("*")):
        if f.is_file():
            size = f.stat().st_size
            total_size += size

    total_mb = total_size / (1024 * 1024)
    print(f"  总存储: {total_mb:.2f} MB")

    # =========================================================================
    # 14. 关机
    # =========================================================================
    print("\n[14] 关机...")
    vms.shutdown()
    check("VMS 关机成功", not vms._started)

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 72)
    print(f"  端到端测试完成: {PASS} passed, {FAIL} failed")
    print("=" * 72)

    shutil.rmtree(TEST_DIR, ignore_errors=True)
    return FAIL == 0


def test_vms_full_e2e():
    """FAISS+SQLite WAL 端到端完整测试——委托给 main()，pytest 收集入口。"""
    assert main() is True


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)

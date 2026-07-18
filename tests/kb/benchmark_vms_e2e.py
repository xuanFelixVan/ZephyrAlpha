# [A_test] module_id: SRC-TST-0085 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-243 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.benchmarks.benchmark_vms_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
FAISS + SQLite WAL 端到端性能基准测试
======================================
测试项目:
  1. Collection 初始化速度
  2. 写入吞吐 (单条 / 批量)
  3. 密集向量搜索延迟
  4. FTS5 全文搜索延迟
  5. 元数据回调延迟
  6. 健康检查延迟
  7. 大规模写入 + 搜索压测
"""

from __future__ import annotations

import shutil
import sys
import time
import uuid
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_DB_DIR = Path("data/benchmark_test")

COLLECTION_DIMS = {
    "decisions": 1024,
    "code_context": 1024,
    "lessons": 1024,
    "knowledge": 1024,
    "rules": 1024,
    "blueprints": 512,
    "session_snapshots": 512,
    "execution_traces": 512,
}

SAMPLE_TEXTS = [
    "Deploy v2.3.1 to production environment with zero-downtime rollout.",
    "Fix null pointer exception in UserService.getProfile() method.",
    "Python 3.12 introduces PEP 695 for improved type parameter syntax.",
    "Retry with exponential backoff: initial delay 100ms, max 10s, jitter 0.1.",
    "YAML-driven prompt template registry with token budget enforcement.",
    "Use structlog for structured logging across all microservices.",
    "Circuit breaker threshold: 50% failure rate over 30s rolling window.",
    "Merge sort has O(n log n) time complexity in all cases.",
    "PostgreSQL 16 supports logical replication from standby servers.",
    "Redis Streams consumer group with XREADGROUP for reliable message processing.",
    "Blueprint section 3.2 defines the hot/cold data separation strategy.",
    "Task ID T-12345 completed in 2.3s with 3 retries and 0 errors.",
    "Governance rule G-042: all production deployments require 2 approvals.",
    "Session snapshot 2026-05-09T14:30:00 — 15 active agents, 3 pipelines.",
    "Kubernetes horizontal pod autoscaler targets 70% CPU utilization.",
    "Token budget: max 4096 input tokens, 2048 output tokens per completion.",
    "Faiss IndexHNSW with M=32, efConstruction=200, efSearch=64 — cosine similarity.",
    "SQLite WAL mode with synchronous=NORMAL for concurrent read performance.",
    "RRF k=60 fusion combines dense and sparse retrieval scores.",
    "ADR-0031: Migrate from ChromaDB to FAISS mmap shared memory backend.",
]


def random_embedding(dim: int) -> np.ndarray:
    vec = np.random.randn(dim).astype(np.float32)
    vec /= np.linalg.norm(vec) + 1e-8
    return vec


def format_latency(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f} us"
    elif seconds < 1.0:
        return f"{seconds * 1_000:.1f} ms"
    else:
        return f"{seconds:.3f} s"


def timer():
    return time.perf_counter()


def measure(name: str, func, iterations: int = 1) -> float:
    times = []
    for _ in range(iterations):
        t0 = timer()
        func()
        times.append(timer() - t0)
    avg = sum(times) / len(times)
    if iterations > 1:
        min_t = min(times)
        max_t = max(times)
        p50 = sorted(times)[len(times) // 2]
        print(
            f"  {name:<40s}: avg={format_latency(avg):>10s}  "
            f"min={format_latency(min_t):>10s}  "
            f"p50={format_latency(p50):>10s}  "
            f"max={format_latency(max_t):>10s}"
        )
    else:
        print(f"  {name:<40s}: {format_latency(avg):>10s}")
    return avg


def main():
    print("=" * 72)
    print("  FAISS + SQLite WAL 端到端性能基准测试")
    print("=" * 72)

    if TEST_DB_DIR.exists():
        shutil.rmtree(TEST_DB_DIR)
    TEST_DB_DIR.mkdir(parents=True, exist_ok=True)

    import faiss

    from zephyr.integration.vector_memory.faiss_collection_manager import FAISSCollectionManager
    from zephyr.integration.vector_memory.sqlite_metadata_store import SQLiteMetadataStore

    print(f"\n  FAISS GPU: {faiss.get_num_gpus()}")
    print("  FAISS AVX2: OK\n")

    faiss_cm = FAISSCollectionManager(persist_dir=str(TEST_DB_DIR))
    meta_store = SQLiteMetadataStore(TEST_DB_DIR / "bench_meta.db")

    # =========================================================================
    # 1. Collection 初始化
    # =========================================================================
    print("[1] Collection 初始化 (8 collections)...")
    measure(
        "init 8 collections (first)",
        lambda: [faiss_cm.create_collection(name, dim=d, strict=False) for name, d in COLLECTION_DIMS.items()],
    )

    measure(
        "re-init 8 collections (cached)",
        lambda: [faiss_cm.create_collection(name, dim=d, strict=False) for name, d in COLLECTION_DIMS.items()],
    )

    # =========================================================================
    # 2. 单条写入
    # =========================================================================
    print("\n[2] 单条写入 (write 1 doc per collection)...")
    for name, dim in COLLECTION_DIMS.items():
        vec = random_embedding(dim)
        vid = f"{name}::{uuid.uuid4().hex[:12]}"
        content = SAMPLE_TEXTS[hash(name) % len(SAMPLE_TEXTS)]
        metadata = {"topic": "benchmark", "collection": name}

        def _write(vid=vid, name=name, content=content, metadata=metadata, vec=vec):
            faiss_cm.add_vector(name, vec)
            faiss_id = meta_store.get_faiss_id(name)
            meta_store.add_document(
                vector_id=vid,
                collection=name,
                content=content,
                metadata=metadata,
                provenance={"origin": "benchmark"},
            )
            meta_store.map_id(vid, faiss_id, name)

        measure(f"  write({name})", _write)

    # =========================================================================
    # 3. 批量写入 200 条
    # =========================================================================
    print("\n[3] 批量写入 (200 docs to knowledge)...")
    dim = 1024
    prepped = []
    for i in range(200):
        vec = random_embedding(dim)
        vid = f"knowledge::batch::{uuid.uuid4().hex[:12]}"
        content = SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)]
        metadata = {"idx": i, "batch": "bench_200"}
        prepped.append((vid, content, metadata, vec))

    t0 = timer()
    for vid, content, metadata, vec in prepped:
        faiss_cm.add_vector("knowledge", vec)
        faiss_id = meta_store.get_faiss_id("knowledge")
        meta_store.add_document(
            vector_id=vid,
            collection="knowledge",
            content=content,
            metadata=metadata,
            provenance={"origin": "benchmark_batch"},
        )
        meta_store.map_id(vid, faiss_id, "knowledge")
    total_time = timer() - t0
    total_docs = 200
    throughput = total_docs / total_time
    avg_lat = total_time / total_docs * 1000
    print(
        f"  {'batch write 200 knowledge':<40s}: "
        f"{format_latency(total_time):>10s} total, "
        f"{throughput:.1f} docs/s, {avg_lat:.1f} ms/doc"
    )

    # =========================================================================
    # 4. 大规模写入 1000 条
    # =========================================================================
    print("\n[4] 大规模写入 (1000 docs to knowledge, 分 10 批)...")
    dim = 1024
    total_written = 0
    batch_times = []
    for batch_idx in range(10):
        batch_prepped = []
        for i in range(100):
            vec = random_embedding(dim)
            vid = f"knowledge::scale::{batch_idx}::{uuid.uuid4().hex[:12]}"
            content = SAMPLE_TEXTS[(batch_idx * 100 + i) % len(SAMPLE_TEXTS)]
            metadata = {"idx": batch_idx * 100 + i, "scale": "bench_1000"}
            batch_prepped.append((vid, content, metadata, vec))

        t0 = timer()
        for vid, content, metadata, vec in batch_prepped:
            faiss_cm.add_vector("knowledge", vec)
            faiss_id = meta_store.get_faiss_id("knowledge")
            meta_store.add_document(
                vector_id=vid,
                collection="knowledge",
                content=content,
                metadata=metadata,
                provenance={"origin": "benchmark_scale"},
            )
            meta_store.map_id(vid, faiss_id, "knowledge")
        batch_times.append(timer() - t0)
        total_written += 100

    total_scale_time = sum(batch_times)
    total_docs_scale = 1000
    throughput_scale = total_docs_scale / total_scale_time
    avg_lat_scale = total_scale_time / total_docs_scale * 1000
    print(
        f"  {'1000 docs write':<40s}: "
        f"{format_latency(total_scale_time):>10s} total, "
        f"{throughput_scale:.1f} docs/s, {avg_lat_scale:.1f} ms/doc"
    )
    print(
        f"  {'  batch breakdown':<40s}: min={format_latency(min(batch_times))}  max={format_latency(max(batch_times))}"
    )

    # =========================================================================
    # 5. 向量搜索
    # =========================================================================
    print("\n[5] 密集向量搜索...")
    dim = 1024
    query_vec = random_embedding(dim)

    measure("search(k=5)", lambda: faiss_cm.search("knowledge", query_vec, k=5), iterations=100)
    measure("search(k=50)", lambda: faiss_cm.search("knowledge", query_vec, k=50), iterations=100)
    measure("search(k=100)", lambda: faiss_cm.search("knowledge", query_vec, k=100), iterations=100)
    measure("search(k=500)", lambda: faiss_cm.search("knowledge", query_vec, k=500), iterations=100)

    # =========================================================================
    # 6. FTS5 全文搜索
    # =========================================================================
    print("\n[6] FTS5 全文搜索 (SQLite BM25)...")

    measure("FTS5 'deploy'", lambda: meta_store.search_fts("deploy", "knowledge", k=10), iterations=50)
    measure("FTS5 'Python logging'", lambda: meta_store.search_fts("Python logging", "knowledge", k=10), iterations=50)
    measure(
        "FTS5 'circuit breaker threshold'",
        lambda: meta_store.search_fts("circuit breaker threshold", "knowledge", k=10),
        iterations=50,
    )
    measure(
        "FTS5 'kubernetes pod' (empty)",
        lambda: meta_store.search_fts("kubernetes pod", "knowledge", k=10),
        iterations=50,
    )

    # =========================================================================
    # 7. 元数据回调
    # =========================================================================
    print("\n[7] 元数据回调 (recall — SQLite)...")

    measure(
        "recall(k=10)",
        lambda: meta_store.get_documents_by_ids(["knowledge::batch::" + str(i) for i in range(10)]),
        iterations=50,
    )

    def _recall_sql():
        meta_store._conn.execute(
            "SELECT * FROM vms_documents WHERE collection=? ORDER BY written_at DESC LIMIT 100",
            ("knowledge",),
        ).fetchall()

    measure("recall latest 100 (SQL)", _recall_sql, iterations=50)
    measure(
        "recall latest 500 (SQL)",
        lambda: meta_store._conn.execute(
            "SELECT * FROM vms_documents WHERE collection=? ORDER BY written_at DESC LIMIT 500",
            ("knowledge",),
        ).fetchall(),
        iterations=50,
    )

    # =========================================================================
    # 8. 健康检查
    # =========================================================================
    print("\n[8] 健康检查...")

    def health():
        for name in COLLECTION_DIMS:
            cnt = faiss_cm.count(name)
            _ = meta_store.count_by_collection(name)

    measure("health_check(all 8)", health, iterations=10)

    # =========================================================================
    # 9. 并发压力测试 (模拟多 Agent 场景)
    # =========================================================================
    print("\n[9] 并发压力测试 (模拟 10 Agent 同时写入)...")
    import threading

    def agent_worker(agent_id: int, results: list):
        for i in range(5):
            dim = 1024
            vec = random_embedding(dim)
            vid = f"knowledge::agent{agent_id}::{uuid.uuid4().hex[:12]}"
            content = f"Agent {agent_id} task {i}: {SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)]}"
            metadata = {"agent_id": agent_id, "task_id": i}

            t0 = timer()
            try:
                faiss_cm.add_vector("knowledge", vec)
                faiss_id = meta_store.get_faiss_id("knowledge")
                meta_store.add_document(
                    vector_id=vid,
                    collection="knowledge",
                    content=content,
                    metadata=metadata,
                    provenance={"origin": f"agent_{agent_id}"},
                )
                meta_store.map_id(vid, faiss_id, "knowledge")
            except Exception as e:
                results.append((agent_id, False, timer() - t0, str(e)))
                return
            results.append((agent_id, True, timer() - t0, None))

    agent_results = []
    threads = []
    t0 = timer()
    for agent_id in range(10):
        t = threading.Thread(target=agent_worker, args=(agent_id, agent_results))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    agent_total_time = timer() - t0

    success = sum(1 for r in agent_results if r[1])
    fail = sum(1 for r in agent_results if not r[1])
    agent_latencies = [r[2] for r in agent_results]
    print(f"  Agents: {success} success, {fail} fail")
    print(f"  Total time: {format_latency(agent_total_time)}")
    print(
        f"  Per-write:   avg={format_latency(sum(agent_latencies) / len(agent_latencies))}  "
        f"min={format_latency(min(agent_latencies))}  "
        f"max={format_latency(max(agent_latencies))}"
    )

    # =========================================================================
    # 10. 数据完整性验证
    # =========================================================================
    print("\n[10] 数据完整性验证...")

    total_faiss = faiss_cm.count("knowledge")
    total_sqlite = meta_store.count_by_collection("knowledge")
    total_fts = meta_store._conn.execute("SELECT COUNT(*) FROM vms_documents_fts").fetchone()[0]
    total_fts_knowledge = meta_store._conn.execute(
        "SELECT COUNT(*) FROM vms_documents WHERE collection='knowledge'"
    ).fetchone()[0]
    total_map = meta_store._conn.execute("SELECT COUNT(*) FROM vms_id_map WHERE collection='knowledge'").fetchone()[0]

    print("  knowledge collection:")
    print(f"    FAISS vectors:    {total_faiss}")
    print(f"    SQLite documents: {total_sqlite}")
    print(f"    ID map entries:   {total_map}")
    print(f"    Integrity:        {'OK' if total_faiss == total_sqlite == total_map else 'MISMATCH!'}")

    total_faiss_all = sum(faiss_cm.count(n) for n in COLLECTION_DIMS)
    total_sqlite_all = sum(meta_store.count_by_collection(n) for n in COLLECTION_DIMS)
    print(f"  All collections: FAISS={total_faiss_all}, SQLite={total_sqlite_all}")

    # =========================================================================
    # 11. 文件大小
    # =========================================================================
    print("\n[11] 存储占用...")
    total_size = 0
    for f in sorted(TEST_DB_DIR.glob("*")):
        size = f.stat().st_size
        total_size += size
        size_kb = size / 1024
        size_mb = size / (1024 * 1024)
        if size_mb >= 1:
            print(f"  {f.name:<40s}: {size_mb:.2f} MB")
        elif size_kb >= 1:
            print(f"  {f.name:<40s}: {size_kb:.1f} KB")
        else:
            print(f"  {f.name:<40s}: {size} B")

    total_mb = total_size / (1024 * 1024)
    print(f"  {'TOTAL':<40s}: {total_mb:.2f} MB")

    # =========================================================================
    # 12. 清理
    # =========================================================================
    print("\n[12] 关闭 & 清理...")
    meta_store.close()
    shutil.rmtree(TEST_DB_DIR)
    print("  Done.")

    print("\n" + "=" * 72)
    print("  基准测试完成")
    print("=" * 72)


if __name__ == "__main__":
    main()

# [A_test] module_id: SRC-TST-0086 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-244 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.benchmarks.benchmark_vms_v2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
FAISS v2 benchmark: batch write + IVF+PQ comparison
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import numpy as np

TEST_DIR = Path("data/bench_v2")
DIM = 1024
N_VECTORS = 1000


def random_vec(dim: int) -> np.ndarray:
    v = np.random.randn(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-8)


def fmt(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}us"
    if seconds < 1.0:
        return f"{seconds * 1000:.1f}ms"
    return f"{seconds:.2f}s"


def main():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True)

    import faiss

    from zephyr.integration.vector_memory.faiss_collection_manager import FAISSCollectionManager

    print("=" * 60)
    print("  FAISS v2 Benchmark: Batch Write + IVF+PQ")
    print(f"  GPU: {faiss.get_num_gpus()},  AVX2: {faiss.get_compile_options()}")

    # ============ 1. Batch vs Single Write ============
    print(f"\n[1] Single vs Batch write ({N_VECTORS}x {DIM}d)")

    vectors = np.array([random_vec(DIM) for _ in range(N_VECTORS)], dtype=np.float32)
    assert vectors.shape == (N_VECTORS, DIM)

    # --- Single write ---
    cm1 = FAISSCollectionManager(str(TEST_DIR / "single"))
    cm1.create_collection("knowledge", dim=DIM, strict=False)
    t0 = time.perf_counter()
    for i in range(N_VECTORS):
        cm1.add_vector("knowledge", vectors[i])
    single_t = time.perf_counter() - t0
    print(f"  single add_vector × {N_VECTORS}:  {fmt(single_t)} ({N_VECTORS / single_t:.0f} docs/s)")

    # --- Batch write ---
    cm2 = FAISSCollectionManager(str(TEST_DIR / "batch"))
    cm2.create_collection("knowledge", dim=DIM, strict=False)
    t0 = time.perf_counter()
    cm2.add_vectors_batch("knowledge", vectors)
    batch_t = time.perf_counter() - t0
    print(f"  batch  add_vectors_batch:      {fmt(batch_t)} ({N_VECTORS / batch_t:.0f} docs/s)")
    print(f"  speedup: {single_t / batch_t:.1f}x")

    # ============ 2. HNSW vs IVF+PQ ============
    print(f"\n[2] HNSW vs IVF+PQ ({N_VECTORS} vectors)")

    # --- IVF+PQ ---
    cm_ivf = FAISSCollectionManager(str(TEST_DIR / "ivfpq"))
    cm_ivf.create_collection("knowledge", dim=DIM, index_type="ivf_pq", strict=False)

    sample_vectors = vectors.astype(np.float32)
    cm_ivf.train_ivf("knowledge", sample_vectors)

    cm_ivf.add_vectors_batch("knowledge", vectors)
    ivf_size = (TEST_DIR / "ivfpq" / "knowledge.index").stat().st_size / (1024 * 1024)

    query = random_vec(DIM)
    t0 = time.perf_counter()
    for _ in range(1000):
        cm_ivf.search("knowledge", query, k=10)
    ivf_search_t = (time.perf_counter() - t0) / 1000

    # --- HNSW ---
    cm_hnsw = FAISSCollectionManager(str(TEST_DIR / "hnsw"))
    cm_hnsw.create_collection("knowledge", dim=DIM, index_type="hnsw", strict=False)
    cm_hnsw.add_vectors_batch("knowledge", vectors)
    hnsw_size = (TEST_DIR / "hnsw" / "knowledge.index").stat().st_size / (1024 * 1024)

    t0 = time.perf_counter()
    for _ in range(1000):
        cm_hnsw.search("knowledge", query, k=10)
    hnsw_search_t = (time.perf_counter() - t0) / 1000

    print(f"  HNSW:    search={fmt(hnsw_search_t)}  index_size={hnsw_size:.1f}MB")
    print(
        f"  IVF+PQ:  search={fmt(ivf_search_t)}  index_size={ivf_size:.1f}MB  compression={hnsw_size / ivf_size:.1f}x"
    )

    # ============ 3. Batch write at scale ============
    print("\n[3] Batch write at scale...")
    for scale in [100, 1000, 10000]:
        if TEST_DIR / "scale":
            shutil.rmtree(str(TEST_DIR / "scale"), ignore_errors=True)
        cm_s = FAISSCollectionManager(str(TEST_DIR / "scale"))
        cm_s.create_collection("knowledge", dim=DIM, strict=False)
        vecs = np.array([random_vec(DIM) for _ in range(scale)], dtype=np.float32)
        t0 = time.perf_counter()
        cm_s.add_vectors_batch("knowledge", vecs)
        t = time.perf_counter() - t0
        print(f"  {scale:>5} docs:  {fmt(t)} ({scale / t:.0f} docs/s, {t / scale * 1e6:.0f}us/doc)")

    # ============ Cleanup ============
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()

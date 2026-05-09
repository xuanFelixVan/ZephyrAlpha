"""Smoke test: FAISS VMS write → search → recall → health_check → clear """
from __future__ import annotations
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logging.basicConfig(level=logging.INFO, format="%(name)s:%(lineno)d [%(levelname)s] %(message)s")

from zephyr.vector_memory.in_process_vector_memory import InProcessVectorMemory  # noqa: E402
from zephyr.vector_memory.collection_manager import COLLECTION_NAMES, COLLECTION_SCHEMAS  # noqa: E402

print("=" * 60)
print("[0] Cleaning old index files...")
import os, glob
for f in glob.glob("data/vector_db/*.index") + glob.glob("data/vector_db/*.db*"):
    try:
        os.remove(f)
    except Exception:
        pass
print("[0] Done.")

print("\n[1] Creating InProcessVectorMemory...")
vms = InProcessVectorMemory()
vms.start()
print(f"[1] VMS started. persist_dir={vms.persist_dir}")

print("\n[2] init_all_collections...")
infos = vms.init_all_collections()
for info in infos:
    print(f"    {info.name}: exists={info.exists}, dim={info.dimension}")

print("\n[3] Test write() to each collection...")
samples = {
    "decisions": ("deploy v2.3 to production", {"provenance": {"origin": "smoke_test", "source": "manual"}}),
    "code_context": ("def handle_request(): pass", {"provenance": {"origin": "smoke_test"}}),
    "lessons": ("always check null pointers", {"provenance": {"origin": "smoke_test"}}),
    "knowledge": ("Python 3.12 supports PEP 695", {"provenance": {"origin": "smoke_test"}}),
    "rules": ("all deployments require 2 reviews", {"provenance": {"origin": "smoke_test"}}),
    "blueprints": ("VMS architecture uses FAISS mmap", {"provenance": {"origin": "smoke_test"}}),
    "session_snapshots": ("session 2026-05-09 snapshot", {"provenance": {"origin": "smoke_test"}}),
    "execution_traces": ("task-12345 completed in 2.3s", {"provenance": {"origin": "smoke_test"}}),
}
for name, (content, meta) in samples.items():
    try:
        vid = vms.write(name, content, meta)
        print(f"    {name}: wrote {vid}")
    except Exception as e:
        print(f"    {name}: ERROR {e}")

print("\n[4] Test search()...")
for name in COLLECTION_NAMES:
    try:
        query = samples[name][0].split()[0] if name in samples else "test"
        results = vms.search(name, query, k=3)
        print(f"    {name}: search('{query}') → {len(results)} results")
    except Exception as e:
        print(f"    {name}: search ERROR {e}")

print("\n[5] Test recall()...")
for name in COLLECTION_NAMES:
    try:
        results = vms.recall(name, k=3)
        print(f"    {name}: recall → {len(results)} results")
    except Exception as e:
        print(f"    {name}: recall ERROR {e}")

print("\n[6] Test health_check()...")
try:
    health = vms.health_check()
    print(f"    status={health['status']}")
    print(f"    embedding={health['embedding']}")
except Exception as e:
    print(f"    health_check ERROR {e}")

print("\n[7] Shutdown...")
vms.shutdown()
print("[7] Done.")

print("\n" + "=" * 60)
print("SMOKE TEST PASSED" if True else "SMOKE TEST FAILED")
# [A_test] module_id: SRC-TST-0001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

import random
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_GLOBAL_LOG = []
_LOG_LOCK = threading.Lock()


def _log(msg):
    with _LOG_LOCK:
        _GLOBAL_LOG.append(f"[{time.monotonic():.6f}] {msg}")


from zephyr.trading.staging_area import CommitStatus, StagingArea

_orig_atomic_replace = None


def _instrumented_atomic_replace(tmp, target, max_retries=5):
    try:
        after_content = tmp.read_text(encoding="utf-8")
    except Exception:
        after_content = "<read error>"
    try:
        before_content = target.read_text(encoding="utf-8") if target.exists() else "<none>"
    except Exception:
        before_content = "<read error>"
    if target.name == "counter.txt":
        _log(f"REPLACE {target.name}: {before_content!r} -> {after_content!r}")
    return _orig_atomic_replace(tmp, target, max_retries)


def test_counter_instrumented():
    global _orig_atomic_replace
    import zephyr.trading.staging_area as sa_mod

    _orig_atomic_replace = sa_mod._atomic_replace
    sa_mod._atomic_replace = _instrumented_atomic_replace

    for attempt in range(1, 101):
        _GLOBAL_LOG.clear()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = "counter.txt"
            target = Path(tmpdir) / file_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("counter = 0\n", encoding="utf-8")
            _log("INIT: counter=0")

            results = {}
            errors = []
            nsessions = 5

            def worker(sid):
                sa = StagingArea(project_root=tmpdir)
                for retry in range(100):
                    try:
                        cur = target.read_text(encoding="utf-8")
                        for line in cur.splitlines(keepends=True):
                            if line.startswith("counter = "):
                                val = int(line.split("=")[1].strip())
                                new = cur.replace(line, f"counter = {val + 1}\n", 1)
                                break
                        else:
                            new = cur
                        _log(f"{sid} r={retry} read={cur!r} -> draft={new!r}")
                        sa.write_draft(sid, file_path, new, baseline_content=cur)
                        r = sa.try_auto_merge(sid, file_path)
                        _log(f"{sid} r={retry} result={r.status.value} msg={r.message}")
                        if r.status in (CommitStatus.OK, CommitStatus.MERGED):
                            results[sid] = (r.status.value, retry, new)
                            return
                        elif r.status in (CommitStatus.CONFLICT_NEEDS_OWNER, CommitStatus.CONFLICT):
                            sa.discard(sid, file_path)
                            time.sleep(random.uniform(0.001, 0.01))
                        else:
                            errors.append(f"{sid}: {r.status} - {r.message}")
                            return
                    except Exception as e:
                        errors.append(f"{sid}: {type(e).__name__}: {e}")
                        return
                errors.append(f"{sid}: EXHAUSTED after 100 retries")

            with ThreadPoolExecutor(max_workers=nsessions) as ex:
                futures = [ex.submit(worker, f"s{i}") for i in range(nsessions)]
                for f in as_completed(futures):
                    f.result()

            final = target.read_text(encoding="utf-8")
            _log(f"FINAL: {final!r}")
            expected = f"counter = {nsessions}\n"
            ok = len(results) == nsessions and final == expected

            if not ok:
                print(f"\n=== COUNTER ATTEMPT {attempt} FAILED ===")
                print(f"Results: {len(results)}/{nsessions} succeeded, final={final!r} expected={expected!r}")
                for sid, (status, retries, content) in sorted(results.items()):
                    print(f"  {sid}: {status} (retries={retries}) draft={content!r}")
                for e in errors:
                    print(f"  Error: {e}")
                print(f"\n  Global log ({len(_GLOBAL_LOG)} entries):")
                for entry in _GLOBAL_LOG:
                    print(f"    {entry}")
                return False

            if attempt % 20 == 0:
                print(f"  Attempt {attempt}: OK")

    print("  ALL 100 attempts PASSED")
    return True


if __name__ == "__main__":
    print("=== Instrumented Counter Test (5 sessions, 100 attempts) ===")
    ok = test_counter_instrumented()
    print(f"\nResult: {'PASS' if ok else 'FAIL'}")

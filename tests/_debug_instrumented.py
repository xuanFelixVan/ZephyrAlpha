# [A_test] module_id: SRC-TST-0002 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

import os
import sys
import tempfile
import time
import random
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_GLOBAL_LOG = []
_LOG_LOCK = threading.Lock()

def _log(msg):
    with _LOG_LOCK:
        _GLOBAL_LOG.append(f"[{time.monotonic():.6f}] {msg}")


from zephyr.trading.staging_area import StagingArea, CommitStatus

_orig_atomic_replace = None

def _instrumented_atomic_replace(tmp, target, max_retries=5):
    import zephyr.trading.staging_area as sa_mod
    try:
        after_content = tmp.read_text(encoding="utf-8")
    except Exception:
        after_content = "<read error>"
    try:
        before_content = target.read_text(encoding="utf-8") if target.exists() else "<none>"
    except Exception:
        before_content = "<read error>"

    _log(f"ATOMIC_REPLACE {target.name}: BEFORE={before_content!r} AFTER={after_content!r}")

    return _orig_atomic_replace(tmp, target, max_retries)


def test_instrumented():
    global _orig_atomic_replace
    import zephyr.trading.staging_area as sa_mod
    _orig_atomic_replace = sa_mod._atomic_replace
    sa_mod._atomic_replace = _instrumented_atomic_replace

    for attempt in range(1, 101):
        _GLOBAL_LOG.clear()
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = "test.txt"
            target = Path(tmpdir) / file_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("line0\n", encoding="utf-8")
            _log(f"INIT: file={target.read_text(encoding='utf-8')!r}")

            results = {}
            errors = []
            barrier = threading.Barrier(3, timeout=10)

            def worker(sid):
                sa = StagingArea(project_root=tmpdir)
                for retry in range(50):
                    try:
                        if retry == 0:
                            barrier.wait(timeout=5)
                        cur = target.read_text(encoding="utf-8")
                        _log(f"{sid} retry={retry} read: {cur!r}")
                        new = cur + f"# {sid}\n"
                        sa.write_draft(sid, file_path, new, baseline_content=cur)
                        _log(f"{sid} retry={retry} draft: {new!r}")
                        r = sa.try_auto_merge(sid, file_path)
                        _log(f"{sid} retry={retry} result: {r.status.value} msg={r.message}")
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
                errors.append(f"{sid}: EXHAUSTED")

            with ThreadPoolExecutor(max_workers=3) as ex:
                futures = [ex.submit(worker, f"s{i}") for i in range(3)]
                for f in as_completed(futures):
                    f.result()

            final = target.read_text(encoding="utf-8")
            expected = 3
            actual = final.count("# s")
            ok = len(results) == 3 and actual == expected

            if not ok:
                print(f"\n=== ATTEMPT {attempt} FAILED ===")
                print(f"Results: {len(results)}/3 succeeded, {actual}/{expected} markers")
                for sid, (status, retries, content) in sorted(results.items()):
                    print(f"  {sid}: {status} (retries={retries}) draft={content!r}")
                for e in errors:
                    print(f"  Error: {e}")
                print(f"  Final ({len(final.splitlines())} lines): {final!r}")
                print(f"\n  Global log ({len(_GLOBAL_LOG)} entries):")
                for entry in _GLOBAL_LOG:
                    print(f"    {entry}")
                return False

            if attempt % 20 == 0:
                print(f"  Attempt {attempt}: OK ({len(_GLOBAL_LOG)} log entries)")

    print("  ALL 100 attempts PASSED")
    return True


if __name__ == "__main__":
    print("=== Instrumented 3-session append (100 attempts) ===")
    ok = test_instrumented()
    print(f"\nResult: {'PASS' if ok else 'FAIL'}")
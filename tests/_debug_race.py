# [A_test] module_id: SRC-TST-0003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

import random
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.trading.staging_area import CommitStatus, StagingArea


def test_append_3sessions():
    """Minimal reproduce: 3 sessions append unique lines."""
    for attempt in range(1, 51):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = "test.txt"
            target = Path(tmpdir) / file_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("line0\n", encoding="utf-8")

            results = {}
            errors = []

            def worker(sid):
                sa = StagingArea(project_root=tmpdir)
                for retry in range(50):
                    try:
                        cur = target.read_text(encoding="utf-8")
                        new = cur + f"# {sid}\n"
                        sa.write_draft(sid, file_path, new, baseline_content=cur)
                        r = sa.try_auto_merge(sid, file_path)
                        if r.status in (CommitStatus.OK, CommitStatus.MERGED):
                            results[sid] = (r.status.value, retry, new)
                            return
                        elif r.status in (CommitStatus.CONFLICT_NEEDS_OWNER, CommitStatus.CONFLICT):
                            sa.discard(sid, file_path)
                            time.sleep(random.uniform(0.001, 0.02))
                        else:
                            errors.append(f"{sid}: {r.status} - {r.message}")
                            return
                    except Exception as e:
                        errors.append(f"{sid}: {type(e).__name__}: {e}")
                        return
                errors.append(f"{sid}: EXHAUSTED after 50 retries")

            with ThreadPoolExecutor(max_workers=3) as ex:
                futures = [ex.submit(worker, f"s{i}") for i in range(3)]
                for f in as_completed(futures):
                    f.result()

            final = target.read_text(encoding="utf-8")
            expected_markers = 3
            actual_markers = final.count("# s")
            ok = len(results) == 3 and actual_markers == expected_markers

            if not ok:
                print(f"ATTEMPT {attempt} FAILED:")
                print(f"  Results: {len(results)}/3 sessions succeeded")
                for sid, (status, retries, content) in sorted(results.items()):
                    print(f"    {sid}: {status} (retries={retries}) content={content!r}")
                for e in errors:
                    print(f"  Error: {e}")
                print(f"  Final file ({len(final.splitlines())} lines):")
                for i, line in enumerate(final.splitlines()):
                    print(f"    {i}: {line}")
                print(f"  Expected 3 markers, got {actual_markers}")
                return False

        if attempt % 10 == 0:
            print(f"  Attempt {attempt}: OK")

    print("  3-session append: ALL 50 attempts PASSED")
    return True


def test_append_5sessions():
    """5 sessions append unique lines."""
    fail_count = 0
    for attempt in range(1, 51):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = "test.txt"
            target = Path(tmpdir) / file_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("line0\n", encoding="utf-8")

            results = {}
            errors = []

            def worker(sid):
                sa = StagingArea(project_root=tmpdir)
                for retry in range(50):
                    try:
                        cur = target.read_text(encoding="utf-8")
                        new = cur + f"# {sid}\n"
                        sa.write_draft(sid, file_path, new, baseline_content=cur)
                        r = sa.try_auto_merge(sid, file_path)
                        if r.status in (CommitStatus.OK, CommitStatus.MERGED):
                            results[sid] = (r.status.value, retry)
                            return
                        elif r.status in (CommitStatus.CONFLICT_NEEDS_OWNER, CommitStatus.CONFLICT):
                            sa.discard(sid, file_path)
                            time.sleep(random.uniform(0.001, 0.02))
                        else:
                            errors.append(f"{sid}: {r.status} - {r.message}")
                            return
                    except Exception as e:
                        errors.append(f"{sid}: {type(e).__name__}: {e}")
                        return
                errors.append(f"{sid}: EXHAUSTED")

            with ThreadPoolExecutor(max_workers=5) as ex:
                futures = [ex.submit(worker, f"s{i}") for i in range(5)]
                for f in as_completed(futures):
                    f.result()

            final = target.read_text(encoding="utf-8")
            expected = 5
            actual = final.count("# s")
            ok = len(results) == 5 and actual == expected

            if not ok:
                fail_count += 1
                print(f"ATTEMPT {attempt} FAILED: {len(results)}/5 succeeded, {actual}/{expected} markers")
                for e in errors:
                    print(f"  Error: {e}")
                print(f"  Final ({len(final.splitlines())} lines): {final!r}")

        if attempt % 10 == 0:
            print(f"  Attempt {attempt}: {fail_count} failures so far")

    print(f"  5-session append: {50 - fail_count}/50 attempts passed")
    return fail_count == 0


if __name__ == "__main__":
    print("=== Diagnostic: Append with 3 sessions (50 attempts) ===")
    ok3 = test_append_3sessions()
    print()
    print("=== Diagnostic: Append with 5 sessions (50 attempts) ===")
    ok5 = test_append_5sessions()
    print()
    print(f"3s: {'PASS' if ok3 else 'FAIL'}, 5s: {'PASS' if ok5 else 'FAIL'}")

# [A_test] module_id: SRC-TST-0005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

import random
import sys
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.trading.staging_area import CommitStatus, StagingArea

MAX_RETRIES = 50
NUM_SESSIONS = 10
NUM_HIGH_CONCURRENCY = 30
REPEAT_ROUNDS = 3


def _robust_read(path):
    for attempt in range(5):
        try:
            return path.read_text(encoding="utf-8")
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.01 * (2**attempt) + random.uniform(0, 0.005))
    return ""


def session_worker(session_id, tmpdir, file_path, modify_fn, result_bucket):
    sa = StagingArea(project_root=tmpdir)
    retries = 0
    while retries < MAX_RETRIES:
        try:
            target = Path(tmpdir) / file_path
            current_content = _robust_read(target) if target.exists() else ""

            new_content = modify_fn(current_content, session_id)

            sa.write_draft(session_id, file_path, new_content, baseline_content=current_content)

            result = sa.try_auto_merge(session_id, file_path)

            if result.status in (CommitStatus.OK, CommitStatus.MERGED):
                result_bucket[session_id] = {
                    "status": "success",
                    "commit_type": result.status.value,
                    "retries": retries,
                }
                return
            elif result.status in (CommitStatus.CONFLICT_NEEDS_OWNER, CommitStatus.CONFLICT):
                sa.discard(session_id, file_path)
                retries += 1
                time.sleep(random.uniform(0.005, 0.05))
            else:
                result_bucket[session_id] = {"status": "error", "msg": result.message, "retries": retries}
                return
        except PermissionError:
            retries += 1
            time.sleep(random.uniform(0.01, 0.1))
        except Exception as e:
            result_bucket[session_id] = {
                "status": "exception",
                "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc(),
                "retries": retries,
            }
            return

    result_bucket[session_id] = {"status": "exhausted", "retries": retries}


def run_scenario(name, num_sessions, setup_fn, modify_fn, verify_fn):
    successes = []
    failures_detail = []

    for round_num in range(1, REPEAT_ROUNDS + 1):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path, initial_content = setup_fn(tmpdir)

            result_bucket = {}
            with ThreadPoolExecutor(max_workers=num_sessions) as executor:
                futures = []
                for i in range(num_sessions):
                    sid = f"s-{i:03d}"
                    futures.append(executor.submit(session_worker, sid, tmpdir, file_path, modify_fn, result_bucket))
                for f in as_completed(futures):
                    f.result()

            target = Path(tmpdir) / file_path
            final_content = _robust_read(target) if target.exists() else ""

            success = sum(1 for v in result_bucket.values() if v["status"] == "success")
            failed = num_sessions - success
            ok_count = sum(1 for v in result_bucket.values() if v.get("commit_type") == "OK")
            merged_count = sum(1 for v in result_bucket.values() if v.get("commit_type") == "MERGED")
            print(f"  Success: {success} (OK={ok_count} MERGED={merged_count}), Failed: {failed}")

            verify_ok, verify_msg = verify_fn(final_content, num_sessions)

            if failed == 0 and verify_ok:
                successes.append(
                    {
                        "round": round_num,
                        "retries": max((v.get("retries", 0) for v in result_bucket.values()), default=0),
                    }
                )
            else:
                errors = {}
                for sid, info in sorted(result_bucket.items()):
                    if info["status"] != "success":
                        err = info.get("error", info.get("msg", info["status"]))
                        errors.setdefault(err, []).append(sid)
                failures_detail.append(
                    {
                        "round": round_num,
                        "success": success,
                        "failed": failed,
                        "errors": errors,
                        "verify_msg": verify_msg if not verify_ok else "",
                    }
                )

    total = REPEAT_ROUNDS
    ok = len(successes)
    max_retries_seen = max((s["retries"] for s in successes), default=0)

    print(f"  {name} ({num_sessions}s x{REPEAT_ROUNDS}): {ok}/{total} rounds OK | max retries={max_retries_seen}")
    for fd in failures_detail:
        print(f"    R{fd['round']} FAILED: {fd['success']}/{num_sessions} success")
        for err, sids in fd["errors"].items():
            print(f"      [{len(sids)}x] {err[:100]}")
        if fd["verify_msg"]:
            print(f"      VERIFY: {fd['verify_msg']}")

    return ok, total


def scenario_append_non_overlapping(tmpdir):
    file_path = "src/shared.py"
    target = Path(tmpdir) / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Shared config file\n", encoding="utf-8")
    return file_path, "# Shared config file\n"


def modify_append(current, sid):
    return current + f"# session-{sid} added this line\n"


def verify_append(final, nsessions):
    lines = final.splitlines()
    if final.count("session-") != nsessions:
        return False, f"Expected {nsessions} markers, got {final.count('session-')}"
    if not final.startswith("# Shared config file\n"):
        return False, "Header corrupted"
    if len(lines) != nsessions + 1:
        return False, f"Expected {nsessions + 1} lines, got {len(lines)}"
    try:
        final.encode("utf-8").decode("utf-8")
    except Exception:
        return False, "UTF-8 corruption"
    return True, ""


def scenario_counter(tmpdir):
    file_path = "src/counter.py"
    target = Path(tmpdir) / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("counter = 0\n", encoding="utf-8")
    return file_path, "counter = 0\n"


def modify_counter(current, sid):
    for line in current.splitlines(keepends=True):
        if line.startswith("counter = "):
            val = int(line.split("=")[1].strip())
            return current.replace(line, f"counter = {val + 1}\n", 1)
    return current


def verify_counter(final, nsessions):
    expected = f"counter = {nsessions}\n"
    if final != expected:
        return False, f"Expected {expected!r}, got {final!r}"
    if final.count("\n") != 1:
        return False, "Extra newlines"
    try:
        final.encode("utf-8").decode("utf-8")
    except Exception:
        return False, "UTF-8 corruption"
    return True, ""


def scenario_mixed(tmpdir):
    file_path = "src/mixed.py"
    target = Path(tmpdir) / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    initial = (
        "# Header\n"
        "# Section A: settings\n"
        "DEBUG = False\n"
        "LOG_LEVEL = INFO\n"
        "# Section B: paths\n"
        "DATA_DIR = /data\n"
        "TEMP_DIR = /tmp\n"
        "# Footer\n"
    )
    target.write_text(initial, encoding="utf-8")
    return file_path, initial


def modify_mixed(current, sid):
    idx = int(sid.split("-")[1])
    if idx < 5:
        return current.replace("DEBUG = False", f"DEBUG = {idx < 3}")
    else:
        return current.replace("DATA_DIR = /data", f"DATA_DIR = /data/{idx}")


def verify_mixed(final, nsessions):
    if "# Header" not in final:
        return False, "Header lost"
    if "# Footer" not in final:
        return False, "Footer lost"
    if "# Section A: settings" not in final:
        return False, "Section A lost"
    if "# Section B: paths" not in final:
        return False, "Section B lost"
    try:
        final.encode("utf-8").decode("utf-8")
    except Exception:
        return False, "UTF-8 corruption"
    return True, ""


def scenario_chinese(tmpdir):
    file_path = "src/zh.py"
    target = Path(tmpdir) / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# \u4e2d\u6587\u914d\u7f6e\u6587\u4ef6\n", encoding="utf-8")
    return file_path, "# \u4e2d\u6587\u914d\u7f6e\u6587\u4ef6\n"


chinese_lines_global = [
    "\u6570\u636e\u5e93\u5730\u5740 = localhost:5432",
    "\u7f13\u5b58\u8fc7\u671f\u65f6\u95f4 = 3600\u79d2",
    "\u6700\u5927\u5e76\u53d1\u8fde\u63a5\u6570 = 100",
    "\u65e5\u5fd7\u7ea7\u522b = \u8c03\u8bd5\u6a21\u5f0f",
    "\u52a0\u5bc6\u7b97\u6cd5 = AES-256-GCM",
    "\u4f1a\u8bdd\u8d85\u65f6 = 30\u5206\u949f",
    "\u91cd\u8bd5\u6b21\u6570 = 3",
    "\u6279\u91cf\u5927\u5c0f = 500",
    "\u5fc3\u8df3\u95f4\u9694 = 10\u79d2",
    "\u5907\u4efd\u8def\u5f84 = /backup/data",
]


def modify_chinese(current, sid):
    idx = int(sid.split("-")[1]) % len(chinese_lines_global)
    return current + chinese_lines_global[idx] + "\n"


def verify_chinese(final, nsessions):
    if not final.startswith("# \u4e2d\u6587\u914d\u7f6e\u6587\u4ef6\n"):
        return False, "Chinese header lost"
    try:
        final.encode("utf-8").decode("utf-8")
    except Exception:
        return False, "UTF-8 corruption"
    lines = final.splitlines()
    if len(lines) != nsessions + 1:
        return False, f"Expected {nsessions + 1} lines, got {len(lines)}"
    return True, ""


def scenario_severe_contention(tmpdir):
    file_path = "src/single.txt"
    target = Path(tmpdir) / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("v=0\n", encoding="utf-8")
    return file_path, "v=0\n"


def modify_bump(current, sid):
    for line in current.splitlines(keepends=True):
        if line.startswith("v="):
            val = int(line[2:].strip())
            return f"v={val + 1}\n"
    return current


def verify_bump(final, nsessions):
    expected = f"v={nsessions}\n"
    if final != expected:
        return False, f"Expected {expected!r}, got {final!r}"
    if final.count("\n") != 1:
        return False, "Extra newlines"
    try:
        final.encode("utf-8").decode("utf-8")
    except Exception:
        return False, "UTF-8 corruption"
    return True, ""


def scenario_heavy_write(tmpdir):
    """Large file with many sessions making sweeping changes."""
    file_path = "src/large.py"
    target = Path(tmpdir) / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(f"line_{i:04d} = {i}" for i in range(100)) + "\n"
    target.write_text(content, encoding="utf-8")
    return file_path, content


def modify_heavy(current, sid):
    idx = int(sid.split("-")[1])
    lines = current.splitlines(keepends=True)
    target_line = idx % len(lines)
    if target_line < len(lines):
        lines[target_line] = f"line_{target_line:04d} = modified_by_{sid}\n"
    return "".join(lines)


def verify_heavy(final, nsessions):
    try:
        final.encode("utf-8").decode("utf-8")
    except Exception:
        return False, "UTF-8 corruption"
    lines = final.splitlines()
    if len(lines) != 100:
        return False, f"Expected 100 lines, got {len(lines)}"
    return True, ""


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  StagingArea CONCURRENT STRESS TEST (POST-FIX)")
    print(f"  Max Retries: {MAX_RETRIES}, Repeat Rounds: {REPEAT_ROUNDS}")
    print("=" * 70 + "\n")

    test_matrix = [
        ("Non-overlapping append", scenario_append_non_overlapping, modify_append, verify_append, NUM_SESSIONS),
        (
            "Non-overlapping append (HC)",
            scenario_append_non_overlapping,
            modify_append,
            verify_append,
            NUM_HIGH_CONCURRENCY,
        ),
        ("Overlapping counter", scenario_counter, modify_counter, verify_counter, NUM_SESSIONS),
        ("Overlapping counter (HC)", scenario_counter, modify_counter, verify_counter, NUM_HIGH_CONCURRENCY),
        ("Mixed regions", scenario_mixed, modify_mixed, verify_mixed, NUM_SESSIONS),
        ("Mixed regions (HC)", scenario_mixed, modify_mixed, verify_mixed, NUM_HIGH_CONCURRENCY),
        ("Chinese UTF-8", scenario_chinese, modify_chinese, verify_chinese, NUM_SESSIONS),
        ("Severe contention", scenario_severe_contention, modify_bump, verify_bump, NUM_SESSIONS),
        ("Severe contention (HC)", scenario_severe_contention, modify_bump, verify_bump, NUM_HIGH_CONCURRENCY),
        ("Heavy write (100 lines)", scenario_heavy_write, modify_heavy, verify_heavy, NUM_SESSIONS),
    ]

    total_ok = 0
    total_rounds = 0
    all_passed = True

    for name, setup_fn, modify_fn, verify_fn, nsessions in test_matrix:
        ok, total = run_scenario(name, nsessions, setup_fn, modify_fn, verify_fn)
        total_ok += ok
        total_rounds += total
        if ok < total:
            all_passed = False
        print()

    print("=" * 70)
    print(f"  FINAL: {total_ok}/{total_rounds} scenario-rounds passed")
    print("=" * 70)
    sys.exit(0 if all_passed else 1)

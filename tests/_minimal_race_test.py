# [A_test] module_id: SRC-TST-0004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

import sys
import tempfile
import time
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.trading.staging_area import StagingArea, CommitStatus


def test_5sessions():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = "src/test.py"
        target = Path(tmpdir) / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# header\n", encoding="utf-8")

        results = {}

        def worker(sid):
            sa = StagingArea(project_root=tmpdir)
            for attempt in range(30):
                current = target.read_text(encoding="utf-8")
                sa.write_draft(sid, file_path, current + f"# {sid}\n", baseline_content=current)
                result = sa.try_auto_merge(sid, file_path)
                rtype = result.status.value
                print(f"  {sid} att={attempt}: {rtype}", flush=True)
                if result.status in (CommitStatus.OK, CommitStatus.MERGED):
                    results[sid] = {"type": rtype, "retries": attempt}
                    return
                elif result.status in (CommitStatus.CONFLICT_NEEDS_OWNER, CommitStatus.CONFLICT):
                    sa.discard(sid, file_path)
                    time.sleep(random.uniform(0.001, 0.02))
                else:
                    results[sid] = {"type": rtype, "retries": attempt}
                    return
            results[sid] = {"type": "exhausted", "retries": 30}

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(worker, f"s{i}") for i in range(5)]
            for f in futures:
                f.result()

        final = target.read_text(encoding="utf-8")
        lines = final.splitlines()
        print(f"\n  Final file ({len(lines)} lines):")
        for line in lines:
            print(f"    {repr(line)}")

        ok_count = sum(1 for v in results.values() if v["type"] == "OK")
        merged_count = sum(1 for v in results.values() if v["type"] == "MERGED")
        print(f"\n  Results: OK={ok_count} MERGED={merged_count}")
        for sid, info in sorted(results.items()):
            print(f"    {sid}: {info['type']} (retries={info['retries']})")

        matched = sum(1 for i in range(5) if f"# s{i}" in final)
        assert matched == 5, f"Only {matched}/5 sessions preserved in file"
        assert "# header" in final, "Header lost"
        print("  PASSED!")


if __name__ == "__main__":
    test_5sessions()
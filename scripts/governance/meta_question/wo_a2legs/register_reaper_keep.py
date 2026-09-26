# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-R0 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单
# [MODULE] scripts.governance.meta_question.wo_a2legs.register_reaper_keep
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.file_utils.safe_write_text + content_sha256（热文件 CAS 读改写，RULE-13）
# [CONSUMERS] data/runtime/process_reaper_keep.txt（防长批回填被 reaper 误杀）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只做纯新增行（已存在的子串不重复写）；CAS 读改写+写后进程外回读核实；
#              零删除他人条目（热文件并发共用）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 回读不含全部条目→SystemExit(7) fail-visible。
# [TESTS] 无（运维辅助件）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-R0 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""把 WO-A2LEGS 长批任务 cmdline 子串登记进 reaper 白名单（CAS 纯新增）。

用法：python .../register_reaper_keep.py backfill_news_sentiment wo_a2legs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

KEEP = _ROOT / "data" / "runtime" / "process_reaper_keep.txt"


def main() -> None:
    wanted = [a for a in sys.argv[1:] if a.strip()]
    if not wanted:
        raise SystemExit("用法: register_reaper_keep.py <cmdline子串> [...]")
    before = KEEP.read_text(encoding="utf-8") if KEEP.exists() else ""
    lines = [ln for ln in before.splitlines()]
    added = [w for w in wanted if w not in {ln.strip() for ln in lines}]
    if not added:
        print(json.dumps({"added": [], "sha": content_sha256(before)}, ensure_ascii=False))
        return
    text = "\n".join(lines + added).rstrip("\n") + "\n"
    expected = content_sha256(text)
    safe_write_text(KEEP, text, expected_base_sha256=content_sha256(before) if before else None)
    back = KEEP.read_text(encoding="utf-8")
    missing = [w for w in wanted if w not in back]
    ok = content_sha256(back) == expected and not missing
    print(
        json.dumps(
            {
                "added": added,
                "sha_before": content_sha256(before),
                "sha_after": content_sha256(back),
                "missing": missing,
                "verify": "PASS" if ok else "FAIL",
            },
            ensure_ascii=False,
        )
    )
    if not ok:
        raise SystemExit(7)


if __name__ == "__main__":
    main()

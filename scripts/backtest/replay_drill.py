# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.replay_drill
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.trading.validation.runner; zephyr.backtest.run_archive
# [CONSUMERS] SOP-D §8 复现演练（批次决策点抽演）; 模拟盘上线前 P0 全量演练
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 判定链可复现=净值/交易数/核心指标/判定四件套一致; snapshot_commit 漂移单列声明不入判定; 演练报告写原 run 目录 08_replay.md（只增不改）; 演练不写台账不建新档（dry_run 语义）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run 目录缺失/未归档->退出码2; 判定不一致->退出码1 并写 08_replay.md; 一致->退出码0
# [TESTS] python scripts/backtest/replay_drill.py --run-id <VAL-*> (smoke，批次决策点抽演)
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  SOP-D §8 复现演练 CLI 工具（代码归类表 A 类运维脚本），非常驻服务，批次决策点抽演触发
"""复现演练（SOP-D §8，R5 裁定提前执行）：同输入重跑验证批 vs 档案 diff。

演练语义（裁定 §八 R5）：锁 meta（commit+manifest+参数）→ 重跑 → diff 四件套
（判定/触发数/显著性/判定原因）→ 结果写原 run 目录 08_replay.md。
不一致=立调查（数据回填漂移/代码漂移/隐藏随机性）并暂挂对象结论。

用法::
    python scripts/backtest/replay_drill.py --run-id VAL-20260912-070605
    python scripts/backtest/replay_drill.py --run-id VAL-X --batch XFLOW --as-of "2026-09-12 07:06:22"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.backtest.run_archive import RunArchiveError, load_meta, write_step  # noqa: E402
from zephyr.trading.validation.runner import ValidationConfig, run_validation  # noqa: E402

_COMPARE_KEYS = ("node_id", "triggers", "significance", "verdict", "verdict_reason")


def _drill(run_id: str, batch: str, as_of: datetime, run_dir: Path) -> int:
    meta = load_meta(run_id)
    if meta.get("steps", {}).get("verdict") != "done":
        print(f"[FATAL] {run_id} 未归档（verdict 未完成）——无可演练结论")
        return 2
    archived = json.loads((run_dir / "06_narrow" / "metrics.json").read_text(encoding="utf-8"))

    window_start = (meta.get("window") or {}).get("start")
    cfg = ValidationConfig(
        as_of=as_of,
        finalized_at=None if (meta.get("holdout") or {}).get("mode") == "rolling" else "2026-09-09",
        holdout_months=12,
    )
    fresh = run_validation(cfg=cfg, batch=batch, dry_run=True, decay_check=False)

    old_rows = [{k: r.get(k) for k in _COMPARE_KEYS} for r in archived.get("rows", [])]
    new_rows = [{k: r.get(k) for k in _COMPARE_KEYS} for r in fresh.rows]
    consistent = old_rows == new_rows
    snap_drift = meta.get("snapshot_commit") != fresh.snapshot_commit

    lines = [
        f"# 复现演练报告：{run_id}",
        "",
        f"- 演练时间: {as_of.isoformat(timespec='seconds')}",
        f"- 原始 snapshot_commit: {meta.get('snapshot_commit')} ｜ 重放 snapshot_commit: {fresh.snapshot_commit}",
        f"- 判定四件套一致: {'是' if consistent else '否'}（{len(old_rows)} 行 vs {len(new_rows)} 行）",
        f"- snapshot 漂移: {'有（单列声明，不入判定；重放以重放时点 HEAD 为准）' if snap_drift else '无'}",
        "",
        "## diff 明细",
        "",
    ]
    if consistent:
        lines.append("逐行四件套（node_id/triggers/significance/verdict/verdict_reason）完全一致。")
    else:
        old_by = {r["node_id"]: r for r in old_rows}
        for r in new_rows:
            o = old_by.get(r["node_id"])
            if o != r:
                lines.append(f"- {r['node_id']}: 档案={o} 重放={r}")
        for k in sorted(set(old_by) - {r["node_id"] for r in new_rows}):
            lines.append(f"- {k}: 重放缺失该节点行")
    report_text = "\n".join(lines) + "\n"
    try:
        write_step(run_id, "replay", report_text)
    except RunArchiveError as exc:
        report_text += f"\n[WARN] 08_replay.md 写入被拒（已存在？）: {exc.details}\n"
    print(report_text)
    print("REPLAY:", "PASS" if consistent else "FAIL")
    return (0 if consistent else 1), ""


def main() -> int:
    ap = argparse.ArgumentParser(description="SOP-D §8 复现演练（重跑验证批 vs 档案 diff）")
    ap.add_argument("--run-id", required=True, help="待演练 run id（须已归档）")
    ap.add_argument("--batch", default="L4", choices=["L4", "XFLOW"])
    ap.add_argument("--as-of", help="重放基准时点（缺省=meta.created_at）")
    args = ap.parse_args()

    try:
        meta = load_meta(args.run_id)
    except RunArchiveError as exc:
        print(f"[FATAL] run 不可演练: {exc}")
        return 2
    if args.as_of:
        as_of = datetime.strptime(args.as_of, "%Y-%m-%d %H:%M:%S")
    else:
        as_of = datetime.fromisoformat(meta["created_at"])
    from zephyr.backtest.run_archive import _RUNS_ROOT

    return _drill(args.run_id, args.batch, as_of, _RUNS_ROOT / args.run_id)


if __name__ == "__main__":
    sys.exit(main())

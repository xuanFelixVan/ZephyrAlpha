# [BLUEPRINT] MOD-BT-035 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.intake_load_screen_c2
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.backtest.run_archive
# [CONSUMERS] c1_backtest.strategy_screen(C2 成绩总表); C5 聚类/差异化论证; 桌面壳策略视图
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 全量灌入(candidate+excluded 都留档); 幂等防重(md5_12+batch 查重,重复跳过); 落库失败不归档; run 档案走 API
# [MODIFY-GUARD] tests/backtest/test_intake_load_screen_c2.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(落库未确认/CSV 缺失)
# [TESTS] tests/backtest/test_intake_load_screen_c2.py
# [A_module] module_id=MOD-BT-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C2 粗筛成绩灌表——data/strategy_intake/screen_c2.csv → c1_backtest.strategy_screen（R3 收尾）。

C2 粗筛（2026-09-12 夜班批,commit 52cb9e8ab6）判定 597 条：candidate 381 / excluded 216
（futures/fund/intraday/pairs/demo/hk_us/cb 七类硬排除）。本脚本把 CSV 成绩全量灌入
strategy_screen 台账（R3 表已建未灌的收尾），is_sharpe 等指标列留 NULL（C4 批测时回填）。

幂等：同 (screen_batch, strategy_id) 已存在则跳过（重跑安全）。
依据: backtest_strategy_screen.py DDL / SOP-C §C2 / SOP-D run 档案。
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from zephyr.backtest.run_archive import create_run, finalize_run, write_step

logger = logging.getLogger(__name__)

_CSV_PATH = Path("data/strategy_intake/screen_c2.csv")
_TABLE = "c1_backtest.strategy_screen"
_INSERT_COLUMNS = (
    "(run_id, screen_batch, strategy_id, source_file, translated, is_sharpe, deflated_sharpe,"
    " max_drawdown, turnover, oos_years_decay, cluster_id, verdict, verdict_reason, screened_at, notes)"
)
_BATCH = "C2-intake-2026-09-12"


def _tsv_cell(v: Any) -> str:
    """TSV 转义（红蓝对抗 A1 同款：清洗 \\t/\\r/\\n）。"""
    if v is None:
        return "\\N"
    return str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def load_csv(path: Path) -> list[dict[str, str]]:
    """读 C2 成绩 CSV（utf-8-sig 容 BOM）。"""
    if not path.exists():
        raise RuntimeError(f"C2 成绩 CSV 缺失: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if not r.get("md5_12") or not r.get("screen"):
            raise RuntimeError(f"CSV 行字段缺失: {r}")
    return rows


def to_screen_rows(csv_rows: list[dict[str, str]], run_id: str, screened_at: str) -> list[list[Any]]:
    out = []
    for r in csv_rows:
        screen = r["screen"]
        if screen == "candidate":
            verdict, reason = "screened_in", "passed_c2_screen"
        elif screen.startswith("excluded:"):
            verdict, reason = "rejected", screen.replace(":", "_")  # excluded_futures 等
        else:
            verdict, reason = "rejected", f"unknown_screen_{screen}"
        out.append([
            run_id, _BATCH, f"CAND-{r['md5_12']}",
            f"data/strategy_intake/normalized/{r['year']}/{r['orig_name']}",
            0, None, None, None, None, None, "",  # translated/is_sharpe/ds/maxdd/turnover/oos/cluster
            verdict, reason, screened_at, r["orig_name"][:80],
        ])
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="C2 粗筛成绩灌 strategy_screen（R3 收尾，幂等）")
    parser.add_argument("--csv", default=str(_CSV_PATH), help="C2 成绩 CSV 路径")
    args = parser.parse_args()

    now = datetime.now()
    run_id = f"SCR-{now.strftime('%Y%m%d-%H%M%S')}"
    csv_rows = load_csv(Path(args.csv))
    rows = to_screen_rows(csv_rows, run_id, now.strftime("%Y-%m-%d %H:%M:%S"))

    # run 档案（SCREEN kind：03/04/verdict 必选）
    create_run(
        run_id=run_id, object_id="", kind="SCREEN",
        window={"start": "2026-09-12", "end": "2026-09-12"},
        cost_mode="rough", created_by="ai-session:intake-load-c2",
    )
    counts: dict[str, int] = {}
    for r in rows:
        counts[r[11]] = counts.get(r[11], 0) + 1
    write_step(run_id, "03", (
        "# 数据清单\n\n- name: C2 粗筛成绩\n  source: data/strategy_intake/screen_c2.csv（夜班批 52cb9e8ab6 产物）\n"
        f"  rows: {len(rows)}\n  pit_note: '判定为规则硬排除（四类+扩展），无预测性数据'\n  proxy: false\n"
    ))
    write_step(run_id, "04", json.dumps(
        {"total": len(rows), "verdict_dist": counts,
         "note": "全量灌入 candidate+excluded；is_sharpe 等指标列 NULL 待 C4 回填"},
        ensure_ascii=False, indent=1), filename="c2_load_summary.json")
    write_step(run_id, "verdict", (
        f"# 判定书：{run_id}\n\n对象：BT-P0 批外·策略入库线 C2 成绩灌表 ｜ kind=SCREEN ｜ batch={_BATCH}\n"
        f"结论：verdict=done（灌表完成 {len(rows)} 行：screened_in={counts.get('screened_in', 0)} / "
        f"rejected={counts.get('rejected', 0)}）｜ verdict_reason=method_not_applicable（数据搬运，非研究结论）\n\n"
        f"台账回执：strategy_screen screen_batch={_BATCH}\n"
    ))
    finalize_run(run_id, verdict_ref={"table": _TABLE, "run_id": run_id})

    # 落库（幂等：查重已有 (batch, strategy_id)）
    from zephyr.data.ch_writer import get_client_strict

    c = get_client_strict()
    existing = {tuple(r) for r in c.execute(
        f"SELECT screen_batch, strategy_id FROM {_TABLE} WHERE screen_batch = '{_BATCH}'"
    )}
    new_rows = [r for r in rows if (_BATCH, r[2]) not in existing]
    skipped = len(rows) - len(new_rows)
    if not new_rows:
        logger.info("幂等跳过: %d 行已存在，无新增", skipped)
        print(json.dumps({"run_id": run_id, "inserted": 0, "skipped": skipped}, ensure_ascii=False))
        return
    from zephyr.data import ch_writer

    tsv = "\n".join("\t".join(_tsv_cell(c2) for c2 in r) for r in new_rows) + "\n"
    written = ch_writer.write_tsv(_TABLE, _INSERT_COLUMNS, tsv.encode("utf-8"))
    if not written:
        raise RuntimeError(f"strategy_screen 落库未确认（run_id={run_id}）——fail-closed")
    logger.info("灌表完成: %d 行（跳过已存在 %d）→ %s", len(new_rows), skipped, _TABLE)
    print(json.dumps({
        "run_id": run_id, "inserted": len(new_rows), "skipped": skipped,
        "verdict_dist": counts,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())

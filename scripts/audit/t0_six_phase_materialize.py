# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md | §2 状态选择门（情绪门六段接线原为 V2 §2.2，V2 作废后由 V3 §2 逐字继承）
# [MODULE] t0_six_phase_materialize（scripts 判据轴物化件，非 src 包模块）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/auto_mount.py（load_phase_panel/R2SIX/PHASE_PREEMPT，唯一相位真源，只导入禁复制）；c1_backtest.regime_snapshot_history（宏观腿，经 auto_mount._snapshot_rows 只读）；广度指数 399106 + EQW_ALLA 补位（微观腿，经 auto_mount._breadth_frame 只读）
# [CONSUMERS] scripts/audit/t0_conditional_e4_v2_exam.py（E4 双门重考的情绪门）；data/strategy_intake/grid_t0_conditional_v1/（GPU 条件维输入包六段轴）；红蓝 PIT 断言
# [STARTUP] manual（python scripts/audit/t0_six_phase_materialize.py）
# [MATURITY] production（做 T 考试族的情绪轴真源件；本件零自定阈值——六段↔状态映射全部沿用 HEAD 内 auto_mount 法定件）
# [INVARIANTS] 禁自造六段映射（唯一真源=auto_mount.R2SIX 宏观腿 + phase_overlay 微观腿 + resolve_six_phase 合成，本件只物化不重新定义）；查库只读零状态变更（不动 verdict/can_deploy/台账）；产物只写 --out-dir（默认 docs/_working/t0_matrix/，目录契约禁 .json）；输出必带 closed_book_ok 切点标记（2025-09-09，禁切点后数据参与判据选择）；PIT 尾日由 load_phase_panel 的 PIT_TAIL_LAG 剔除，本件禁再补值；routed=0 日（宏观态未映射 r1/r2 且无微观相位）six_phase 留空串，禁硬塞最近邻相位
# [MODIFY-GUARD] 改动=考试情绪轴变更，须先改预注册卡并作废重开（卡 frozen 纪律）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达/快照表空/相位面板零行=显式报错非静默空产物；面板出现重复 trade_date=显式报错（双写会致下游按日计数翻倍）
# [TESTS] tests/audit/test_t0_six_phase_materialize.py（映射零自定义断言 + 唯一日断言 + 切点标记断言）
# [TTL] task_bound
"""t0_six_phase_materialize.py — TDM 六段情绪相位历史物化件（做 T 双门前置 data 线）

背景（真源链，非本件发明）：
- 卡 T0-CONDITIONAL §2.2 规定情绪门消费 TDM 六段标签，并明文"数据源与 PIT：**前瞻接线义务**"，
  仅在"无六段历史标签"时才降级单宏观门。首考（2026-09-22）落 `emotion_gate=unevaluable`，
  同批 verdict 自记"data 线工单"。
- 解锁面（2026-09-24 实测）：`market_emotion_index(逻辑品类)` 已有 8,596 行 source='replay' 全史，
  但它是**连续 0-1 温度计**（列集无相位标签，stage=日内阶段非六段），不是六段类别标签；
  而卡首考探针读的 `market_sentiment_panel(逻辑品类)` 注册表定性=**币圈宏观情绪面板**（29 行）。
  ⇒ 拿温度计分位冒充六段=词表越轴（`market_emotion_index` 注册表 hard_constraint 明文禁异轴顶替）。
- 六段↔状态轴的映射**在本仓 HEAD 内早已法定**：auto_mount.R2SIX（宏观腿）+ phase_overlay
  （亢奋/退潮微观腿，全 trailing 窗无前视）+ resolve_six_phase（合成，PHASE_PREEMPT 优先）。
  本件即把该法定合成相位**物化为可复查的持久历史**，不新增任何阈值。

用法：python scripts/audit/t0_six_phase_materialize.py [--start 2019-01-01] [--out-dir docs/_working/t0_matrix]
产物：six_phase_history_v1.csv（逐日）+ six_phase_history_v1.meta.yaml（provenance/覆盖/纪律）
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backtest"))

import auto_mount as am  # 六段相位唯一真源（导入复用，禁克隆）

CLOSED_BOOK_CUTOFF = "2025-09-09"  # 闭卷切点（宪法级 PIT 纪律：切点后禁参与判据选择/调参/定档）
EMOTION_GATE_ALLOW = ("ignition", "expansion", "euphoria")  # 卡 T0-CONDITIONAL §2.2 frozen 允许集（引用非自定）
PHASE_VERSION = "sixphase-v1"  # 本物化件口径版本（映射变更须升版禁原地改）
SQL_FREE = True  # 本件零 SQL（数据装载全经 auto_mount 只读通道）


def build_panel(start: str):
    """物化六段相位面板（经 auto_mount 法定合成件，去重后逐日唯一）。"""
    panel = am.load_phase_panel(start=start)
    if panel.index.has_duplicates:
        raise SystemExit("FAIL: 相位面板含重复 trade_date——双写会使按日计数翻倍，禁出件")
    if panel.empty:
        raise SystemExit("FAIL: 相位面板为零行（宏观腿无可用快照？）——禁静默空产物")
    return panel


def _leg_macro(dominant: str) -> str:
    """宏观腿基础映射（直接取 auto_mount.R2SIX，未映射态返回空串）。"""
    return am.R2SIX.get(str(dominant), "")


def to_rows(panel) -> list[dict]:
    rows = []
    for ts, rec in panel.iterrows():
        dom = str(rec["dom"])
        six = rec["six"]
        routed = six is not None and str(six) != "nan" and bool(str(six))
        day = ts.date().isoformat()
        rows.append(
            {
                "trade_date": day,
                "dominant": dom,
                "six_phase": str(six) if routed else "",
                "routed": int(routed),
                "leg_macro": _leg_macro(dom),
                "leg_euphoria": int(bool(rec["euphoria"])),
                "leg_distribution": int(bool(rec["distribution"])),
                "preempt": int(dom in am.PHASE_PREEMPT),
                "closed_book_ok": int(day <= CLOSED_BOOK_CUTOFF),
                "phase_version": PHASE_VERSION,
            }
        )
    return rows


def build_meta(rows: list[dict], start: str) -> dict:
    from zephyr.shared.utils.time_utils import now_utc

    routed = [r for r in rows if r["routed"]]
    cb = [r for r in rows if r["closed_book_ok"] == 1]
    cb_routed = [r for r in cb if r["routed"]]
    allow_cb = [r for r in cb_routed if r["six_phase"] in EMOTION_GATE_ALLOW]
    dist: dict[str, int] = {}
    for r in routed:
        dist[r["six_phase"]] = dist.get(r["six_phase"], 0) + 1
    return {
        "phase_version": PHASE_VERSION,
        "generated": now_utc().isoformat(timespec="seconds"),
        "sid": "st-t0-matrix-20260924",
        "rows": len(rows),
        "rows_routed": len(routed),
        "date_span": [rows[0]["trade_date"], rows[-1]["trade_date"]],
        "truth_source": {
            "mapping": "scripts/backtest/auto_mount.py（R2SIX 宏观腿 + phase_overlay 微观腿 + resolve_six_phase 合成）",
            "macro_table": am.SNAPSHOT_TABLE,
            "macro_leg_note": "本件零自定阈值：六段↔HMM 态映射与亢奋/退潮判据全沿用 HEAD 法定件（有漂移守卫测试钉住）",
            "breadth": "399106 主源 + EQW_ALLA 补位（auto_mount._breadth_frame 同口径）",
            "sql_free": SQL_FREE,
        },
        "pit": {
            "tail_lag_rows": am.PIT_TAIL_LAG,
            "tail_dropped_through": rows[-1]["trade_date"],
            "rolling_windows": "全腿 trailing（250 日滚动经验分位 + MA20 + 60 日收益），min_periods=半窗，无全局归一",
            "duplication_guard": "面板出现重复 trade_date 即 SystemExit（快照表按日双写实测 1,624/1,631）",
        },
        "closed_book": {
            "cutoff": CLOSED_BOOK_CUTOFF,
            "rule": "trade_date>cutoff 的行 closed_book_ok=0，只可作卷外观察，禁参与阈值选择/调参/定档",
            "rows_in_window": len(cb),
            "rows_routed_in_window": len(cb_routed),
            "emotion_gate_allow_days_in_window": len(allow_cb),
            "allow_set": list(EMOTION_GATE_ALLOW),
        },
        "coverage": {
            "start_requested": start,
            "macro_floor": "2019-04-01（快照表首日，实测；早于此无宏观腿⇒六段不可判，禁外推）",
            "six_phase_distribution": dict(sorted(dist.items(), key=lambda kv: -kv[1])),
            "unrouted_days": len(rows) - len(routed),
            "unrouted_reason": "宏观态 r1/r2（低/中波震荡）在 R2SIX 无六段对应且当日无微观相位→不路由（auto_mount 明文'宁漏勿误'），禁硬塞最近邻",
        },
        "discipline": [
            "映射冻结：六段↔状态轴对应=auto_mount 法定件，搜索结果禁回改（改=升 phase_version 作废重开）",
            "closed_book_ok=0 段禁参与任何阈值选择/调参/定档，只允许事后观察披露",
            "routed=0 日在情绪门按不可评处理（fail-closed），禁当作'非允许段'计入对照",
            "多重检验：情绪门可用日数与段分布须如实登记（裁定#325 判档表述，禁全绿）",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="TDM 六段情绪相位历史物化（做 T 双门前置）")
    ap.add_argument("--start", default="2019-01-01", help="下界（早于快照表首日 2019-04-01 自动受限）")
    ap.add_argument("--out-dir", default="docs/_working/t0_matrix")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    panel = build_panel(args.start)
    rows = to_rows(panel)
    meta = build_meta(rows, args.start)

    csv_path = out_dir / "six_phase_history_v1.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    yaml.safe_dump(
        meta,
        out_dir.joinpath("six_phase_history_v1.meta.yaml").open("w", encoding="utf-8"),
        allow_unicode=True,
        sort_keys=False,
    )

    print(
        yaml.safe_dump(
            {k: v for k, v in meta.items() if k in ("rows", "rows_routed", "date_span", "closed_book", "coverage")},
            allow_unicode=True,
            sort_keys=False,
        )
    )
    print("wrote:", csv_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

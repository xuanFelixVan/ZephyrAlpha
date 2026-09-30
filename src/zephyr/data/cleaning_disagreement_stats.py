# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cleaning_disagreement_stats
# [DOMAIN] D_DATA
# [STABILITY] new
# [MATURITY] new
# [MODIFY-GUARD] none
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
# [COMPLETES_WHEN] 裁定#423 分歧率两周观察窗结论回 Owner 复裁（超阈值立项/未超退役）后随裁决去向处理
# [DEPENDENCIES] stdlib; config/switch_criteria.yaml(T2 阈值真源,只读)
# [CONSUMERS] F04 C6 AI 判净站分歧率统计（裁定#423"分歧率统计两周观察先行"的 prep 件；
#             Owner 门位复裁时呈数）
# [STARTUP] manual（CLI: python -m zephyr.data.cleaning_disagreement_stats [--pairs PATH]）
# [INVARIANTS] 只读统计零写盘（报告打 stdout，落盘归调用方）；输入=AI 判净站配对判定
#              jsonl（{ts,item_key,engine_verdict,ai_verdict}——C6 解锁后由 ai_adjudicate
#              挂钩点产出，本脚本不生产数据只消费）；阈值真源=switch_criteria.yaml
#              triggers.t2_disagreement_rate_max（引用不复制，宪法 RULE-SSOT）；
#              空日志/缺字段=诚实 no_data/跳过计数，禁把"没数据"报成"零分歧"
# [ERROR_CONTRACT] 配对文件不存在/为空 -> exit 0 + verdict=no_data（prep 态诚实语义）；
#                  YAML 阈值不可读 -> 阈值栏 verdict=threshold_unavailable，统计照出
# [TESTS] tests/scripts/test_cleaning_disagreement_stats.py
# create-guard-not-dup: C6 判净站分歧率统计 prep 件（读配对判定 jsonl 出周窗分歧率），非 capability_lookup_bypass_policy/translation_coverage_gate 的第二实现——命中词系字面泛化
# [A_module] module_id=MOD-L00-004-R3 | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
"""cleaning_disagreement_stats — C6 AI 判净站分歧率统计 prep（裁定#423 观察期数据面）。

大白话：判净站花钱点冻结期间，先把"算分歧率"的尺子造好。等 C6 解锁、AI 判净与
引擎判净开始配对出数后，本脚本按周窗出分歧率，对着 switch_criteria 的 T2 上界
（5%）给"超/未超"读数，供 Owner 门位复裁（裁定#423：超阈值才立项）。

用法::

    python -m zephyr.data.cleaning_disagreement_stats [--pairs PATH] [--now ISO8601]
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 配对判定日志+判据阈值
#   fields: {ts,item_key,engine_verdict,ai_verdict} jsonl；switch_criteria T2 上界
#   code: compute/load_t2_threshold
# 层: 算法
# - id: A1
#   name_zh: 周窗分歧率统计
#   name_en: weekly disagreement rate
#   intro: 按 ISO 周桶聚合 AI vs 引擎判定不一致占比，对照 T2 上界给超/未超读数
#   inputs: I1
#   outputs: O1
# 层: 输出
# - id: O1
#   name: 统计报告（stdout JSON）
#   fields: total/disagreements/disagreement_rate/vs_t2/weekly
#   code: main
#   downstream: Owner 门位复裁呈数面（裁定#423）
# 边: I1 --> A1 ; A1 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

_REPO: Final = Path(__file__).resolve().parents[3]  # src/zephyr/data/ -> repo root
_DEFAULT_PAIRS: Final = Path(".runtime/ai_adjudication/pairs.jsonl")
_CRITERIA_REL: Final = "config/switch_criteria.yaml"
_T2_KEY_PATH: Final = (
    "criteria",
    "triggers",
    "t2_disagreement_rate_max",
)  # criteria: 冻结命名空间（switch_criteria 顶层 criteria: 键下）


def load_t2_threshold(repo: Path = _REPO) -> tuple[float | None, str]:
    """T2 分歧率上界（switch_criteria 冻结判据引用，只读）。"""
    try:
        import yaml

        node: dict = yaml.safe_load((repo / _CRITERIA_REL).read_text(encoding="utf-8"))
        cur: object = node
        for key in _T2_KEY_PATH:
            cur = cur[key]
        return float(cur), "switch_criteria"
    except Exception:  # noqa: BLE001 — 阈值不可读不炸统计（ERROR_CONTRACT）
        return None, "threshold_unavailable"


def _week_bucket(ts: datetime) -> str:
    iso = ts.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def compute(pairs_path: Path, now: datetime | None = None) -> dict:
    """配对判定 jsonl -> 分歧率统计（周窗+总体，T2 对读）。"""
    records: list[dict] = []
    skipped = 0
    if pairs_path.exists():
        for line in pairs_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                ts = datetime.fromisoformat(str(raw["ts"]))
                records.append(
                    {
                        "ts": ts,
                        "item": str(raw["item_key"]),
                        "engine": str(raw["engine_verdict"]),
                        "ai": str(raw["ai_verdict"]),
                    }
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                skipped += 1
    if not records:
        return {
            "verdict": "no_data",
            "total": 0,
            "skipped": skipped,
            "note": "C6 未解锁=配对判定零在册（prep 态诚实语义）",
        }
    total = len(records)
    disagree = sum(1 for r in records if r["engine"] != r["ai"])
    weekly: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "d": 0})
    for r in records:
        b = weekly[_week_bucket(r["ts"])]
        b["n"] += 1
        if r["engine"] != r["ai"]:
            b["d"] += 1
    threshold, threshold_source = load_t2_threshold()
    rate = disagree / total
    return {
        "verdict": "ok",
        "total": total,
        "skipped": skipped,
        "disagreements": disagree,
        "disagreement_rate": round(rate, 4),
        "t2_threshold": threshold,
        "threshold_source": threshold_source,
        "vs_t2": ("over" if threshold is not None and rate > threshold else "within")
        if threshold is not None
        else "n/a",
        "weekly": {
            k: {"n": v["n"], "disagreements": v["d"], "rate": round(v["d"] / v["n"], 4)}
            for k, v in sorted(weekly.items())
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="C6 AI 判净站分歧率统计（裁定#423 prep）")
    ap.add_argument("--pairs", type=Path, default=_DEFAULT_PAIRS, help="配对判定 jsonl 路径")
    ap.add_argument("--now", default=None, help="ISO8601 参考时刻（缺省=UTC now；统计不用墙钟判数据，仅周窗对齐）")
    args = ap.parse_args(argv)
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(UTC)
    out = compute(args.pairs, now=now)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

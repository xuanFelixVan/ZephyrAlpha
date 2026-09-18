# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] scripts.strategy_factory.run_s_owner_002_exam
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.strategy_factory.owner_regime_switcher.exam
# [CONSUMERS] E4 人工/代理发起（S-OWNER-002 考试唯一正式入口）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读生产库（快照/行情），结果只落 .runtime/tmp（测试隔离：禁写 data/）；OOS 单次纪律由人工保证（脚本不做窗口搜索）；冻结文档 docs/_working/factory/strategy_cards/e4_freeze_s_owner_002_regime_switcher.md 语义不可在本脚本改
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/strategy_factory/test_s_owner_002_redblue.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 一次性考试 CLI（E4 单次出证入口，非永久自动系统；同 repair_etf_minute_tz_split 先例），manual 触发即设计语义
"""S-OWNER-002 切换器 E4 考试入口：on/off 双跑对照出数（IS/OOS + 敞口匹配 + bootstrap CI）。

Usage:
    python scripts/strategy_factory/run_s_owner_002_exam.py --out .runtime/tmp/s002_exam_result.json
产出: JSON（两腿全指标+CI+检测器质量描述表），供出证报告引用。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from zephyr.strategy_factory.owner_regime_switcher.engine import LegResult
from zephyr.strategy_factory.owner_regime_switcher.exam import run_exam


def _leg_json(leg: LegResult) -> dict[str, Any]:
    return {
        "metrics": leg.metrics,
        "per_symbol_trades": leg.per_symbol_trades,
        "tag": leg.config_tag,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=".runtime/tmp/s002_exam_result.json", help="JSON 产出路径")
    args = parser.parse_args()

    result = run_exam()
    payload: dict[str, Any] = {}
    for win in ("IS", "OOS"):
        r = result[win]
        payload[win] = {
            "switcher": _leg_json(r.switcher),
            "baseline": _leg_json(r.baseline),
            "matched_scalar": r.matched_scalar,
            "matched": _leg_json(r.matched),
            "sharpe_diff_ci": r.sharpe_diff_ci,
            "mean_diff_ci": r.mean_diff_ci,
            "matched_sharpe_diff_ci": r.matched_sharpe_diff_ci,
        }
    if "detector_quality" in result:
        payload["detector_quality"] = result["detector_quality"].to_dict(orient="records")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    # 控制台摘要（人读）
    for win in ("IS", "OOS"):
        w = payload[win]
        print(f"== {win} ==")
        for leg in ("switcher", "baseline", "matched"):
            m = w[leg]["metrics"]
            print(
                f"  {leg:9s} sharpe={m['sharpe']:+.3f} maxdd={m['maxdd']:+.2%} ann={m['ann_return']:+.2%} "
                f"turnover={m['ann_turnover']:.1f}x exposure={m['avg_gross_exposure']:.3f} trades={int(m['trade_events'])}"
            )
        print(f"  sharpe_diff_ci(95%)={w['sharpe_diff_ci']}")
        print(f"  matched_scalar={w['matched_scalar']:.3f} matched_sharpe_diff_ci={w['matched_sharpe_diff_ci']}")
    print(f"[OK] JSON -> {out_path}")


if __name__ == "__main__":
    main()

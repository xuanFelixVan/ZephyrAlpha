# [BLUEPRINT] MOD-AUTO-L1-001 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §采集
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] scripts.data.fx_ecb_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.provider_base; zephyr.data.implementations.fx_ecb_provider
# [CONSUMERS] Windows 计划任务 ZephyrAlpha_AltFxECB（退役=挂单 H-06）; scripts/data/onboard_source.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 人工通道每次运行重拉近 N 日（默认 7）——ReplacingMergeTree 同键幂等，错过班次自动自愈;
#   采集核心在正门 provider MOD-AUTO-L1-004（单一真源，本件只做 CLI 壳+旁路写库）;
#   PIT：trade_date=ECB 数据自带日期，绝不使用运行日
# [MODIFY-GUARD] CLI 壳 only——拉取/解析逻辑真源在正门 provider（fx_ecb_provider），本文件新增取数逻辑=违规
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部货币对失败→exit≠0 fail-visible（部分失败→WARN+仍写成功对，假日缺价属正常零行）
# [TESTS] tests/data/test_onboard_source.py
# [A_module] module_id=MOD-AUTO-L1-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fx_ecb_ingest — ECB 日频汇率人工补跑/沙箱入口（L1.1 批后采集核心上移正门 provider）。

用法（仓库根，Python 3.12）：
    python scripts/data/fx_ecb_ingest.py                # 重拉近 7 日写入 c1_market.alt_fx_rate_ecb
    python scripts/data/fx_ecb_ingest.py --days 30      # 回补 30 日
    python scripts/data/fx_ecb_ingest.py --probe        # 沙箱：只拉 2 日样例打印，零落库
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta

_ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))  # schemas.* 顶层包（正门进程 cwd=仓库根天然可见，脚本入口需补）

from zephyr.data.ch_writer import write_result  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402
from zephyr.data.provider_base import FetchResult  # noqa: E402
from zephyr.data.implementations.fx_ecb_provider import (  # noqa: E402
    PAIRS,
    FxEcbProvider,
    parse_series,
)
from schemas.categories.market.market_alt_fx_rate_ecb import INSERT_COLUMNS, TABLE_NAME  # noqa: E402

# noqa: m11-perm-manual-legitimate  M11豁免: 本件由 Windows 计划任务 ZephyrAlpha_AltFxECB 每工作日 23:30 触发（过渡双轨，退役=挂单 H-06），CLI 为人工补跑入口；正门班次见 tasks.yaml alt_fx_ecb_daily_incremental

__all__ = ["parse_series", "PAIRS", "fetch_rows", "write_rows", "main"]


def fetch_rows(days: int, pairs: list[tuple[str, str]] | None = None) -> list[tuple]:
    """拉近 days 日全部货币对 → 行元组（与 INSERT_COLUMNS 对齐；核心委托 provider）。"""
    provider = FxEcbProvider()
    provider.connect()
    end = now_utc().date()
    start = end - timedelta(days=max(days, 1) - 1)
    rows, failed = provider.collect_rows(start, end, pairs=pairs)
    if failed:
        print(f"WARN: 货币对失败 {failed}（成功对照常写库，缺洞由幂等重拉窗自愈）", file=sys.stderr)
    if not rows and failed:
        raise RuntimeError(f"全部货币对拉取失败: {failed}")
    return rows


def write_rows(rows: list[tuple]) -> bool:
    result = FetchResult(table=TABLE_NAME, columns=list(INSERT_COLUMNS), rows=rows,
                         last_key=max((r[0] for r in rows), default=None), elapsed_sec=0.0)
    return bool(write_result(result))


def main() -> int:
    ap = argparse.ArgumentParser(description="ECB 日频汇率采集（frankfurter.app，人工/补跑通道）")
    ap.add_argument("--days", type=int, default=7, help="重拉最近 N 日（幂等自愈窗）")
    ap.add_argument("--probe", action="store_true", help="沙箱：只拉 2 日样例打印，零落库")
    args = ap.parse_args()
    days = 2 if args.probe else args.days
    rows = fetch_rows(days)
    if args.probe:
        print(json.dumps({"sample_rows": rows[:6], "total": len(rows)}, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("WARN: 0 行（全假日窗？）——按成功退出，明日自愈窗补")
        return 0
    ok = write_rows(rows)
    print(json.dumps({"ok": bool(ok), "rows": len(rows)}, ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())

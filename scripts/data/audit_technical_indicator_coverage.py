# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] scripts.data.audit_technical_indicator_coverage
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.factor.technical_indicators; pandas
# [CONSUMERS] Owner/施工会话手动触发（REG-IND-001 回填验收闸，回填后必跑）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] fail-loud：任何批次查询失败/空样本 exit 3 永不假绿；40 列/批分批防 1500+ parts 宽表 CH 内存 241；短窗（<60 行）事件型列 fractal_* 豁免判定仅报告
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 退出码 0=PASS/2=存在全 0 列/3=查询失败或空样本
# [TESTS] 实弹双窗验证（2026-09-16：08 标准窗+09 尾部窗双 PASS）；断言逻辑内嵌 docstring
# [A_module] module_id=scripts-data-ti-coverage-audit | layer=script | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""技术指标宽表全列覆盖审计器（REG-IND-001 验收闸，回填后必跑）。

对 c1_market.technical_indicator 按"单标的+时间窗"样本逐列审计非空率：
    160+ 指标列 100% 非空（fractal_high/fractal_low 等事件型列按稀疏本性豁免判定，
    仅报告不判罚）。

血泪两条（2026-09-16 实证，违反必复发）：
    1. ch_reader.query 失败返回空串——旧版拿空串除零后输出"全 0 列（0）: []"
       假绿，查询失败被当成审计通过。本版 fail-loud：任何批次查询失败/空样本
       一律非零退出。
    2. 162 列单查询在 1500+ active parts 宽表上空载也撞 CH 内存（Code 241→
       HTTP 500）——本版 40 列/批分批查询合并判定。

用法：
    python scripts/data/audit_technical_indicator_coverage.py                 # 000852 daily 2026-08 标准样本
    python scripts/data/audit_technical_indicator_coverage.py --start 2026-09-01 --end 2026-09-16
    python scripts/data/audit_technical_indicator_coverage.py --symbol 600519 --period weekly

退出码：0=PASS；2=存在全 0 列；3=查询失败/空样本（审计不可信）。
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.factor.technical_indicators import autodiscover_technical_indicators
from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

# [ERROR_CONTRACT] 查询失败/空样本→exit 3；全 0 列→exit 2；PASS 才 exit 0；永不输出假绿
QUERY_BATCH = 40  # 1552 parts 宽表实测：162 列单查询必炸 CH 内存，40 列/批安全
_TBL = get_registry().table("market_technical_indicator")  # TableRegistry 真源（#ARCH-CH-024）


def main() -> int:
    ap = argparse.ArgumentParser(description="技术指标宽表全列覆盖审计（fail-loud 分批版）")
    ap.add_argument("--symbol", default="000852", help="样本标的（默认 000852 中证1000）")
    ap.add_argument("--period", default="daily", choices=["daily", "weekly", "monthly"])
    ap.add_argument("--start", default="2026-08-01", help="样本窗起点")
    ap.add_argument("--end", default="2026-08-31", help="样本窗终点")
    args = ap.parse_args()

    autodiscover_technical_indicators()
    all_cols = sorted(TechnicalIndicatorRegistry.list_output_columns())
    print(f"在产指标列: {len(all_cols)}  样本: {args.symbol} {args.period} {args.start}~{args.end}")

    base = (
        f"FROM {_TBL} "
        f"WHERE period='{args.period}' AND symbol='{args.symbol}' "
        f"AND trade_date >= '{args.start}' AND trade_date <= '{args.end}'"
    )
    frames = []
    for i in range(0, len(all_cols), QUERY_BATCH):
        cols = all_cols[i : i + QUERY_BATCH]
        tsv = ch_reader.query(f"SELECT {', '.join(cols)} {base} FORMAT TSV")
        if not tsv or not tsv.strip():
            print(f"FAIL: 第 {i // QUERY_BATCH + 1} 批查询失败/空结果（{cols[0]}~{cols[-1]}）——审计不可信，不得当全绿")
            return 3
        frames.append(pd.read_csv(io.StringIO(tsv), sep="\t", header=None, names=cols))
    df = pd.concat(frames, axis=1)
    total = len(df)
    if total == 0:
        print("FAIL: 样本 0 行——审计不可信")
        return 3

    zero_cols, partial = [], []
    for c in all_cols:
        pct = df[c].notna().sum() / total * 100
        if pct == 0:
            zero_cols.append(c)
        elif pct < 100:
            partial.append((c, round(pct, 1)))
    # 事件型列（fractal_* 只在转折点出值）在短窗口（<60 行）合法为 0——降级警告不判罚；
    # 长窗口下 0% 仍是缺陷（回填缺口的特征是整列空）。
    short_window = total < 60
    hard_zero = [
        c for c in zero_cols
        if not (short_window and c.startswith("fractal_"))
    ]
    soft_zero = [c for c in zero_cols if c not in hard_zero]
    print(f"样本行数: {total}")
    print(f"全 0 列（{len(zero_cols)}）: {zero_cols}")
    if soft_zero:
        print(f"短窗事件型豁免（{len(soft_zero)}）: {soft_zero}")
    print(f"部分非空列（{len(partial)}）: {partial}")
    if hard_zero:
        print("AUDIT FAIL（存在全 0 列）")
        return 2
    print("AUDIT PASS" + ("（含短窗事件型豁免列，见上）" if soft_zero else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

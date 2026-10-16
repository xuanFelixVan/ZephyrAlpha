# [BLUEPRINT] MOD-BT-COND-PACKAGE | docs/03_modules/_domain_backtest/blueprint.md（shadow 接线配套件，待统筹登记）
# [MODULE] zephyr.backtest.regime_validation.ps_shadow
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.data.ch_reader; zephyr.regime.formreg.ps_chronology
# [CONSUMERS] zephyr.backtest.regime_validation.condition_package.load_condition_pack（ps_shadow 参数透传）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] shadow 语义铁律：本件只产出并行记录信号（market_regime_ps/ps_agree 列），
#              禁替换/影响 F4 代理腿（signal_id=F4_BDI_MOMENTUM_Z20）的现有行为与判据地位
#              （替换需另行验证与 Owner 裁定）；两态态源=formreg.ps_chronology（P-S 月频年代学，
#              打靶 PASS 见 formreg/9_prereg_targeting_r2.md），逐日态=所属段 phase 按月展开；
#              右端残段 confirmed=False=离线年代学确认滞后，shadow 右缘为暂定态（meta 如实记录）；
#              一致率=逐日映射对（bull→risk_on/bear→risk_off，两态无 neutral 对应=计不一致）
#              的逐日布尔，禁入任何统计判据/禁当独立样本计 n（观察层，precheck §2.4 同口径）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] kline 000300 空结果→RuntimeError（fail-closed）；ps_chronology 校验异常原样上抛
# [TESTS] 无（shadow 接线验证＝桌面短窗冒烟，产物不入仓）
# [TTL] permanent
# [A_module] module_id=MOD-BT-COND-PACKAGE-PS-SHADOW | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""ps_shadow — P-S 两态引擎 → condition_package 大盘腿 shadow 接线装载器。

两态引擎（P-S 年代学，月频 bull/bear 段表）并行产出到条件包大盘腿的 shadow 列：
    market_regime_ps = 逐日所属 P-S 段 phase（'bull'/'bear'，缺月=NaN）
    ps_agree         = shadow 与 F4 现役态的逐日一致布尔（bull→risk_on/bear→risk_off
                       映射后比对；neutral 无两态对应=不一致；shadow 缺月=None）

本件是消费面接线（formreg 冻结面条款的 shadow 例外）：只记录、只对照、不计 n、
不入判据；F4 代理腿的判据地位零改动（condition_package 既有列与细胞计算不动）。
# [ALGO_FLOW] external: none（shadow 接线暂不登记 algo_flow，随战役归档裁定）
"""

from __future__ import annotations

from typing import Final

import pandas as pd

from zephyr.data import ch_reader

SYMBOL: Final = "000300"  # 打靶标的（9_prereg_targeting_r2.md §1.2 同口径）
_SQL_KLINE: Final = "SELECT trade_date, close FROM c1_market.kline_index WHERE symbol = '{symbol}' ORDER BY trade_date"


def build_ps_shadow() -> tuple[pd.Series, dict]:
    """000300 日频全史 → P-S 年代学 → 逐月两态 phase 序列。

    Returns:
        (monthly_phase, meta)：
        monthly_phase: index=月末 Timestamp，值='bull'/'bear'（段表按月展开，后段覆盖前段）；
        meta: 数据范围/段数/右缘确认标志/最后确认月（如实记录确认滞后）。

    Raises:
        RuntimeError: kline 空结果（fail-closed）。
    """
    from zephyr.regime.formreg import build_chronology, to_monthly  # noqa: PLC0415 — 惰性导入（冻结面隔离）

    rows = ch_reader.query_rows(_SQL_KLINE.format(symbol=SYMBOL), timeout=120)
    if not rows:
        raise RuntimeError(f"kline_index {SYMBOL} 空结果——shadow 态源不可用（fail-closed）")
    df = pd.DataFrame(rows, columns=["trade_date", "close"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    close = df.dropna(subset=["close"]).set_index("trade_date")["close"].sort_index()

    monthly = to_monthly(close)
    _, segs = build_chronology(monthly)

    expanded: dict[pd.Period, str] = {}
    for r in segs.to_dict(orient="records"):
        start = pd.Timestamp(r["start_date"]).to_period("M")
        end = pd.Timestamp(r["end_date"]).to_period("M")
        for p in pd.period_range(start, end, freq="M"):
            expanded[p] = str(r["phase"])
    phase = pd.Series(expanded, name="phase").sort_index()
    phase.index = phase.index.to_timestamp(how="end")  # 月末 Timestamp，与段表口径一致

    confirmed_ends = [str(r["end_date"]) for r in segs.to_dict(orient="records") if bool(r["confirmed"])]
    meta = {
        "symbol": SYMBOL,
        "daily_first": str(close.index.min().date()),
        "daily_last": str(close.index.max().date()),
        "monthly_bars": int(len(monthly)),
        "n_segments": int(len(segs)),
        "right_edge_confirmed": bool(segs.iloc[-1]["confirmed"]) if len(segs) else False,
        "last_confirmed_month": max(confirmed_ends) if confirmed_ends else None,
        "note": "右端残段 confirmed=False=离线年代学确认滞后，shadow 右缘为暂定态",
    }
    return phase, meta


def load_pack_with_ps_shadow(start: str, end: str):
    """条件包 + shadow 列一站式装载（既有列零改动，仅追加 market_regime_ps/ps_agree）。"""
    from zephyr.backtest.regime_validation.condition_package import load_condition_pack  # noqa: PLC0415

    phase, _meta = build_ps_shadow()
    return load_condition_pack(start=start, end=end, ps_shadow=phase)

# [BLUEPRINT] MOD-PA-034 | docs/03_modules/_domain_portfolio_alloc/portfolio_netting/blueprint.md
# [MODULE] zephyr.pf_alloc.core.portfolio_netting
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pandas（纯函数无 IO 无 DB，无本仓内部依赖）
# [CONSUMERS] L-4 范围③④（调权全链/组合聚合层，后续里程碑）；MOD-PA-003 下游可选
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯向量化(无逐行 Python 循环); NaN=诚实缺供不掩盖(不 fillna); 校验 fail-closed(空输入/非DataFrame/负预算/未知策略名/重复索引列抛 ValueError); 同票反向等量权重→净零(代数和); 符号保留(负净权重=组合净空头自然表达); 预算切分逐策略独立缩放互不挪用
# [MODIFY-GUARD] docs/03_modules/_domain_portfolio_alloc/portfolio_netting/blueprint.md
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(空 strategies/非 DataFrame/空索引列/重复索引列/负预算/非有限预算/预算与策略名集合不全等)
# [TESTS] tests/research/pf_alloc/test_portfolio_v0.py
# [A_module] module_id=MOD-PA-034 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""
Portfolio Netting — 组合层 v0 净额轧平与预算切分 (MOD-PA-034)

L-4 多策略组合层引擎里程碑一（l5_project_cards_20261006.md 卡 L-4 范围①②），
PP-001 整装组合 V0 蓝图首块：

    net_positions  — 净额轧平（TDM-F-C2-01 intent netting）
        多策略权重面（每策略一张 date×symbol 目标权重 DataFrame）→ 同标的跨策略
        权重代数和（买 1000+卖 600=净买 400 的权重面版），符号保留=多空自然表达。
        两策略同票等量反向 → 净零（对冲净额）。

    split_capital  — 预算切分（TDM-F-C1 Millennium pod 模式）
        组合级多策略权重面（columns=MultiIndex(strategy, symbol)）按策略名资金
        比例逐策略缩放（各 sleeve 账本独立、互不挪用）后再轧平出组合净面。

语义约定（v0 冻结）:
    - 权重面: index=交易日, columns=标的代码, 值=带符号目标权重（正多负空）。
    - NaN=诚实缺供: 策略在某格缺供（值 NaN）→ 净面该格 NaN（不 fillna 掩盖）。
      列缺席（策略面根本没有该标的列）= 该策略无观点，贡献记 0（docstring 声明）。
    - 净面列序=标的字典序（groupby 确定性输出）；日期=各面并集。
    - 纯向量化: concat + groupby 完成，无逐行 Python 循环。
    - 输入校验 fail-closed: 非法输入一律 ValueError，禁止静默修正。

与邻件分工（防责任重叠）:
    - MOD-PA-002 信号合成器: 信号级投票/共振/去重（StrategySignal 列表），非权重面。
    - MOD-PA-003 资金分配器: 单策略内部权重规整（容量/MaxDD/冷启动），非跨策略聚合。
    - MOD-POS-021 FirmRiskAggregator: 实盘 Firm 层风险聚合（position 域），非本件。

# [ALGO_FLOW] external: docs/03_modules/_domain_pf_alloc/algo_flow/portfolio_netting.yaml

依据: trading_map_07_f_portfolio.md TDM-F-C1 / TDM-F-C2-01；卡 L-4（20261006）
SSoT: depgraph MOD-PA-034（node_id=16422915）
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final

import pandas as pd

__all__: Final = [
    "net_positions",
    "split_capital",
]


def _validate_weight_face(df: pd.DataFrame, name: str) -> None:
    """校验单张权重面（fail-closed）。

    Raises:
        ValueError: 非 DataFrame/空面/重复或空索引/重复或空列。
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"策略 '{name}' 的权重面必须是 pd.DataFrame, got {type(df).__name__}")
    if df.empty:
        raise ValueError(f"策略 '{name}' 的权重面为空（禁止空面进入轧平）")
    if df.index.empty or df.columns.empty:
        raise ValueError(f"策略 '{name}' 的权重面索引或列为空")
    if not df.index.is_unique:
        raise ValueError(f"策略 '{name}' 的权重面索引含重复日期（fail-closed 禁止隐式聚合）")
    if not df.columns.is_unique:
        raise ValueError(f"策略 '{name}' 的权重面列含重复标的（fail-closed 禁止隐式重复计数）")
    if df.index.hasnans or df.columns.hasnans:
        raise ValueError(f"策略 '{name}' 的权重面索引或列含 NaN（索引/列必须是完整标的与日期）")


def _honest_group_net(combined: pd.DataFrame, symbol_level: int = -1) -> pd.DataFrame:
    """跨策略诚实轧平：同标的代数和，任一供方该格 NaN → 净格 NaN。

    combined: MultiIndex 列（level 0=策略名, 末层=标的）的缩放后权重面。
    纯向量化：groupby(sum/count/size) + where，无逐行循环。
    count(非 NaN 计数)==组内列数(供方全到) 才保留代数和，否则 NaN——不 fillna 掩盖。
    """
    transposed = combined.T
    grp = transposed.groupby(level=symbol_level)
    sums = grp.sum()  # skipna 语义：NaN 记 0 参与和
    counts = grp.count()  # 每格非 NaN 供方数
    members = grp.size()  # 每标的组的供方列数（列面固定，逐组常数）
    net = sums.where(counts.eq(members, axis=0))
    return net.T.reindex(combined.index)


def net_positions(strategies: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """多策略权重面净额轧平（TDM-F-C2-01 intent netting）。

    同标的跨策略权重代数和，符号保留（正=净多，负=净空，净零=对冲）。

    Args:
        strategies: 策略名→权重面（index=交易日, columns=标的, 值=带符号目标权重）。

    Returns:
        组合净权重面（index=各面日期并集, columns=出现过的标的字典序）。
        某策略列缺席=该策略无观点（贡献 0）；某策略列在但格值 NaN 或面无该
        日期行=缺供，净面该格 NaN（诚实传播，不 fillna）。

    Raises:
        ValueError: strategies 为空/键非非空字符串/值非 DataFrame/面校验失败。
    """
    if not isinstance(strategies, dict):
        raise ValueError(f"strategies 必须是 dict[str, pd.DataFrame], got {type(strategies).__name__}")
    if not strategies:
        raise ValueError("strategies 为空（净额轧平至少需要一个策略权重面）")
    for name, face in strategies.items():
        if not isinstance(name, str) or not name:
            raise ValueError(f"策略名必须是非空字符串, got {name!r}")
        _validate_weight_face(face, name)

    combined = pd.concat(
        list(strategies.values()),
        axis=1,
        keys=list(strategies.keys()),
        names=["strategy", "symbol"],
    )
    return _honest_group_net(combined, symbol_level=-1)


def split_capital(weights: pd.DataFrame, budget: dict[str, float]) -> pd.DataFrame:
    """预算切分（TDM-F-C1 Millennium pod 模式）：逐策略缩放后再轧平。

    各 sleeve 账本独立、互不挪用：策略 s 的权重列整体乘 budget[s]，再跨策略
    诚实轧平（同 net_positions 语义）出组合净面。

    Args:
        weights: 组合级多策略权重面，columns=MultiIndex(level0=策略名, 末层=标的)。
        budget: 策略名→资金比例（>=0 有限值；键集合必须与 weights 策略集合全等）。

    Returns:
        预算切分+轧平后的组合净权重面（语义同 net_positions 输出）。

    Raises:
        ValueError: weights 非 DataFrame/空/列非 MultiIndex；
                    budget 空/负值/非有限值/未知策略名/漏策略名。
    """
    if not isinstance(weights, pd.DataFrame):
        raise ValueError(f"weights 必须是 pd.DataFrame, got {type(weights).__name__}")
    if weights.empty or weights.index.empty or weights.columns.empty:
        raise ValueError("weights 为空（禁止空面进入预算切分）")
    if not isinstance(weights.columns, pd.MultiIndex) or weights.columns.nlevels < 2:
        raise ValueError("weights 列必须是 MultiIndex(level0=策略名, 末层=标的) 以识别策略归属")
    if not isinstance(budget, dict):
        raise ValueError(f"budget 必须是 dict[str, float], got {type(budget).__name__}")
    if not budget:
        raise ValueError("budget 为空（预算切分至少需要一个策略资金比例）")

    strategy_level = weights.columns.get_level_values(0)
    present = set(strategy_level)
    budget_keys = set(budget)
    unknown = budget_keys - present
    if unknown:
        raise ValueError(f"budget 含未知策略名（不在 weights 中）: {sorted(unknown)}")
    missing = present - budget_keys
    if missing:
        raise ValueError(f"weights 含未供预算的策略名（缺供 fail-closed）: {sorted(missing)}")
    for name, ratio in budget.items():
        if not isinstance(ratio, (int, float)) or isinstance(ratio, bool):
            raise ValueError(f"策略 '{name}' 的预算比例必须是有限数值, got {ratio!r}")
        if ratio < 0:
            raise ValueError(f"策略 '{name}' 的预算比例为负（负预算 fail-closed）: {ratio}")
        if ratio != ratio or ratio in (float("inf"), float("-inf")):
            raise ValueError(f"策略 '{name}' 的预算比例非有限值: {ratio}")

    # 逐列乘各自策略预算：Series 对齐 MultiIndex 列后整列广播（纯向量化，无循环）
    factors = pd.Series(
        [budget[s] for s in strategy_level],
        index=weights.columns,
        dtype="float64",
    )
    scaled = weights.mul(factors, axis=1)
    return _honest_group_net(scaled, symbol_level=-1)

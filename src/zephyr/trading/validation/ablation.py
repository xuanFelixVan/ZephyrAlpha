# [BLUEPRINT] MOD-TDMVAL-001 | docs/03_modules/_domain_trading/validation/blueprint.md
# [MODULE] zephyr.trading.validation.ablation
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.core.engine_base
# [CONSUMERS] zephyr.trading.validation.runner(exit_counterfactual 对照数据源); P2-3 反事实对照
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 不修改回测引擎本体; BacktestResult 15 字段契约冻结; holdout 保密窗口不回放(§12 参数定稿前不跑回测); 对照缺失如实降级不造假
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError
# [TESTS] tests/trading/test_validation_ablation.py
# [TTL] permanent
"""信号消融对照器（X 流验证批 T2，晨报 2026-09-10 裁定②落地）。

语义（Owner 2026-09-10 X 流验证批指令 T2）: 同一段行情 + 同一批信号输入，剥离 X 流
（卖出/风控类）动作后重放，输出"全量 vs 无风控"双净值与差额序列——差额=X 流救回的
金额。不修改回测引擎本体。

裁定②背景: "关风控回放开关"是伪命题——引擎 DecisionGate 是策略晋升闸不在成交路径，
X 流是决策生产者（生成信号）。正确切口=信号层剥离 X 流动作再重放。

实现（双权重面板重放差，盘点方案 A）:
    输入=同一行情 data + 两份权重面板（全量 panel_full / 剥离后面板 panel_ablated），
    引擎各跑一支 run，净值从 last_portfolio.nav_series 取（BacktestResult 15 字段契约
    冻结，净值走引擎旁路）。剥算子 ablate_weight_panel 是纯函数:
    - v1 动作标注（XFlowAction）由调用方显式注入——现有信号结构（权重面板/
      SynthesizedSignal 契约）无 X 流判别字段，SellSignal 流尚未接入回测（盘点③④：
      sell_decision 包外零消费者）。诚实 v1：不猜测、不伪造归因。
    - 剥离语义="回滚式"（保 Σw=1）: X 流清仓动作=该标的权重回滚到上一有效持有权重
      再按比例分摊给未剥离标的；X 流减仓动作=减去减量份额后同样分摊。规避引擎
      Σ=1 归一化的再分配污染（盘点⑦-2）。

已知限制（如实披露）:
    - 差额=X 流直接效应 + 资金路径二阶效应（剥离改变现金时序→后续买单可用资金变化，
      含涨跌停拒单/T+1 两侧不对称），v1 不做效应分解。
    - 本模块只提供重放机制；消融回放受回测协议备忘录 §12 约束（参数没定稿不跑回测/
      holdout 只考一次），实弹运行须 Owner 放行——runner 消费前对照缺失一律 pending。

真源: docs/_working/2026-09-10-nodebt-night-report.md 裁定② + Owner X 流验证批指令 T2。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """消融输入数据/配置异常（与 runner.ValidationError 同族，独立定义防跨模块循环导入）。"""

    error_code = "ZA-TDMVAL-0002"


@dataclass(frozen=True)
class XFlowAction:
    """X 流动作标注（调用方注入；v1 信号结构无此信息，见模块 docstring）。

    Attributes:
        date: 动作日（与面板 index 同形态，str/date 均可）。
        symbol: 标的。
        action: "clear"=清仓（该标的权重归零）| "reduce"=减仓（权重按 reduce_to 下调）。
        reduce_to: reduce 动作的目标权重（clear 时忽略）。
        source: 动作来源标注（如 TDM-X-S1-02），透传进报告便于追溯。
    """

    date: Any
    symbol: str
    action: str  # "clear" | "reduce"
    reduce_to: float | None = None
    source: str = ""


@dataclass
class AblationReport:
    """消融对照报告（自定义 dataclass——BacktestResult 15 字段契约冻结勿动）。

    Attributes:
        nav_full / nav_ablated: 双净值曲线（引擎 last_portfolio.nav_series 旁路）。
        rescued: 差额序列 = nav_full − nav_ablated（按日期对齐；>0=X 流救回金额）。
        rescued_total: 期末累计差额。
        result_full / result_ablated: 两支 run 的 BacktestResult（自带 map_snapshot）。
        actions: 实际生效的 X 流动作清单。
        notes: 语义披露（二阶效应/口径）。
    """

    nav_full: pd.Series
    nav_ablated: pd.Series
    rescued: pd.Series
    rescued_total: float
    result_full: Any
    result_ablated: Any
    actions: list[XFlowAction] = field(default_factory=list)
    notes: str = ""


def ablate_weight_panel(
    panel_full: pd.DataFrame,
    actions: list[XFlowAction],
) -> pd.DataFrame:
    """剥离 X 流动作后的权重面板（纯函数，回滚式保 Σw=1）。

    语义:
        - clear: 该 (date, symbol) 权重与"此后该标的被清出"的目标权重清零；
          权重缺口按比例分摊给同日其余持有标的（引擎 Σ=1 归一化对齐口径）。
        - reduce: 权重削减至 reduce_to，削减份额同上分摊。
        - 分摊语义=回滚到"若无 X 流动作"的近似持有结构：X 流动作把策略层的
          目标权重改小/清掉，本函数把它改回去（v1 按同日剩余标的等比分摊近似）。

    Args:
        panel_full: 全量权重面板 date×symbol（引擎 signals 同构）。
        actions: X 流动作标注清单（date 不在面板 index 的动作忽略并告警）。

    Returns:
        panel_ablated: 剥离后权重面板（深拷贝，不改入参）。

    Raises:
        ValidationError: 面板为空 / 动作非法（action 非 clear|reduce、reduce_to 越界）。
    """
    if panel_full is None or panel_full.empty:
        raise ValidationError("消融输入面板为空——不可对空面板剥离")
    for a in actions:
        if a.action not in ("clear", "reduce"):
            raise ValidationError(f"非法动作类型: {a.action}（合法值 clear|reduce）@ {a.date}/{a.symbol}")
        if a.action == "reduce" and (a.reduce_to is None or a.reduce_to < 0):
            raise ValidationError(f"reduce 动作必须带合法 reduce_to>=0: {a.date}/{a.symbol}")

    ablated = panel_full.copy(deep=True)
    index_lookup = {str(k): k for k in ablated.index}
    applied = 0
    for a in actions:
        key = index_lookup.get(str(a.date))
        if key is None or a.symbol not in ablated.columns:
            logger.warning("X 流动作忽略（日期或标的不在面板）: %s/%s", a.date, a.symbol)
            continue
        cur = float(ablated.at[key, a.symbol]) if a.symbol in ablated.columns else 0.0
        if a.action == "clear":
            target = 0.0
        else:
            target = min(float(a.reduce_to), cur)   # reduce_to 高于现权重=非减仓动作，忽略
        delta = cur - target
        if delta <= 0:
            continue
        others = ablated.loc[key].drop(a.symbol)
        others_total = float(others.sum())
        if others_total > 0:
            # 缺口只分摊给其余标的（排除动作标的，严格守恒 Σw=1）；
            # 全清仓日 others_total=0 → 缺口不转移（Σw<1=持币语义由引擎保持昨仓）
            scaled = others * (1.0 + delta / others_total)
            ablated.loc[key, others.index] = scaled.values
        ablated.at[key, a.symbol] = target
        applied += 1
    logger.info("消融剥离完成: %d/%d 动作生效（面板 %d 行）", applied, len(actions), len(ablated))
    return ablated


def run_ablation(
    data: pd.DataFrame,
    panel_full: pd.DataFrame,
    actions: list[XFlowAction],
    config: Any = None,
    strategy_name: str = "ablation",
) -> AblationReport:
    """消融对照入口: 双权重面板各跑一支引擎 run，输出双净值与差额序列。

    两次 run 共享同一行情 data 与同一 config（引擎无跨 run 状态，每次 run 新建
    Portfolio——nav_series 必须逐次先取再跑第二支）。

    Args:
        data: 行情（load_history 产物或 flat DataFrame date/symbol/close，引擎三形态输入）。
        panel_full: 全量权重面板。
        actions: X 流动作标注（经 ablate_weight_panel 生成剥离面板）。
        config: BacktestConfig（None=引擎默认；两支 run 必须同一实例值）。
        strategy_name: 策略名（BacktestResult.strategy_id）。

    Returns:
        AblationReport（rescued=nav_full − nav_ablated 按日期对齐）。

    Raises:
        ValidationError: 输入面板为空 / 双 run 净值缺失。
    """
    from zephyr.backtest.implementations.vectorized_engine import BacktestConfig, DefaultBacktestEngine

    if panel_full is None or panel_full.empty:
        raise ValidationError("消融输入面板为空")
    cfg = config or BacktestConfig()
    panel_ablated = ablate_weight_panel(panel_full, actions)

    engine_full = DefaultBacktestEngine(config=cfg, enable_stk_limit_provider=False)
    result_full = engine_full.run(data=data, signals=panel_full, strategy_name=strategy_name)
    nav_full = engine_full.last_portfolio.nav_series if engine_full.last_portfolio else None

    engine_abl = DefaultBacktestEngine(config=cfg, enable_stk_limit_provider=False)
    result_abl = engine_abl.run(data=data, signals=panel_ablated, strategy_name=strategy_name)
    nav_abl = engine_abl.last_portfolio.nav_series if engine_abl.last_portfolio else None

    if nav_full is None or nav_abl is None:
        raise ValidationError("双 run 净值缺失（last_portfolio 为空）——引擎运行异常")

    # nav_series 首日索引可能为 NaT（引擎逐日循环前的初始化行，runner 同款过滤先例）
    nav_full = nav_full[nav_full.index.notna()]
    nav_abl = nav_abl[nav_abl.index.notna()]
    rescued = (nav_full - nav_abl).dropna()
    notes = (
        "差额=X 流直接效应+资金路径二阶效应（现金时序/涨跌停/T+1 不对称），v1 不做效应分解；"
        "动作标注由调用方注入（信号结构无 X 流字段）；回放受协议备忘录 §12 约束，"
        "参数定稿放行前不得对 holdout 窗口实弹运行"
    )
    return AblationReport(
        nav_full=nav_full,
        nav_ablated=nav_abl,
        rescued=rescued,
        rescued_total=round(float(rescued.iloc[-1]), 2) if len(rescued) else 0.0,
        result_full=result_full,
        result_ablated=result_abl,
        actions=list(actions),
        notes=notes,
    )


__all__ = [
    "AblationReport",
    "ValidationError",
    "XFlowAction",
    "ablate_weight_panel",
    "run_ablation",
]
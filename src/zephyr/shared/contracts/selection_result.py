# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.selection_result
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.pf_core.strategies.daban_sleeve_strategy; zephyr.pf_core.strategies.multifactor_sleeve_strategy; zephyr.pf_core.strategies.event_driven_sleeve_strategy
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] frozen dataclass; urgency∈{immediate,next_open,gradual}; confidence∈[0,1]; 手工维护（非 codegen 托管——SSoT=21号设计备忘录 §3.5，非 cross_layer_contracts.yaml，故不加 CODGEN 标记）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] urgency 非法值→ValueError; confidence 越界 [0,1]→ValueError
# [TESTS] tests/pf_core/test_selection_result_contract.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: infrastructure
# category: data_contract
# status: active
# created: "2026-08-21"
# ---

"""
ZephyrAlpha — shared/contracts/selection_result.py

CTR-P1-018: SelectionResult / 选股统一结果契约（手工维护，编号自续 cross_layer_contracts.yaml CTR-P1-017）

选股引擎（G05）→ firm 层 统一接口契约。3 个 sleeve（打板/多因子/事件驱动）异构
（信号源/频率/周期全不同），但须对接同一 firm 层（MOD-POS-021 FirmRiskAggregator），
统一接口是 Model A"统一 firm 风险框架 + 差异化 sleeve"的工程落地——差异化在接口
实现内部，统一在接口签名（21 号 §3.5 / §4.3 / §5.1）。

签名定稿（21 号 §3.5 L224-235 + v1.1.1 L241-261 施工环节补全）：
    输入：SignalInput(as_of_date, universe, regime_budget)   # regime_budget=数字，非 regime 状态
    处理：sleeve.select(SignalInput) → SelectionResult
    输出：SelectionResult(target_portfolio, signals, confidence, metadata)  # 轻量 4 字段（L383 裁定不过重）

urgency↔convergence_window 映射（21 号 L255-259）：
    immediate  盘中立即   1-2 天  打板 sleeve     T 日盘中买入，T+1 卖出
    next_open  次日开盘   2-3 天  事件驱动 sleeve T+1 开盘买入，2-3 天收敛
    gradual    逐步建仓   3-5 天  多因子 sleeve   T+1 起 3-5 天逐步建仓

字段语义（21 号 L232-235）：
    target_portfolio  list[TargetPosition(symbol, target_weight, signal_source, urgency)]
    signals           原始信号留痕，供归因与 G07 相关性验证
    confidence        sleeve 自评置信度 ∈[0,1]，喂 firm 层 PerformanceScore（30 号 §2.2）；
                      算法待裁定（21 号 §6 待裁定-5，四候选路径登记在案），当前由 sleeve 自填占位
    metadata          sleeve 私有信息（打板情绪周期阶段/多因子因子贡献度/事件冲击衰减阶段）

[MATURITY] testing（宪章 B-007：新模块一律 testing 封顶，production 启用属 Owner）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Final

# ── urgency 合法值（21 号 §3.5 L255-259 urgency↔convergence_window 映射表）──
URGENCY_IMMEDIATE: Final[str] = "immediate"  # 盘中立即（打板 sleeve）
URGENCY_NEXT_OPEN: Final[str] = "next_open"  # 次日开盘（事件驱动 sleeve）
URGENCY_GRADUAL: Final[str] = "gradual"  # 逐步建仓（多因子 sleeve）
VALID_URGENCY: Final[tuple[str, ...]] = (URGENCY_IMMEDIATE, URGENCY_NEXT_OPEN, URGENCY_GRADUAL)


@dataclass(frozen=True)
class TargetPosition:
    """目标持仓（选股引擎输出单元）。

    urgency : 执行时序 ∈ {immediate, next_open, gradual}，由 sleeve 按信号强度与
        持仓周期自决（21 号 L261）；convergence_window 在 StrategyBook 层持有，
        不在本契约（21 号 §3.7 边界裁定）。
    """

    symbol: str
    target_weight: float
    signal_source: str
    urgency: str

    def __post_init__(self) -> None:
        if self.urgency not in VALID_URGENCY:
            raise ValueError(
                f"TargetPosition: urgency 非法值 {self.urgency!r}，合法值={VALID_URGENCY}"
            )


@dataclass(frozen=True)
class SignalInput:
    """选股标准输入（21 号 §3.5 核心 3 字段 + v1.1.1 扩展 2 字段）。

    as_of_date    信号产出日
    universe      候选池（漏斗①生成后）
    regime_budget regime 风险节流后的 budget 数字（非 regime 状态，21 号 L227 强调）
    signals       L2-C 产出的原始信号（v1.1.1 扩展：打板=双引擎融合输入负载/
                  多因子=因子打分/事件=事件冲击负载），元素形态各 sleeve 自定
    metadata      sleeve 私有上下文（v1.1.1 扩展）
    """

    as_of_date: date
    universe: list[str]
    regime_budget: float
    signals: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SelectionResult:
    """选股统一结果（21 号 §3.5 轻量 4 字段，L383 裁定不过重）。

    全字段带默认值，空结果（SelectionResult()）= 合法空仓输出。
    confidence ∈ [0,1] 越界即 ValueError（契约违反，非降级场景）。
    """

    target_portfolio: list[TargetPosition] = field(default_factory=list)
    signals: list[Any] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"SelectionResult: confidence 越界 {self.confidence}，合法域=[0,1]"
            )


__all__: Final = [
    "URGENCY_GRADUAL",
    "URGENCY_IMMEDIATE",
    "URGENCY_NEXT_OPEN",
    "VALID_URGENCY",
    "SelectionResult",
    "SignalInput",
    "TargetPosition",
]

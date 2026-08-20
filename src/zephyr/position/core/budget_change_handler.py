# [BLUEPRINT] MOD-POS-022 | docs/03_modules/_domain_position/budget_change_handler/blueprint.md
# [MODULE] zephyr.position.core.budget_change_handler
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.strategy_book
# [CONSUMERS] MOD-POS-020(StrategyBook收rebalance指令); MOD-POS-021(FirmRiskAggregator收ForcedTrim); RegimeMetaAllocator(收BudgetChangeHandled反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只处理budget下调(上调简单直接抬高上限); 三级升级Tier1封锁→Tier2策略自主→Tier3强裁; 策略不能说"我不卖"(rebalance_to_budget必返回适配portfolio); convergence_window按换手率差异化; 每级独立事件可log可复盘; state缺失=无活跃升级返回NO_ACTION(进程内缓存语义; Phase2 DB持久化后读取失败场景适用fail-closed假设Tier1封锁)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BudgetChangeError(ZA-POS-0040); RebalanceTimeoutError(ZA-POS-0042)
# [TESTS] tests/position/test_budget_change_handler.py
# [A_module] module_id=MOD-POS-022 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


BudgetChangeHandler — Budget变动处理器 (MOD-POS-022)

A 模型（30_multi_strategy_concurrency §2.4）的执行层。当 RegimeMetaAllocator 产出新
BudgetAllocation 导致某策略 budget 变动时，本模块负责**把 budget 变动落地到
StrategyBook**——三级升级（Tier 1 封锁 → Tier 2 自主 → Tier 3 强裁），确保策略
适配新 budget。

核心原则（30_multi_strategy_concurrency §2.4）：budget 是硬约束，策略的自主权在"怎么适应 budget"，
不在"要不要适应"。**策略不能说"我不卖"**。三级升级而非直接强砍：尊重策略自主权
（决定砍哪个）+ 避免随机时刻强制卖出的高成本。

三级升级（§2.4）：
    Tier 1（立即，被动）：封锁新仓，现有仓位不动
    Tier 2（Tier 1 后立即，策略自主）：发 rebalance_to_budget，策略自选砍哪些
    Tier 3（Tier 2 窗口超时 / firm 风险违例，强制）：按比例强行裁剪所有仓位

收敛检测（§2.4 Tier 2→Tier 3）：
    ① 仓位差收敛：|实际总仓位 - target_budget| / target_budget < ε_pos（5%）
    ② 持续性：连续维持 ε_days 日（1 个交易日）
    ③ 无新违例：窗口内无新的 firm 层风险违例

防抖（§6 待裁定，theledgermind 2026-05 实证 5% 为 return/cost trade-off 最优点）：
    日内抖动 <5% 忽略；日间累计趋势 >10% 强制触发（防抖不过度）

不做什么：budget 计算（归 RegimeMetaAllocator）/ 选股仓位裁决（归 StrategyBook/MOD-POS-001）
         / 决定砍哪个仓位（Tier 2 策略自主，Tier 3 按比例 dumb）/ 执行交易（归 D-EX-CORE）
         / 处理 budget 上调（上调简单，直接抬高上限自然部署）

设计决策：本模块生成指令（FreezeNewPositions/RebalanceRequest/ForcedTrim）但不直接
         调用 broker/strategy_book——调用者负责执行指令。这使得本模块可纯单元测试，
         且与执行层解耦（circuit breaker/大宗交易/TWAP 等执行细节归 D-EX-CORE）。

依据: 30_multi_strategy_concurrency §2.4 + 33_budget_change_handler §3.4 + blueprint §3
SSoT: depgraph MOD-POS-022
Version: 1.0.1

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: budget 变动事件
#   fields: strategy_id + old_budget + new_budget + strategy_type（打板/多因子/事件驱动）
#   code: handle_budget_change L286-292
# - id: I2
#   name: 策略当前实际暴露 current_exposure
#   fields: 策略实际总仓位占比（收敛检查用）
#   code: check_convergence L365-368
# 层: 算法
# - id: A1
#   name_zh: ① 防抖裁决（五条规则）
#   name_en: handle_budget_change
#   intro: budget 变动先过防抖筛子：上调直接放行、小抖动忽略、大下调才触发升级
#   desc: 规则1 上调→NO_ACTION 不防抖；规则2 收敛中→re-target；规则3 下调<5% 且累计<10%→DEBOUNCE 忽略；规则4/5 ≥5% 或日间累计>10%→触发三级升级（L320-363）
#   inputs: I1
#   outputs: BudgetChangeResult（动作+状态+指令）
#   invariant: 只处理 budget 下调（上调直接抬高上限）
# - id: A2
#   name_zh: ② 三级升级触发 Tier1+Tier2
#   name_en: _trigger_three_tier_escalation
#   intro: 立即发 Tier1 封锁新仓指令 + Tier2 策略自主 rebalance 请求（含收敛窗口）
#   desc: Tier1 FreezeNewPositions（撤买单留卖单）→ Tier2 RebalanceRequest（new_budget+convergence_window 打板2天/多因子4天/事件驱动3天），状态机置 TIER_2_REBALANCE 记窗口截止（L468-520）
#   inputs: A1
#   outputs: FreezeNewPositions + RebalanceRequest 指令
#   invariant: 策略不能说"我不卖"（rebalance_to_budget 必返回适配 portfolio）
# - id: A3
#   name_zh: ③ 收敛检查
#   name_en: check_convergence
#   intro: 窗口内查实际仓位是否贴近新预算：差<5%且连续1日算收敛，否则超时升 Tier3
#   desc: |exposure−target|/target<5% → 持续计数+1 ≥1日 → CONVERGED；未收敛重置计数；now≥window_end → 升级 Tier3（L404-445）
#   inputs: I2
#   outputs: CONVERGED / WAITING / 升级 Tier3
#   invariant: 收敛需仓位差收敛+持续性+无新违例
# - id: A4
#   name_zh: ④ Tier3 按比例强裁
#   name_en: _escalate_to_tier3
#   intro: 超时未收敛就按统一比例硬砍所有仓位，dumb but safe
#   desc: trim_ratio=(exposure−target)/exposure（L595）；exposure≤0 或已≤target 直接 CONVERGED；否则发 ForcedTrim（L562-612）
#   inputs: A3
#   outputs: ForcedTrim 指令（trim_ratio）
# 层: 输出
# - id: O1
#   name_zh: rebalance 指令（FreezeNewPositions/RebalanceRequest）
#   name_en: rebalance instructions
#   intro: Tier1/Tier2 指令交调用者发给 StrategyBook 执行，本模块不直接碰执行层
#   invariant: 只生成指令不执行（与 D-EX-CORE 解耦）
#   downstream: MOD-POS-020 StrategyBook（收 rebalance 指令）
# - id: O2
#   name_zh: 强裁指令 ForcedTrim + 处理反馈
#   name_en: ForcedTrim + BudgetChangeHandled
#   intro: Tier3 等比裁剪指令给 Firm 层执行，处理结果反馈分配器
#   downstream: MOD-POS-021 FirmRiskAggregator（收 ForcedTrim）; RegimeMetaAllocator MOD-PA-007（收 BudgetChangeHandled 反馈）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# I2 --> A3
# A3 --> A4
# A2 --> O1
# A4 --> O2
# A3 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# ── 常量（参数来源：30_multi_strategy_concurrency §2.4/§6 + 33号 §3.4）──

# 防抖阈值（§6，theledgermind 2026-05 实证 5% 最优）
DEBOUNCE_THRESHOLD = 0.05  # budget 变动 <5% 忽略（日内抖动）
CUMULATIVE_TREND_THRESHOLD = 0.10  # 连降累计 >10% 必须执行（日间趋势）

# 收敛检测阈值（§2.4 Tier 2→Tier 3）
CONVERGENCE_EPS_POS = 0.05  # 仓位差 <5% 视为收敛
CONVERGENCE_EPS_DAYS = 1  # 连续维持 1 日

# 默认 convergence_window（§6.4，按换手率差异化）
DEFAULT_CONVERGENCE_WINDOWS = {
    "打板": timedelta(days=2),  # 高换手 1-2 天自然收敛
    "多因子": timedelta(days=4),  # 低换手需更多时间
    "事件驱动": timedelta(days=3),  # 中等换手
}


class TierLevel(Enum):
    """三级升级级别（30_multi_strategy_concurrency §2.4）。"""

    IDLE = "idle"  # 空闲（无活跃升级）
    TIER_1_LOCK = "tier_1_lock"  # 封锁新仓（立即，被动）
    TIER_2_REBALANCE = "tier_2_rebalance"  # 策略自主 rebalance（建议，策略自主）
    TIER_3_FORCE_TRIM = "tier_3_force_trim"  # 强制裁剪（强制，firm 层）
    CONVERGED = "converged"  # 收敛完成


@dataclass(frozen=True)
class FreezeNewPositions:
    """Tier 1 指令：封锁新仓（CTR-POS-022-F）。

    策略收到后：不允许开任何新仓，现有仓位不动。
    撤未成交买单（减仓方向不超限），保留卖单。
    """

    strategy_id: str
    cancel_pending_buy_orders: bool = True  # 撤未成交买单
    keep_pending_sell_orders: bool = True  # 卖单不撤
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass(frozen=True)
class RebalanceRequest:
    """Tier 2 指令：策略自主 rebalance（CTR-POS-022-R）。

    策略收到后：调用 rebalance_to_budget(new_budget) 自选砍哪些仓位。
    **策略不能说"我不卖"**——必须返回适配新 budget 的 target_portfolio。
    """

    strategy_id: str
    new_budget: float
    convergence_window: timedelta  # 按换手率差异化
    interface_contract: str = "rebalance_to_budget() 必须返回 target_portfolio 总暴露 ≤ new_budget"
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass(frozen=True)
class ForcedTrim:
    """Tier 3 指令：强制按比例裁剪（CTR-POS-022-T，dumb but safe）。

    策略/FirmRiskAggregator 收到后：所有仓位 × trim_ratio 等比缩放。
    """

    strategy_id: str
    trim_ratio: float  # 裁剪比例（如 0.2 = 所有仓位削 20%）
    reason: str  # 触发原因（Tier 2 超时 / firm 风险违例）
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass
class TierState:
    """单策略 budget 变动的三级升级状态机。

    每个策略独立一份状态，进程内缓存（生产环境可持久化到 DB）。
    """

    strategy_id: str
    current_tier: TierLevel = TierLevel.IDLE
    old_budget: float = 0.0
    target_budget: float = 0.0
    tier1_at: datetime | None = None
    tier2_at: datetime | None = None
    tier3_at: datetime | None = None
    converged_at: datetime | None = None
    convergence_window_end: datetime | None = None
    cumulative_budget_change: float = 0.0  # 累计 budget 变动（防抖"日间趋势"判定用）
    last_budget_change_date: str = ""  # 上次 budget 变动日期（YYYY-MM-DD，日内防抖重置用）
    convergence_days_satisfied: int = 0  # 连续满足收敛条件的天数（§2.4 ε_days）
    strategy_type: str = "多因子"  # 策略类型（打板/多因子/事件驱动），re-target 重置窗口查询用
    instructions_issued: list[dict[str, Any]] = field(default_factory=list)  # 已发出的指令记录

    def is_in_convergence(self) -> bool:
        """是否正在收敛流程中（Tier 1/2/3 任一活跃）→ re-target 不防抖。"""
        return self.current_tier in (
            TierLevel.TIER_1_LOCK,
            TierLevel.TIER_2_REBALANCE,
            TierLevel.TIER_3_FORCE_TRIM,
        )


@dataclass
class BudgetChangeResult:
    """handle_budget_change 返回结果。"""

    action: str  # 动作描述
    state: TierState  # 更新后的状态
    instructions: list[dict[str, Any]]  # 待执行指令列表（调用者负责执行）


class BudgetChangeHandler:
    """Budget 变动处理器（MOD-POS-022）。

    使用方式：
        handler = BudgetChangeHandler()
        result = handler.handle_budget_change("s1", 0.30, 0.20, strategy_type="打板")
        # result.instructions 含 FreezeNewPositions + RebalanceRequest
        # 调用者负责执行这些指令（发送给 StrategyBook）

        # Tier 2 窗口结束后检查收敛
        result = handler.check_convergence("s1", current_exposure=0.22)
        # 若未收敛 → result.instructions 含 ForcedTrim
    """

    def __init__(
        self,
        convergence_windows: dict[str, timedelta] | None = None,
        debounce_threshold: float = DEBOUNCE_THRESHOLD,
        cumulative_trend_threshold: float = CUMULATIVE_TREND_THRESHOLD,
        eps_pos: float = CONVERGENCE_EPS_POS,
        eps_days: int = CONVERGENCE_EPS_DAYS,
    ) -> None:
        """初始化。

        Args:
            convergence_windows: 各策略 convergence_window（按换手率差异化）。
                30_multi_strategy_concurrency §6.4：打板 2 天，多因子 4 天，事件驱动 3 天。
            debounce_threshold: 日内防抖阈值（默认 5%）。
            cumulative_trend_threshold: 日间累计趋势阈值（默认 10%）。
            eps_pos: 收敛仓位差容忍度（默认 5%）。
            eps_days: 收敛持续性天数（默认 1 日）。
        """
        self.convergence_windows = convergence_windows or dict(DEFAULT_CONVERGENCE_WINDOWS)
        self.debounce_threshold = debounce_threshold
        self.cumulative_trend_threshold = cumulative_trend_threshold
        self.eps_pos = eps_pos
        self.eps_days = eps_days
        self._active_states: dict[str, TierState] = {}  # strategy_id → TierState

    # ══ 公共接口 ══════════════════════════════════════════════════════

    def handle_budget_change(
        self,
        strategy_id: str,
        old_budget: float,
        new_budget: float,
        strategy_type: str = "多因子",
        current_date: str | None = None,
    ) -> BudgetChangeResult:
        """主入口：处理 budget 变动，裁决是否触发三级升级。

        规则优先级（§3.4 伪代码）：
            1. 上调 → 即时返回不防抖（StrategyBook 自然部署）
            2. 已在收敛中 → re-target 不防抖
            3. 首次下调 <5% → 防抖忽略（日内抖动）
            4. 首次下调 ≥5% → 触发三级升级
            5. 累计趋势 >10% → 强制触发（日间趋势，防抖不过度）

        Args:
            strategy_id: 策略 ID
            old_budget: 旧 budget 占比
            new_budget: 新 budget 占比
            strategy_type: 策略类型（打板/多因子/事件驱动，convergence_window 用）
            current_date: 当前日期 YYYY-MM-DD（防抖日内/日间判定用），None=用今天

        Returns:
            BudgetChangeResult（含动作描述+更新后状态+待执行指令列表）
        """
        if current_date is None:
            current_date = datetime.now().strftime("%Y-%m-%d")

        # 获取或创建 TierState
        state = self._get_or_create_state(strategy_id, old_budget)

        # ── 规则 1：上调 → 即时返回，不防抖（§3.1 对称性）──
        if new_budget >= old_budget:
            if state.is_in_convergence():
                # 收敛中上调 → re-target（trim_ratio 变小/为负 → 停止强裁）
                return self._retarget_in_convergence(state, new_budget)
            # 非收敛中上调：无动作
            state.target_budget = new_budget
            return BudgetChangeResult(
                action="NO_ACTION: budget 上调或不变，StrategyBook 自然部署",
                state=state,
                instructions=[],
            )

        # ── 下调场景（new < old）──
        change_pct = (old_budget - new_budget) / old_budget if old_budget > 0 else 0.0

        # ── 规则 2：已在收敛中 → re-target 不防抖（§3.3 防抖豁免）──
        if state.is_in_convergence():
            return self._retarget_in_convergence(state, new_budget)

        # ── 日内/日间防抖累计 ──
        if current_date != state.last_budget_change_date:
            # 新交易日 → 重置日内累计
            state.cumulative_budget_change = 0.0
            state.last_budget_change_date = current_date
        state.cumulative_budget_change += change_pct

        # ── 规则 3：首次下调 <5% 且累计 <10% → 防抖忽略 ──
        if change_pct < self.debounce_threshold and state.cumulative_budget_change < self.cumulative_trend_threshold:
            return BudgetChangeResult(
                action=f"DEBOUNCE: budget 下调 {change_pct:.1%} < {self.debounce_threshold:.0%} 阈值，忽略（日内抖动）",
                state=state,
                instructions=[],
            )

        # ── 规则 4/5：触发三级升级（≥5% 或累计趋势 >10%）──
        trigger_reason = (
            f"budget 下调 {change_pct:.1%} ≥ {self.debounce_threshold:.0%} 阈值"
            if change_pct >= self.debounce_threshold
            else f"累计趋势 {state.cumulative_budget_change:.1%} ≥ {self.cumulative_trend_threshold:.0%} 阈值（日间趋势强制触发）"
        )

        return self._trigger_three_tier_escalation(state, old_budget, new_budget, strategy_type, trigger_reason)

    def check_convergence(
        self,
        strategy_id: str,
        current_exposure: float,
        now: datetime | None = None,
    ) -> BudgetChangeResult:
        """检查 Tier 2 是否在 convergence_window 内收敛，否则升级 Tier 3。

        收敛条件（§2.4，同时满足）：
            ① 仓位差收敛：|实际总仓位 - target_budget| / target_budget < ε_pos（5%）
            ② 持续性：连续维持 ε_days 日（1 日）
            ③ 无新违例（调用者保证，本方法不检查）

        Args:
            strategy_id: 策略 ID
            current_exposure: 策略当前实际暴露占比
            now: 当前时间（测试用），None=用 datetime.now()

        Returns:
            BudgetChangeResult（收敛 → CONVERGED；未收敛且超时 → Tier 3 ForcedTrim）
        """
        if now is None:
            now = datetime.now()

        state = self._active_states.get(strategy_id)
        if state is None or not state.is_in_convergence():
            return BudgetChangeResult(
                action="NO_ACTION: 无活跃升级状态",
                state=state or TierState(strategy_id=strategy_id),
                instructions=[],
            )

        # 只在 Tier 2 阶段检查收敛（Tier 1 是瞬时的，Tier 3 已在强裁）
        if state.current_tier != TierLevel.TIER_2_REBALANCE:
            return BudgetChangeResult(
                action=f"NO_ACTION: 当前 Tier={state.current_tier.value}，非 Tier 2",
                state=state,
                instructions=[],
            )

        target = state.target_budget
        if target <= 0:
            # target=0：exposure=0 才算收敛
            is_position_converged = current_exposure <= 0.001
        else:
            is_position_converged = abs(current_exposure - target) / target < self.eps_pos

        # ── 检查收敛 ──
        if is_position_converged:
            state.convergence_days_satisfied += 1
            if state.convergence_days_satisfied >= self.eps_days:
                # 完全收敛
                state.current_tier = TierLevel.CONVERGED
                state.converged_at = now
                return BudgetChangeResult(
                    action=f"CONVERGED: Tier 2 收敛完成（exposure={current_exposure:.4f} ≤ target={target:.4f}+ε）",
                    state=state,
                    instructions=[],
                )
            else:
                # 持续性未达标，继续等待
                return BudgetChangeResult(
                    action=f"WAITING: 仓位已收敛但持续性未达标（{state.convergence_days_satisfied}/{self.eps_days} 日）",
                    state=state,
                    instructions=[],
                )
        else:
            # 仓位未收敛 → 重置持续性计数
            state.convergence_days_satisfied = 0

        # ── 检查是否超时 → 升级 Tier 3 ──
        if state.convergence_window_end and now >= state.convergence_window_end:
            return self._escalate_to_tier3(state, current_exposure, now)
        else:
            # 窗口内但未收敛，继续等待
            return BudgetChangeResult(
                action=f"WAITING: 仓位未收敛（exposure={current_exposure:.4f} vs target={target:.4f}），窗口内继续等待",
                state=state,
                instructions=[],
            )

    def get_state(self, strategy_id: str) -> TierState | None:
        """获取策略的当前 TierState。"""
        return self._active_states.get(strategy_id)

    def on_budget_allocation(
        self,
        effective_budgets: dict[str, float],
        previous_budgets: dict[str, float],
        strategy_types: dict[str, str] | None = None,
        current_date: str | None = None,
    ) -> dict[str, BudgetChangeResult]:
        """G15→G14 接线就绪入口适配（33号 §7 新发现3 登记：BudgetChanged 事件链）。

        RegimeMetaAllocator（G15）只产 BudgetAllocation，本方法是其
        `effective_budgets` → handle_budget_change 的接线就绪适配器：逐策略 diff
        新旧 budget 并走既有防抖+三级升级裁决。生产编排层（G15→G14 集成位）
        确定后直接调用本方法即可，无需再改本模块。

        口径与边界：
          - 入参用纯 dict（非 BudgetAllocation 对象）保持跨域依赖倒置——
            调用方负责解包 BudgetAllocation.effective_budgets；
          - 仅处理新旧两侧都存在的策略；previous 中缺失的视为新策略首配
            （非"budget 变动"，跳过——其渐进暴露由 30号 §6.7 冷启动状态机承载）；
          - new 中缺失的策略**不**自动按 budget→0 强裁（防数据缺口误触 Tier3，
            Fail-Closed 保守方向）；策略下线须显式传 new_budget=0；
          - budget 数值语义 = effective_budget（已含 Shrinkage/冷启动缩放）。

        Args:
            effective_budgets: {strategy_id: 新 budget}（BudgetAllocation.effective_budgets 解包）
            previous_budgets: {strategy_id: 旧 budget}（上一期分配快照）
            strategy_types: {strategy_id: 策略类型}（打板/多因子/事件驱动，窗口查询用）
            current_date: 当前日期 YYYY-MM-DD（防抖日内/日间判定）

        Returns:
            {strategy_id: BudgetChangeResult}（含各策略指令列表，调用方负责执行）
        """
        results: dict[str, BudgetChangeResult] = {}
        types = strategy_types or {}
        for sid, new_budget in effective_budgets.items():
            if sid not in previous_budgets:
                continue  # 新策略首配：非 budget 变动事件（30号 §6.7 冷启动承载渐进暴露）
            results[sid] = self.handle_budget_change(
                strategy_id=sid,
                old_budget=previous_budgets[sid],
                new_budget=new_budget,
                strategy_type=types.get(sid, "多因子"),
                current_date=current_date,
            )
        return results

    def on_firm_violation(
        self,
        strategy_id: str,
        current_exposure: float,
        target_budget: float | None = None,
        violation: str = "firm 风险违例",
        now: datetime | None = None,
    ) -> BudgetChangeResult:
        """firm 违例直触 Tier3 入口（30号 §2.4 Tier3 触发时机② + 33号 §7-③）。

        firm 层（FirmRiskAggregator degraded 五条件 / 风险违例）检出该策略违例时，
        不等 Tier 2 收敛窗口，直接按比例强裁（dumb but safe）。与超时路径共用
        _escalate_to_tier3，reason 如实标记违例来源。

        Args:
            strategy_id: 策略 ID
            current_exposure: 策略当前实际暴露占比
            target_budget: 目标 budget（None=继承活跃状态中的 target；
                无活跃状态且未显式传入 → ValueError）
            violation: 违例描述（如 "单票超限未纠正" / "行业集中度违例"）
            now: 当前时间（测试可注入）

        Returns:
            BudgetChangeResult（Tier3 ForcedTrim 指令；exposure≤target 时 CONVERGED）

        Raises:
            ValueError: target_budget 缺失且无可继承的活跃状态
        """
        if now is None:
            now = datetime.now()

        state = self._active_states.get(strategy_id)
        if target_budget is None:
            if state is None or state.target_budget <= 0:
                raise ValueError(
                    f"on_firm_violation({strategy_id}) 需要 target_budget（无活跃状态可继承，显式传入目标 budget）"
                )
            target_budget = state.target_budget

        if state is None:
            state = self._get_or_create_state(strategy_id, target_budget)
        state.target_budget = target_budget

        reason = f"firm 风险违例直触 Tier3（不等 Tier2 窗口）：{violation}"
        return self._escalate_to_tier3(state, current_exposure, now, override_reason=reason)

    # ══ 内部方法 ══════════════════════════════════════════════════════

    def _get_or_create_state(self, strategy_id: str, current_budget: float) -> TierState:
        """获取或创建 TierState。"""
        if strategy_id not in self._active_states:
            state = TierState(
                strategy_id=strategy_id,
                current_tier=TierLevel.IDLE,
                old_budget=current_budget,
                target_budget=current_budget,
            )
            self._active_states[strategy_id] = state
        return self._active_states[strategy_id]

    def _trigger_three_tier_escalation(
        self,
        state: TierState,
        old_budget: float,
        new_budget: float,
        strategy_type: str,
        trigger_reason: str,
    ) -> BudgetChangeResult:
        """触发三级升级：Tier 1 封锁 → Tier 2 策略自主 → Tier 3 强裁兜底。

        Tier 1 和 Tier 2 立即发出（Tier 1 是瞬时的，Tier 2 紧随其后）。
        Tier 3 仅在 check_convergence 超时时触发。
        """
        state.old_budget = old_budget
        state.target_budget = new_budget
        state.strategy_type = strategy_type  # 记录策略类型（re-target 重置窗口用，修复硬编码"多因子"）
        instructions: list[dict[str, Any]] = []

        # ── Tier 1：封锁新仓（瞬时）──
        state.current_tier = TierLevel.TIER_1_LOCK
        state.tier1_at = datetime.now()
        tier1_instr = self._issue_tier1_freeze(state.strategy_id)
        instructions.append({"tier": 1, "instruction": tier1_instr, "reason": trigger_reason})
        state.instructions_issued.append({"tier": 1, "reason": trigger_reason, "at": state.tier1_at})

        # ── Tier 2：发 rebalance 请求（策略自选砍仓）──
        state.current_tier = TierLevel.TIER_2_REBALANCE
        state.tier2_at = datetime.now()
        convergence_window = self.convergence_windows.get(strategy_type, timedelta(days=3))
        state.convergence_window_end = state.tier2_at + convergence_window
        state.convergence_days_satisfied = 0  # 重置收敛计数

        tier2_instr = self._issue_tier2_rebalance(state.strategy_id, new_budget, convergence_window)
        instructions.append(
            {
                "tier": 2,
                "instruction": tier2_instr,
                "reason": f"窗口 {convergence_window.days} 天，截止 {state.convergence_window_end}",
            }
        )
        state.instructions_issued.append(
            {
                "tier": 2,
                "reason": f"窗口 {convergence_window.days} 天",
                "at": state.tier2_at,
            }
        )

        return BudgetChangeResult(
            action=f"TIER1+TIER2 触发：{trigger_reason}，窗口 {convergence_window.days} 天",
            state=state,
            instructions=instructions,
        )

    def _retarget_in_convergence(self, state: TierState, new_budget: float) -> BudgetChangeResult:
        """收敛中 budget 再变动 → re-target（§3.3 防抖豁免）。

        上调 → trim_ratio 变小/为负 → 停止强裁（若在 Tier 3）。
        下调 → 更新 target_budget，重置收敛窗口。
        """
        old_target = state.target_budget
        state.target_budget = new_budget

        if new_budget >= old_target:
            # 上调：若在 Tier 3，停止强裁
            if state.current_tier == TierLevel.TIER_3_FORCE_TRIM:
                state.current_tier = TierLevel.CONVERGED
                state.converged_at = datetime.now()
                return BudgetChangeResult(
                    action=f"RETARGET: 收敛中上调 {old_target:.4f}→{new_budget:.4f}，停止 Tier 3 强裁",
                    state=state,
                    instructions=[],
                )
            # Tier 2 上调：更新 target，重置收敛窗口
            state.convergence_days_satisfied = 0
            return BudgetChangeResult(
                action=f"RETARGET: 收敛中上调 {old_target:.4f}→{new_budget:.4f}，更新 target 重置收敛计数",
                state=state,
                instructions=[],
            )
        else:
            # 下调：更新 target，按策略自身类型重置收敛窗口（给策略更多时间）
            state.convergence_window_end = datetime.now() + self.convergence_windows.get(
                state.strategy_type, timedelta(days=3)
            )
            state.convergence_days_satisfied = 0
            return BudgetChangeResult(
                action=f"RETARGET: 收敛中下调 {old_target:.4f}→{new_budget:.4f}，更新 target 重置窗口",
                state=state,
                instructions=[],
            )

    def _escalate_to_tier3(
        self,
        state: TierState,
        current_exposure: float,
        now: datetime,
        override_reason: str | None = None,
    ) -> BudgetChangeResult:
        """升级到 Tier 3：按比例强裁兜底（dumb but safe）。

        trim_ratio = (current_exposure - target_budget) / current_exposure
        若 current_exposure=0 则无需裁剪。
        override_reason：非超时路径（如 on_firm_violation 直触）的触发原因覆盖。
        """
        state.current_tier = TierLevel.TIER_3_FORCE_TRIM
        state.tier3_at = now

        if current_exposure <= 0:
            # 无暴露，无需裁剪
            state.current_tier = TierLevel.CONVERGED
            state.converged_at = now
            return BudgetChangeResult(
                action="CONVERGED: 当前暴露=0，无需 Tier 3 强裁",
                state=state,
                instructions=[],
            )

        target = state.target_budget
        if current_exposure <= target:
            # 已收敛（窗口结束时实际已收敛）
            state.current_tier = TierLevel.CONVERGED
            state.converged_at = now
            return BudgetChangeResult(
                action=f"CONVERGED: 窗口结束时已收敛（exposure={current_exposure:.4f} ≤ target={target:.4f}）",
                state=state,
                instructions=[],
            )

        # 计算 trim_ratio：需裁剪的比例
        trim_ratio = (current_exposure - target) / current_exposure
        reason = override_reason or f"Tier 2 超时未收敛（exposure={current_exposure:.4f} vs target={target:.4f}）"

        tier3_instr = self._issue_tier3_force_trim(state.strategy_id, trim_ratio, reason)

        state.instructions_issued.append(
            {
                "tier": 3,
                "reason": reason,
                "at": now,
            }
        )

        return BudgetChangeResult(
            action=f"TIER3 强裁：{reason}，trim_ratio={trim_ratio:.4f}",
            state=state,
            instructions=[{"tier": 3, "instruction": tier3_instr, "reason": reason}],
        )

    # ── 三级指令生成 ──────────────────────────────────────────────────

    def _issue_tier1_freeze(self, strategy_id: str) -> FreezeNewPositions:
        """Tier 1：封锁新仓指令。"""
        return FreezeNewPositions(
            strategy_id=strategy_id,
            cancel_pending_buy_orders=True,
            keep_pending_sell_orders=True,
        )

    def _issue_tier2_rebalance(
        self, strategy_id: str, new_budget: float, convergence_window: timedelta
    ) -> RebalanceRequest:
        """Tier 2：策略自主 rebalance 请求（含 convergence_window）。"""
        return RebalanceRequest(
            strategy_id=strategy_id,
            new_budget=new_budget,
            convergence_window=convergence_window,
        )

    def _issue_tier3_force_trim(self, strategy_id: str, trim_ratio: float, reason: str) -> ForcedTrim:
        """Tier 3：强制按比例裁剪（dumb but safe）。"""
        return ForcedTrim(
            strategy_id=strategy_id,
            trim_ratio=trim_ratio,
            reason=reason,
        )

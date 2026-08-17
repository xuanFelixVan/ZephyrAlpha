# [BLUEPRINT] MOD-PLAN-001 | docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md
# [MODULE] zephyr.plan_engine.tomorrow_boundary_planner
# [DOMAIN] D_PLAN
# [DEPENDENCIES] (待登记)
# [CONSUMERS] MOD-PLAN-002(premarket_constraint_loader); BM-BUY-02(买入融合); BM-SELL-02(卖出融合)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 边界层坏=致命暂停操作; 盘后生成次日边界; 不读盘中实时数据
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BoundaryComputeError(ZA-PLAN-0001)
# [TESTS] tests/plan_engine/test_plan_engine.py
# [A_module] module_id=MOD-PLAN-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


TomorrowBoundaryPlanner — 明日预案引擎 (MOD-PLAN-001)

BM-PLAN-01 明日预案引擎。盘后收盘后基于当日数据冷静计算明日操作边界，
是边界层（B/C）的核心产出者。

核心设计（41 §3.10.2）：
    - 盘后生成 TomorrowBoundary（箱体上沿/下沿、加仓上限、禁加仓价位、必出止盈价位）
    - 边界层坏=致命（暂停操作，延迟开盘到加载成功或人工介入）
    - 推演层坏=可接受（机械执行边界——"边界比聪明更重要"）

不做什么：不做盘中推演（归 BM-PLAN-01-C）/ 不做尾盘决策（归 BM-PLAN-03）/
         不执行下单（归 §3.4 尾盘窗口）

依据: 41_buy_flow §3.10.2 BM-PLAN-01
SSoT: depgraph MOD-PLAN-001
Version: 1.0.0

# [ALGO_FLOW]
# 输入: 市场状态(BM-SEL-03) + 次日8态预测(BM-SEL-04) + 主力行为(BM-SEL-05) + 情绪周期(BM-SEL-23) + 卖出侧边界(BM-SELL-07)
# 特征: 昨日收盘数据, 箱体上沿/下沿, 加仓仓位上限, 禁加仓价位, 必出止盈价位
# 算法: 盘后冷静计算 → 箱体边界 → 操作约束 → 突破验证条件
# 输出: TomorrowBoundary(箱体上沿/下沿/加仓上限/禁加仓价位/必出止盈价位/突破验证条件)

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zephyr.shared.utils.time_utils import now_utc

# ── 常量（41 §3.10.2 参数默认值）──

DEFAULT_MAX_ADD_POSITION = 0.30  # 加仓仓位上限（单标的加仓后总仓位不超过此上限）
BREAKOUT_CONFIRM_CONDITION = "放量站稳10分钟"  # 突破验证条件


class BoundaryComputeError(ValueError):
    """边界计算错误（ZA-PLAN-0001）——边界层坏=致命，调用方暂停操作。

    继承 ValueError 保持向后兼容（调用方/测试按 ValueError 捕获仍生效）。
    """

    error_code = "ZA-PLAN-0001"


# ── 数据契约（41 §3.10.2 输出契约）──


@dataclass(frozen=True)
class TomorrowBoundary:
    """明日操作边界（BM-PLAN-01 产出）。

    盘后收盘后基于当日数据冷静计算的明日操作边界。
    """

    symbol: str
    box_upper: float  # 箱体上沿（明日压力位）
    box_lower: float  # 箱体下沿（明日支撑位）
    max_add_position: float  # 加仓仓位上限（默认 0.30）
    no_add_price: float  # 禁加仓价位（≈上沿，价格接近时禁止加仓防追高）
    must_exit_price: float  # 必出止盈价位（冲上沿必出，纪律）
    breakout_confirm: str  # 突破验证条件（"放量站稳10分钟"）
    computed_at: Any = None  # 计算时间（datetime，由 now_utc() 生成）


# ── 明日预案引擎 ──


class TomorrowBoundaryPlanner:
    """明日预案引擎（MOD-PLAN-001）。

    盘后收盘后基于当日数据冷静计算明日操作边界。
    边界层（B/C）的核心产出者。
    """

    def compute_boundary(
        self,
        symbol: str,
        market_state: dict[str, Any],
        next_day_prediction: dict[str, Any] | None = None,
        main_force_behavior: dict[str, Any] | None = None,
        sentiment_cycle: dict[str, Any] | None = None,
        sell_side_boundary: dict[str, Any] | None = None,
    ) -> TomorrowBoundary:
        """计算明日操作边界。

        Args:
            symbol: 标的代码。
            market_state: 市场状态（BM-SEL-03）。
            next_day_prediction: 次日 8 态预测（BM-SEL-04，暂缓，可为 None）。
            main_force_behavior: 主力行为（BM-SEL-05，可为 None）。
            sentiment_cycle: 情绪周期（BM-SEL-23，可为 None）。
            sell_side_boundary: 卖出侧边界（BM-SELL-07，可为 None）。

        Returns:
            TomorrowBoundary: 明日操作边界。

        Raises:
            BoundaryComputeError: 边界计算失败（致命，暂停操作）。
        """
        # MVP：基于昨日收盘数据计算箱体边界
        # 实际算法待 BM-SEL-03/04/05/23 数据就绪后完善
        # 当前为骨架实现——边界层坏=致命，宁可暂停也不在边界不清时操作

        close_price = market_state.get("close", 0.0)
        if close_price <= 0:
            msg = f"收盘价异常: {close_price}"
            raise BoundaryComputeError(msg)

        # 箱体上沿/下沿：基于昨日收盘价和技术位计算
        # MVP 简化：用昨日振幅的 ±1 倍作为箱体
        amplitude = market_state.get("amplitude", 0.03)  # 默认 3% 振幅
        box_upper = close_price * (1 + amplitude)
        box_lower = close_price * (1 - amplitude)

        return TomorrowBoundary(
            symbol=symbol,
            box_upper=box_upper,
            box_lower=box_lower,
            max_add_position=DEFAULT_MAX_ADD_POSITION,
            no_add_price=box_upper * 0.98,  # 接近上沿时禁止加仓
            must_exit_price=box_upper,  # 冲上沿必出
            breakout_confirm=BREAKOUT_CONFIRM_CONDITION,
            computed_at=now_utc(),
        )

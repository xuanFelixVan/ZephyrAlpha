# [BLUEPRINT] MOD-PLAN-002 | docs/03_modules/_domain_plan_engine/premarket_constraint_loader/blueprint.md
# [MODULE] zephyr.plan_engine.premarket_constraint_loader
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.tomorrow_boundary_planner(TomorrowBoundary)
# [CONSUMERS] MOD-PLAN-003(closing_session_decision); BM-BUY-02(买入融合); BM-SELL-02(卖出融合)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 盘前加载失败=致命(延迟开盘到加载成功或人工介入); 9:25集合竞价匹配9情景; 无约束状态禁止开始交易
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConstraintLoadError(ZA-PLAN-0002)
# [TESTS] tests/plan_engine/test_plan_engine.py
# [A_module] module_id=MOD-PLAN-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


PremarketConstraintLoader — 盘前预案加载 (MOD-PLAN-002)

BM-PLAN-02 盘前预案加载。次日盘前加载昨晚 TomorrowBoundary，
9:25 集合竞价匹配 9 种情景，初始化 ConstraintState。

核心设计（41 §3.10.3）：
    - 9:00 加载边界 → 9:25 竞价匹配情景 → 触发对应分支
    - 盘前加载失败=致命（无约束状态禁止开始交易）
    - 竞价匹配窗口 9:20-9:25（9:20 后不可撤单，价格趋稳）

不做什么：不做盘中推演（归 BM-PLAN-01-C）/ 不做尾盘决策（归 BM-PLAN-03）

依据: 41_buy_flow §3.10.3 BM-PLAN-02
SSoT: depgraph MOD-PLAN-002
Version: 1.0.0

# [ALGO_FLOW]
# 输入: 昨晚 TomorrowBoundary(BM-PLAN-01 产出)
# 特征: 竞价匹配窗口 9:20-9:25, 9 种情景(高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘)
# 算法: 9:00 加载边界 → 9:25 竞价匹配情景 → 初始化 ConstraintState
# 输出: ConstraintState(约束状态, 含 scenario/initialized)

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary

# ── 常量（41 §3.10.3 参数默认值）──

AUCTION_MATCH_WINDOW_START = "09:20"  # 竞价匹配窗口开始
AUCTION_MATCH_WINDOW_END = "09:25"  # 竞价匹配窗口结束

# 9 种情景分类（高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘）
SCENARIO_LIST: Final = [
    "HIGH_OPEN_REAL_UP",  # 高开真涨
    "HIGH_OPEN_FAKE_UP",  # 高开假涨
    "HIGH_OPEN_WASH",  # 高开洗盘
    "LOW_OPEN_REAL_DOWN",  # 低开真跌
    "LOW_OPEN_FAKE_DOWN",  # 低开假跌
    "LOW_OPEN_WASH",  # 低开洗盘
    "FLAT_OPEN_REAL_UP",  # 平开真涨
    "FLAT_OPEN_REAL_DOWN",  # 平开真跌
    "FLAT_OPEN_WASH",  # 平开洗盘
]


# ── 数据契约（41 §3.10.2 输出契约）──


class ConstraintLoadError(ValueError):
    """盘前约束加载错误（ZA-PLAN-0002）——加载失败=致命，禁止开始交易。

    继承 ValueError 保持向后兼容（调用方/测试按 ValueError 捕获仍生效）。
    """

    error_code = "ZA-PLAN-0002"


@dataclass(frozen=True)
class ConstraintState:
    """约束状态（BM-PLAN-02 产出）。

    盘前加载昨晚 TomorrowBoundary + 9:25 竞价匹配情景后的初始化状态。
    """

    symbol: str
    boundary: TomorrowBoundary
    scenario: str  # 盘前竞价匹配的 9 情景之一
    initialized: bool  # 盘前加载是否成功


# ── 盘前预案加载器 ──


class PremarketConstraintLoader:
    """盘前预案加载器（MOD-PLAN-002）。

    次日盘前加载昨晚 TomorrowBoundary，9:25 集合竞价匹配 9 种情景，
    初始化 ConstraintState。加载失败=致命（无约束状态禁止开始交易）。
    """

    def load_constraint(
        self,
        symbol: str,
        boundary: TomorrowBoundary,
        auction_data: dict[str, Any] | None = None,
    ) -> ConstraintState:
        """加载盘前约束状态。

        Args:
            symbol: 标的代码。
            boundary: 昨晚 TomorrowBoundary（BM-PLAN-01 产出）。
            auction_data: 9:25 集合竞价数据（可为 None，MVP 降级）。

        Returns:
            ConstraintState: 约束状态。

        Raises:
            ValueError: 盘前加载失败（致命）。
        """
        if boundary is None:
            msg = f"TomorrowBoundary 未加载: {symbol}"
            raise ConstraintLoadError(msg)

        # 9:25 竞价匹配情景（MVP：无竞价数据时默认平开）
        scenario = self._match_scenario(auction_data) if auction_data else "FLAT_OPEN_WASH"

        return ConstraintState(
            symbol=symbol,
            boundary=boundary,
            scenario=scenario,
            initialized=True,
        )

    def _match_scenario(self, auction_data: dict[str, Any]) -> str:
        """9:25 集合竞价情景匹配。

        Args:
            auction_data: 竞价数据（含 open_price / prev_close / volume 等）。

        Returns:
            str: 匹配的 9 种情景之一。
        """
        open_price = auction_data.get("open_price", 0.0)
        prev_close = auction_data.get("prev_close", 0.0)

        if prev_close <= 0:
            return "FLAT_OPEN_WASH"

        open_pct = (open_price - prev_close) / prev_close

        if open_pct > 0.02:
            return "HIGH_OPEN_REAL_UP"  # MVP 简化，待 G04 校准
        elif open_pct < -0.02:
            return "LOW_OPEN_REAL_DOWN"
        else:
            return "FLAT_OPEN_WASH"

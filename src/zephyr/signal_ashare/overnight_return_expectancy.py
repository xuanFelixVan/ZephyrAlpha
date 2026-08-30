# [BLUEPRINT] MOD-SIG-107 | docs/03_modules/_domain_signal/overnight_return_expectancy/blueprint.md
# [MODULE] zephyr.signal_ashare.overnight_return_expectancy
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（纯函数核，不 import zephyr 内部件）
# [CONSUMERS] （候选：开仓评估装配层，L3+模块29联动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] E = p_up×E涨 − (1−p_up)×E跌；三门槛 E>0.5% ∧ 盈亏比>1.5 ∧ 成本优势>2ATR（cost 注入时）；踏空成本量化不参与门槛；门语义非异常
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01464 行 + 候选注册表 CAND-TESTB-024
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] p_up 越界[0,1]/非有限/E涨E跌<0/开仓价≤0/支撑≤0/ATR≤0/miss_probability越界/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_overnight_return_expectancy.py
# [A_module] module_id=MOD-SIG-107 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
隔夜收益预测与开仓期望值（MOD-SIG-107，B10-01464，模块13）。

决策链第二道经济门槛：E[次日收益]=P涨×E涨−P跌×E跌；E>0.5% 且盈亏比>1.5 且
成本优势>2ATR 才参与。上游概率/密度生产方（MOD-SIG-037/043）鸭子类型注入。

依据: AUD-DRAFT-001 深挖批 B10-01464（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-107
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: overnight_return_expectancy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OvernightReturnExpectancy
#   name_en: OvernightReturnExpectancy
#   intro: 隔夜收益期望值与开仓经济门槛。
#   desc: 隔夜收益期望值与开仓经济门槛。；公共方法（定义序）: evaluate；源码 L127-L177
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: OvernightReturnExpectancy
#   downstream: （候选：开仓评估装配层，L3+模块29联动）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "EntryCostContext",
    "ExpectancyConfig",
    "ExpectancyDecision",
    "OvernightForecast",
    "OvernightReturnExpectancy",
]


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class OvernightForecast:
    p_up: float
    e_up_pct: float
    e_down_pct: float

    def __post_init__(self):
        if not (0.0 <= self.p_up <= 1.0) or not math.isfinite(self.p_up):
            raise ValueError("p_up 必须在 [0,1] 且有限")
        if not math.isfinite(self.e_up_pct) or not math.isfinite(self.e_down_pct):
            raise ValueError("E 涨幅度/跌幅度必须有限")
        if self.e_up_pct < 0 or self.e_down_pct < 0:
            raise ValueError("E 涨幅度/跌幅度不可 <0")


@dataclass(frozen=True)
class EntryCostContext:
    entry_price: float
    support_price: float
    atr14: float

    def __post_init__(self):
        if self.entry_price <= 0 or self.support_price <= 0 or self.atr14 <= 0:
            raise ValueError("entry_price/support_price/atr14 必须 >0")
        for v in (self.entry_price, self.support_price, self.atr14):
            if not math.isfinite(v):
                raise ValueError("成本读数必须有限")


@dataclass(frozen=True)
class ExpectancyConfig:
    expectancy_threshold_pct: float = 0.005
    profit_loss_ratio_threshold: float = 1.5
    cost_advantage_atr_threshold: float = 2.0


@dataclass(frozen=True)
class ExpectancyDecision:
    expectancy_pct: float
    profit_loss_ratio: float | None
    cost_advantage_atr: float | None
    missed_opportunity_cost: float
    passed: bool
    reasons: str
    notes: str = ""


# ------------------------------------------------------------------
# 实现
# ------------------------------------------------------------------
class OvernightReturnExpectancy:
    """隔夜收益期望值与开仓经济门槛。"""

    def __init__(self, config: ExpectancyConfig | None = None) -> None:
        self.config = config or ExpectancyConfig()

    def evaluate(
        self,
        forecast: OvernightForecast,
        cost: EntryCostContext | None = None,
        *,
        miss_probability: float | None = None,
        expected_miss_gain_pct: float | None = None,
    ) -> ExpectancyDecision:
        e_pct = forecast.p_up * forecast.e_up_pct - (1.0 - forecast.p_up) * forecast.e_down_pct
        # 盈亏比
        if forecast.e_down_pct == 0.0:
            pl_ratio = float("inf")
        else:
            pl_ratio = forecast.e_up_pct / forecast.e_down_pct
        # 成本优势
        cost_adv = None
        if cost is not None:
            cost_adv = (cost.entry_price - cost.support_price) / cost.atr14
        # 踏空成本
        missed = 0.0
        if miss_probability is not None and expected_miss_gain_pct is not None:
            if not (0.0 <= miss_probability <= 1.0) or not math.isfinite(miss_probability):
                raise ValueError("miss_probability 必须在 [0,1] 且有限")
            missed = miss_probability * expected_miss_gain_pct
        # 门槛判定
        reasons: list[str] = []
        notes: list[str] = []
        if e_pct < self.config.expectancy_threshold_pct:
            reasons.append(f"expectancy={e_pct:.4f}<threshold={self.config.expectancy_threshold_pct}")
        if pl_ratio is not None and pl_ratio < self.config.profit_loss_ratio_threshold:
            reasons.append(f"profit_loss={pl_ratio:.2f}<threshold={self.config.profit_loss_ratio_threshold}")
        if cost is None:
            notes.append("cost_skipped")
        elif cost_adv is not None and cost_adv < self.config.cost_advantage_atr_threshold:
            reasons.append(f"cost_advantage={cost_adv:.2f}<threshold={self.config.cost_advantage_atr_threshold}")
        passed = len(reasons) == 0
        return ExpectancyDecision(
            expectancy_pct=e_pct,
            profit_loss_ratio=pl_ratio,
            cost_advantage_atr=cost_adv,
            missed_opportunity_cost=missed,
            passed=passed,
            reasons="; ".join(reasons) if reasons else "ok",
            notes="; ".join(notes) if notes else "",
        )

# [BLUEPRINT] MOD-XS-008 | docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md
# [MODULE] zephyr.ex_sor.core.rl_exec_contract
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.backtest.core.matching_logic ; stdlib
# [CONSUMERS] zephyr.ex_sor.core.rl_exec_boundary ; zephyr.ex_sor.core.rl_exec_env
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] frozen 契约实例化后不可变; 训练与生产执行共用同一份约束口径; price_limit_pct/lot_size 默认复用 MatchingConfig 撮合口径
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_sor/test_rl_exec_env.py
# [A_module] module_id=MOD-XS-008 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


RL Execution Contract — RL 执行参数契约 (MOD-XS-008, P-4 裁定组件)

D-EX-SOR §2.1 XS-08: RL Execution Training Env 的参数契约层。

职责:
    - 以 frozen dataclass 定义 RL 执行环境的全部硬约束参数
      （涨跌停限价带 / POV 上限 / 切片数 / 禁市价标志 / 价格偏移档位表）
    - 供未来真训练（B-007 闸门）与生产执行两侧共用，保证训练约束=生产约束
    - 本骨架不含任何训练逻辑（真训练属宪章 B-007 人工审批闸门，仅留痕）

口径:
    - price_limit_pct / lot_size 默认复用 backtest MatchingConfig 撮合口径
      （2026-08-21 #233 裁定费率口径统一的同一真源），禁止另立常量
    - 限价基准 = 盘口中间价 mid=(ask1+bid1)/2，限价 = mid×(1+offset)
    - 实现短缺基准 = arrival_price（母单决策价）

SSoT: depgraph MOD-XS-008
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 母单与硬约束参数
#   fields: symbol/side/total_quantity/slice_count/pov_limit/forbid_market/offset_levels/prev_close/arrival_price
#   code: RlExecContract L61
# 层: 算法
# - id: A1
#   name_zh: ① 冻结契约载体
#   name_en: frozen_dataclass
#   intro: 纯值对象无行为，字段即契约；默认值复用 MatchingConfig 撮合口径
#   desc: frozen=True 实例化后不可变；price_limit_pct=0.10/lot_size=100 取自 MatchingConfig 默认
#   inputs: I1
#   outputs: 不可变契约实例
#   invariant: frozen 契约实例化后不可变
# 层: 输出
# - id: O1
#   name_zh: 执行约束契约
#   name_en: RlExecContract
#   intro: 被硬边界层（裁剪/拒绝判定）与环境（回合推进）共同消费
#   downstream: zephyr.ex_sor.core.rl_exec_boundary ; zephyr.ex_sor.core.rl_exec_env
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from zephyr.backtest.core.matching_logic import MatchingConfig

__all__: list[str] = ["RlExecContract"]

# 撮合口径默认真源（涨跌停幅度/整手数与回测=实盘一致性口径同源，禁另立常量）
_MATCHING_DEFAULTS = MatchingConfig()


@dataclass(frozen=True)
class RlExecContract:
    """RL 执行参数契约（frozen，训练与生产执行共用）。

    Attributes:
        symbol: 标的代码（板块识别依赖，如 600000.SH）
        side: 母单方向 "BUY" | "SELL"
        total_quantity: 母单总量（股）
        slice_count: 切片数（= 回合最大步数）
        pov_limit: POV 上限（0,1]，单步数量 ≤ pov_limit × 对方五档盘口总量
        forbid_market: 禁市价标志；True 时市价类动作被硬边界拒绝（本步不成交）
        offset_levels: 价格偏移档位表（小数，如 Decimal("-0.02")），动作按索引引用
        prev_close: 前收盘价（涨跌停带基准）
        arrival_price: 母单决策价（实现短缺 IS 基准）
        price_limit_pct: 涨跌停幅度（默认 0.10，复用 MatchingConfig 口径；ST 股可调 0.05）
        lot_size: 整手数（默认 100，复用 MatchingConfig 口径；科创板 200 由板块规则细化）
    """

    symbol: str
    side: str
    total_quantity: Decimal
    slice_count: int
    pov_limit: Decimal
    forbid_market: bool
    offset_levels: tuple[Decimal, ...]
    prev_close: Decimal
    arrival_price: Decimal
    price_limit_pct: Decimal = _MATCHING_DEFAULTS.price_limit_pct
    lot_size: int = _MATCHING_DEFAULTS.lot_size

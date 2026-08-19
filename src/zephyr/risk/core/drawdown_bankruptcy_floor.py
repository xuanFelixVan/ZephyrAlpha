# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §4.10/§6.15
# [MODULE] zephyr.risk.core.drawdown_bankruptcy_floor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] RiskOrchestrator(§6.5 接线位); §3.5 Kill Switch 触发条件表第5类触发源(取最严OR)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] static模式底线=初始本金×0.85(§4.10部分采纳,PropGuard TradeShield双模式之static腿); nav<底线→触发(绝对破产防护,与trailing 25% peak口径正交——大幅盈利后trailing远高于本金时static仍守初始本金); nav==底线不触发(严格小于); initial_capital≤0或floor_ratio越界或nav<0抛错
# [MODIFY-GUARD] tests/risk/test_drawdown_bankruptcy_floor.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidBankruptcyFloorInputError(ZA-RK-0067)
# [TESTS] tests/risk/test_drawdown_bankruptcy_floor.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: current_nav当前净值 + initial_capital初始本金 + BankruptcyFloorConfig(floor_ratio=0.85)
# F1: check_bankruptcy_floor(floor=initial×0.85; nav<floor→Breach(含breach_pct=距底线深度); 否则None)
# O1: BankruptcyFloorBreach(floor+breach_pct+reason)或None → Kill Switch 第5类触发源(§3.5表新增行)
# [/ALGO_FLOW]
"""D_RISK — Static 模式破产底线 Kill Switch 触发源（35 号 memo §6.15 施工，§4.10 部分采纳）。

痛点（§6.15 P1）：trailing 25% Kill Switch 锚定 peak NAV——大幅盈利后
底线仍远高于初始本金（如本金 100w 盈利到 300w，trailing 底线 225w，
亏回 225w 才触发，本金已亏 -55% 仍无"绝对破产防护"）。§4.10 裁定
部分采纳 TradeShield 双模式之 static 腿：初始本金 × 0.85 作为第五类
Kill Switch 触发源（§3.5 触发条件表新增"组合净值 < 初始本金 × 0.85"行）。

本模块落地（函数级）：
  - check_bankruptcy_floor：nav < initial_capital × floor_ratio（默认 0.85）
    → BankruptcyFloorBreach（含 breach_pct=相对底线的击穿深度）；否则 None。
  - 与 trailing 口径正交互补：trailing 守 peak（浮盈回撤），static 守本金
    （绝对破产）；两源 OR 取最严（§3.5 多源触发原则）。
  - 触发语义=Kill Switch 建议（调用方接 trigger_kill_switch），本函数
    只判定不发单（对齐 stop_loss 单向交接）。

SSoT: 35_drawdown_protocol_impl §4.10（部分采纳）+ §6.15
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidBankruptcyFloorInputError",
    "BankruptcyFloorConfig",
    "BankruptcyFloorBreach",
    "check_bankruptcy_floor",
]

_logger = logging.getLogger(__name__)


class InvalidBankruptcyFloorInputError(ZephyrBaseError):
    """破产底线检测输入非法（本金非正/比例越界/净值非法）。"""

    error_code = "ZA-RK-0067"


@dataclass(frozen=True)
class BankruptcyFloorConfig:
    """破产底线配置（C 类可调参数，默认值真源=§4.10 static 模式）。

    Attributes:
        floor_ratio: 底线比例（默认 0.85=初始本金 × 0.85）
    """

    floor_ratio: float = 0.85

    def __post_init__(self) -> None:
        if not 0 < self.floor_ratio < 1:
            raise InvalidBankruptcyFloorInputError(
                f"floor_ratio 须在 (0,1), got {self.floor_ratio}"
            )


@dataclass(frozen=True)
class BankruptcyFloorBreach:
    """破产底线击穿结果（Kill Switch 第五类触发源）。

    Attributes:
        current_nav: 当前净值
        initial_capital: 初始本金
        floor: 底线值（initial_capital × floor_ratio）
        breach_pct: 击穿深度 = (floor - nav) / floor（正数，越大越深）
        reason: 人类可读说明
    """

    current_nav: float
    initial_capital: float
    floor: float
    breach_pct: float
    reason: str


def check_bankruptcy_floor(
    current_nav: float,
    initial_capital: float,
    config: BankruptcyFloorConfig | None = None,
) -> BankruptcyFloorBreach | None:
    """Static 破产底线检测：nav < 初始本金 × 0.85 → 击穿（Kill Switch 触发源）。

    Args:
        current_nav: 当前组合净值（须 >= 0；NaN/Inf 拒绝）
        initial_capital: 初始本金（须 > 0，static 锚）
        config: 底线配置（None=默认 0.85）

    Returns:
        BankruptcyFloorBreach（击穿）；未击穿 None
    """
    if initial_capital <= 0 or math.isnan(initial_capital) or math.isinf(initial_capital):
        raise InvalidBankruptcyFloorInputError(
            f"initial_capital 须为正, got {initial_capital}"
        )
    if current_nav < 0 or math.isnan(current_nav) or math.isinf(current_nav):
        raise InvalidBankruptcyFloorInputError(
            f"current_nav 须 >= 0, got {current_nav}"
        )
    cfg = config or BankruptcyFloorConfig()
    floor = initial_capital * cfg.floor_ratio
    if current_nav >= floor:
        return None
    breach_pct = (floor - current_nav) / floor
    reason = (
        f"组合净值 {current_nav:.2f} < 破产底线 {floor:.2f}"
        f"（初始本金 {initial_capital:.2f} × {cfg.floor_ratio:.0%}），"
        f"击穿深度 {breach_pct:.1%}，建议 Kill Switch（§3.5 第五类触发源）"
    )
    _logger.critical(
        "BANKRUPTCY_FLOOR_BREACH nav=%.2f floor=%.2f breach=%.3f",
        current_nav, floor, breach_pct,
    )
    return BankruptcyFloorBreach(
        current_nav=current_nav,
        initial_capital=initial_capital,
        floor=floor,
        breach_pct=breach_pct,
        reason=reason,
    )

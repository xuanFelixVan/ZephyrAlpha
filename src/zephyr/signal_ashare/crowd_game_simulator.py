# [BLUEPRINT] MOD-SIG-114 | docs/03_modules/_domain_signal/crowd_game_simulator/blueprint.md
# [MODULE] zephyr.signal_ashare.crowd_game_simulator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；行为先验参数/时钟全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四类玩家词表闭合（北向/公募/游资/散户）；先验参数全注入；合力方向∈[-1,1]；分歧度（方向熵）∈[0,1]；盘后运行语义标注；输出 inference=True 推断性质仅作信号输入；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/crowd_game_simulator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CrowdGameError(占位 ZA-SIG-UNREGISTERED-CROWD-GAME)——非法玩家类型/先验缺项或重复/权重非正/方向先验越界/盘后语义缺失时抛
# [TESTS] tests/signal_ashare/test_crowd_game_simulator.py
# [A_module] module_id=MOD-SIG-114 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
CrowdGameSimulator — 群体博弈模拟器（MOD-SIG-114，B1-00169，C2 C-036）。

轻量博弈推演：四类玩家（北向/公募/游资/散户词表闭合）行为规则库
（历史统计先验参数注入）+ 合力方向（加权净方向）/分歧度（方向熵）输出
+ 盘后运行语义 + 输出标注推断性质仅作信号输入。
ABM思想规则库版。

纯内存/DI设计；外部副作用全部经注入回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: priors 参数
#   fields: 参数 priors（无注解）
#   code: crowd_game_simulator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: crowd_game_simulator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CrowdGameSimulator
#   name_en: CrowdGameSimulator
#   intro: 群体博弈模拟器（规则库+加权净方向+方向熵）。
#   desc: 群体博弈模拟器（规则库+加权净方向+方向熵）。；公共方法（定义序）: simulate；源码 L167-L268
#   inputs: priors clock
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: CrowdGameSimulator
#   downstream: 运行时装配批（统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CrowdGameError",
    "CrowdGameResult",
    "CrowdGameSimulator",
    "PlayerPrior",
    "PlayerType",
    "PostCloseSemantics",
]


class CrowdGameError(Exception):
    """群体博弈协议输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-CROWD-GAME。
    """


class PlayerType(str, Enum):
    """四类玩家词表（闭合）。"""

    NORTHBOUND = "北向"
    PUBLIC_FUND = "公募"
    HOT_MONEY = "游资"
    RETAIL = "散户"


@dataclass(frozen=True)
class PlayerPrior:
    """玩家行为先验参数（历史统计注入）。"""

    player_type: PlayerType
    weight: float  # 合力方向加权权重，>0
    momentum_bias: float  # 动量倾向先验，∈[-1,1]
    sentiment_sensitivity: float  # 情绪敏感度，∈[0,1]

    def __post_init__(self) -> None:
        if not isinstance(self.player_type, PlayerType):
            raise CrowdGameError(f"非法玩家类型: {self.player_type!r}")
        if self.weight <= 0:
            raise CrowdGameError(f"weight 须>0: {self.weight!r}")
        if not -1.0 <= self.momentum_bias <= 1.0:
            raise CrowdGameError(f"momentum_bias 越界: {self.momentum_bias!r}")
        if not 0.0 <= self.sentiment_sensitivity <= 1.0:
            raise CrowdGameError(f"sentiment_sensitivity 越界: {self.sentiment_sensitivity!r}")


@dataclass(frozen=True)
class PostCloseSemantics:
    """盘后运行语义标注。"""

    is_post_close: bool = True
    data_as_of: str = "close"  # close | auction | intraday


@dataclass(frozen=True)
class CrowdGameResult:
    """群体博弈推演结果。"""

    timestamp: datetime.datetime
    net_direction: float  # 加权净方向，∈[-1,1]
    direction_entropy: float  # 分歧度（方向熵），∈[0,1]
    player_votes: tuple[tuple[PlayerType, float], ...]  # (玩家, 方向∈[-1,1])
    post_close: PostCloseSemantics
    inference: bool = True
    notes: tuple[str, ...] = ()


#: 默认四类玩家先验（MVP初拍值，可被注入覆盖）
_DEFAULT_PRIORS: Final[dict[PlayerType, PlayerPrior]] = {
    PlayerType.NORTHBOUND: PlayerPrior(
        player_type=PlayerType.NORTHBOUND,
        weight=0.30,
        momentum_bias=0.2,
        sentiment_sensitivity=0.3,
    ),
    PlayerType.PUBLIC_FUND: PlayerPrior(
        player_type=PlayerType.PUBLIC_FUND,
        weight=0.25,
        momentum_bias=0.1,
        sentiment_sensitivity=0.2,
    ),
    PlayerType.HOT_MONEY: PlayerPrior(
        player_type=PlayerType.HOT_MONEY,
        weight=0.25,
        momentum_bias=0.5,
        sentiment_sensitivity=0.8,
    ),
    PlayerType.RETAIL: PlayerPrior(
        player_type=PlayerType.RETAIL,
        weight=0.20,
        momentum_bias=-0.1,
        sentiment_sensitivity=0.9,
    ),
}


class CrowdGameSimulator:
    """群体博弈模拟器（规则库+加权净方向+方向熵）。"""

    def __init__(
        self,
        *,
        priors: Mapping[PlayerType, PlayerPrior] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._priors = dict(priors) if priors is not None else dict(_DEFAULT_PRIORS)
        # 四类玩家必须齐
        missing = set(PlayerType) - set(self._priors)
        if missing:
            raise CrowdGameError(f"先验缺项: {[m.value for m in sorted(missing, key=lambda x: x.value)]}")
        for p in self._priors.values():
            if not isinstance(p, PlayerPrior):
                raise CrowdGameError("priors 含非法条目（非 PlayerPrior）")
        self._clock = clock or datetime.datetime.now

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _now(self) -> datetime.datetime:
        return self._clock()

    # ── 玩家行为规则库 ──────────────────────────────────────────────────────

    def _vote(
        self,
        prior: PlayerPrior,
        *,
        market_momentum: float,
        sentiment_index: float,
    ) -> float:
        """单玩家投票方向∈[-1,1]（规则：动量先验+情绪敏感度×情绪偏离）。"""
        if not -1.0 <= market_momentum <= 1.0:
            raise CrowdGameError(f"market_momentum 越界: {market_momentum!r}")
        if not -1.0 <= sentiment_index <= 1.0:
            raise CrowdGameError(f"sentiment_index 越界: {sentiment_index!r}")
        raw = (
            prior.momentum_bias
            + market_momentum * (1.0 - prior.sentiment_sensitivity)
            + sentiment_index * prior.sentiment_sensitivity
        )
        # 限制在 [-1,1]
        return max(-1.0, min(1.0, raw))

    # ── 合力方向与分歧度 ──────────────────────────────────────────────────

    def simulate(
        self,
        *,
        market_momentum: float,
        sentiment_index: float,
        post_close: bool = True,
        data_as_of: str = "close",
    ) -> CrowdGameResult:
        """博弈推演主入口：四类玩家投票→加权净方向+方向熵。"""
        ts = self._now()
        semantics = PostCloseSemantics(is_post_close=post_close, data_as_of=data_as_of)

        votes: list[tuple[PlayerType, float]] = []
        for pt in sorted(PlayerType, key=lambda x: x.value):
            prior = self._priors[pt]
            v = self._vote(prior, market_momentum=market_momentum, sentiment_index=sentiment_index)
            votes.append((pt, round(v, 6)))

        # 加权净方向
        total_w = sum(self._priors[pt].weight for pt, _ in votes)
        net = sum(self._priors[pt].weight * v for pt, v in votes) / total_w if total_w > 0 else 0.0
        net = max(-1.0, min(1.0, net))

        # 方向熵：将 [-1,1] 划分为 10 桶，计算投票分布熵并归一化到 [0,1]
        entropy = self._direction_entropy([v for _, v in votes])

        return CrowdGameResult(
            timestamp=ts,
            net_direction=round(net, 6),
            direction_entropy=entropy,
            player_votes=tuple(votes),
            post_close=semantics,
            inference=True,
            notes=("推断性质，仅作信号输入",),
        )

    @staticmethod
    def _direction_entropy(votes: Sequence[float], buckets: int = 10) -> float:
        """方向熵（归一化到[0,1]）。"""
        if not votes:
            return 0.0
        counts = [0] * buckets
        for v in votes:
            idx = int((v + 1.0) / 2.0 * buckets)
            idx = max(0, min(buckets - 1, idx))
            counts[idx] += 1
        total = len(votes)
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        max_entropy = math.log2(min(buckets, total)) if total > 1 else 1.0
        return round(entropy / max_entropy if max_entropy > 0 else 0.0, 6)

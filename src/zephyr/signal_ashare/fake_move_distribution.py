# [BLUEPRINT] MOD-SIG-124 | docs/03_modules/_domain_signal/fake_move_distribution/blueprint.md
# [MODULE] zephyr.signal_ashare.fake_move_distribution
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（规则库/打分核纯内存；clock/warning_sink/7维信号数据全注入）
# [CONSUMERS] 运行时装配批（追涨门禁 / 买入侧防伪告警接 alert 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 假动作6模式词表闭合(假拉升真出货|假突破真派发|假吸筹真对倒|假洗盘真出货|假护盘真诱多|假反弹真派发); 7维信号词表闭合且全部注入数据; 维度嫌疑分∈[0,1]; 加权概率∈[0,1]; 概率>warn_threshold(0.85) 输出 FakeMoveWarning 暂停追涨; 告警不阻断; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/fake_move_distribution/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FakeMoveError(占位 ZA-SIG-UNREGISTERED-FAKE-MOVE)——空symbol/信号取值越界或非有限/未知拉升时段/权重或阈值配置非法时抛
# [TESTS] tests/signal_ashare/test_fake_move_distribution.py
# [A_module] module_id=MOD-SIG-124 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
FakeMoveDetector — 主力假动作与筹码派发识别（MOD-SIG-124）。

B10-01425（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-044，A1 模块27；
canonical 承接 TESTB-056 归并）：**假动作 6 模式规则库**（假拉升真出货/
假突破真派发/假吸筹真对倒/假洗盘真出货/假护盘真诱多/假反弹真派发，
词表闭合，各含表面行为+底层矛盾信号）+ **7 维信号打分**（主动买入占比/
大单净流入/量能持续/板块跟涨率/拉升时段/底部筹码/龙虎榜，全部注入数
据）+ **>85% 暂停追涨**输出 FakeMoveWarning。

查重分工（蓝图 §0）：false_breakout_trap_detector（MOD-SIG-100）=单次突
破 N 日回落判假+诱多三特征（本件=多模式假动作规则库+7维资金/筹码面打
分，零交集）；trading_compliance_detector=合规检测（本件为信号域行为
识别，不做合规判定）；识别结论仅作信号输入，不直接下单（advisory）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: fake_move_distribution.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: warning_sink 参数
#   fields: 参数 warning_sink（无注解）
#   code: fake_move_distribution.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: fake_move_distribution.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FakeMoveDetector
#   name_en: FakeMoveDetector
#   intro: 主力假动作识别器（6 模式规则库 + 7 维打分 + >85% 暂停追涨）。
#   desc: 主力假动作识别器（6 模式规则库 + 7 维打分 + >85% 暂停追涨）。；公共方法（定义序）: assess；源码 L320-L399
#   inputs: clock warning_sink config
#   outputs: 返回值
#   （注：A1 之后另有 9 个公共定义未列入（含 9 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: FakeMoveDetector
#   downstream: 运行时装配批（追涨门禁 / 买入侧防伪告警接 alert 路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "FAKE_MOVE_RULES",
    "FakeMoveAssessment",
    "FakeMoveConfig",
    "FakeMoveDetector",
    "FakeMoveError",
    "FakeMovePattern",
    "FakeMoveRule",
    "FakeMoveWarning",
    "PumpWindow",
    "SignalDim",
    "SignalMetrics",
]


class FakeMoveError(Exception):
    """假动作识别输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-FAKE-MOVE。
    """


class FakeMovePattern(str, Enum):
    """主力假动作 6 模式（词表闭合）。"""

    FAKE_PUMP_REAL_DUMP = "fake_pump_real_dump"  # 假拉升真出货
    FAKE_BREAKOUT_REAL_DISTRIBUTION = "fake_breakout_real_distribution"  # 假突破真派发
    FAKE_ACCUMULATION_REAL_COLLUSION = "fake_accumulation_real_collusion"  # 假吸筹真对倒
    FAKE_WASH_REAL_DUMP = "fake_wash_real_dump"  # 假洗盘真出货
    FAKE_SUPPORT_REAL_TRAP = "fake_support_real_trap"  # 假护盘真诱多
    FAKE_REBOUND_REAL_DISTRIBUTION = "fake_rebound_real_distribution"  # 假反弹真派发


class SignalDim(str, Enum):
    """7 维信号维度（词表闭合，全部注入数据）。"""

    ACTIVE_BUY = "active_buy"  # 主动买入占比
    BIG_ORDER_INFLOW = "big_order_inflow"  # 大单净流入
    VOLUME_PERSISTENCE = "volume_persistence"  # 量能持续
    SECTOR_FOLLOW = "sector_follow"  # 板块跟涨率
    PUMP_WINDOW = "pump_window"  # 拉升时段
    BOTTOM_CHIP = "bottom_chip"  # 底部筹码
    LHB = "lhb"  # 龙虎榜


class PumpWindow(str, Enum):
    """拉升时段（词表闭合）。"""

    MORNING = "morning"  # 早盘
    MIDDAY = "midday"  # 盘中
    TAIL = "tail"  # 尾盘


#: 维度打分顺序（词表定义序，确定性）
_DIM_ORDER: Final = tuple(SignalDim)

#: 等权默认（7 维均权）
_EQUAL_WEIGHTS: Final = tuple(1.0 / 7.0 for _ in range(7))

#: 拉升时段嫌疑静态表（尾盘偷袭最可疑；封闭表可审计）
_WINDOW_SUSPICION: Final = {
    PumpWindow.MORNING: 0.2,
    PumpWindow.MIDDAY: 0.4,
    PumpWindow.TAIL: 1.0,
}


@dataclass(frozen=True)
class FakeMoveRule:
    """假动作规则：表面行为 + 底层矛盾信号（命中=矛盾维度嫌疑全部成立）。"""

    pattern: FakeMovePattern
    surface_behavior: str
    contradiction_signals: tuple[str, ...]
    contradiction_dims: tuple[SignalDim, ...]


#: 假动作 6 模式规则库（词表闭合，各含表面行为+底层矛盾信号）
FAKE_MOVE_RULES: Final[dict[FakeMovePattern, FakeMoveRule]] = {
    FakeMovePattern.FAKE_PUMP_REAL_DUMP: FakeMoveRule(
        pattern=FakeMovePattern.FAKE_PUMP_REAL_DUMP,
        surface_behavior="盘中快速拉升造势，涨幅亮眼引跟风盘",
        contradiction_signals=("主动买入占比低迷", "大单资金净流出", "拉升量能无法持续"),
        contradiction_dims=(
            SignalDim.ACTIVE_BUY,
            SignalDim.BIG_ORDER_INFLOW,
            SignalDim.VOLUME_PERSISTENCE,
        ),
    ),
    FakeMovePattern.FAKE_BREAKOUT_REAL_DISTRIBUTION: FakeMoveRule(
        pattern=FakeMovePattern.FAKE_BREAKOUT_REAL_DISTRIBUTION,
        surface_behavior="放量突破关键压力位，形态看似转强",
        contradiction_signals=("突破后量能迅速萎缩", "底部筹码松动上移", "板块不跟涨"),
        contradiction_dims=(
            SignalDim.VOLUME_PERSISTENCE,
            SignalDim.BOTTOM_CHIP,
            SignalDim.SECTOR_FOLLOW,
        ),
    ),
    FakeMovePattern.FAKE_ACCUMULATION_REAL_COLLUSION: FakeMoveRule(
        pattern=FakeMovePattern.FAKE_ACCUMULATION_REAL_COLLUSION,
        surface_behavior="低位横盘小阳堆积，疑似主力吸筹",
        contradiction_signals=("大单净流入为零/负", "龙虎榜席位对倒净卖出", "对倒放量量能无法持续"),
        contradiction_dims=(
            SignalDim.BIG_ORDER_INFLOW,
            SignalDim.LHB,
            SignalDim.VOLUME_PERSISTENCE,
        ),
    ),
    FakeMovePattern.FAKE_WASH_REAL_DUMP: FakeMoveRule(
        pattern=FakeMovePattern.FAKE_WASH_REAL_DUMP,
        surface_behavior="急跌破位疑似洗盘，制造恐慌吸筹假象",
        contradiction_signals=("下跌中大单持续净流出", "底部筹码峰消失", "板块未同步走弱"),
        contradiction_dims=(
            SignalDim.BIG_ORDER_INFLOW,
            SignalDim.BOTTOM_CHIP,
            SignalDim.SECTOR_FOLLOW,
        ),
    ),
    FakeMovePattern.FAKE_SUPPORT_REAL_TRAP: FakeMoveRule(
        pattern=FakeMovePattern.FAKE_SUPPORT_REAL_TRAP,
        surface_behavior="关键价位护盘拉升，营造有主力托底假象",
        contradiction_signals=("护盘仅靠尾盘偷袭", "主动买入占比低跟风不足", "龙虎榜净卖出"),
        contradiction_dims=(
            SignalDim.PUMP_WINDOW,
            SignalDim.ACTIVE_BUY,
            SignalDim.LHB,
        ),
    ),
    FakeMovePattern.FAKE_REBOUND_REAL_DISTRIBUTION: FakeMoveRule(
        pattern=FakeMovePattern.FAKE_REBOUND_REAL_DISTRIBUTION,
        surface_behavior="超跌反弹放量上攻，看似反转启动",
        contradiction_signals=("反弹量能不持续", "板块跟涨率低", "大单借反弹净流出"),
        contradiction_dims=(
            SignalDim.VOLUME_PERSISTENCE,
            SignalDim.SECTOR_FOLLOW,
            SignalDim.BIG_ORDER_INFLOW,
        ),
    ),
}


@dataclass(frozen=True)
class SignalMetrics:
    """7 维信号注入数据（盘后快照；比率∈[0,1]，金额为元）。"""

    active_buy_ratio: float  # 主动买入占比 [0,1]
    big_order_net_inflow: float  # 大单净流入（元，负=净流出）
    volume_persistence: float  # 量能持续度 [0,1]
    sector_follow_rate: float  # 板块跟涨率 [0,1]
    pump_window: PumpWindow  # 拉升时段
    bottom_chip_ratio: float  # 底部筹码占比 [0,1]
    lhb_net_buy: float  # 龙虎榜净买入（元，负=净卖出）


@dataclass(frozen=True)
class FakeMoveConfig:
    """假动作打分配置（构造即校验，Fail-Closed）。

    Attributes:
        weights: 7 维权重（None=等权；提供则须 7 项非负、Σ≈1）
        active_buy_mid: 主动买入占比中位阈值（低于→嫌疑线性升）
        big_order_scale: 大单净流出归一化刻度（元）
        lhb_scale: 龙虎榜净卖出归一化刻度（元）
        pattern_match_threshold: 矛盾维度嫌疑分≥阈值→该维矛盾成立
        warn_threshold: 假动作概率>阈值→FakeMoveWarning 暂停追涨
    """

    weights: tuple[float, ...] | None = None
    active_buy_mid: float = 0.5
    big_order_scale: float = 1e8
    lhb_scale: float = 5e7
    pattern_match_threshold: float = 0.5
    warn_threshold: float = 0.85

    def __post_init__(self) -> None:
        if self.weights is not None:
            if len(self.weights) != len(_DIM_ORDER):
                raise FakeMoveError(f"weights 须 {len(_DIM_ORDER)} 项（7维），实得 {len(self.weights)}")
            for w in self.weights:
                if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w) or w < 0.0:
                    raise FakeMoveError(f"weights 含非法权重: {w!r}（须非负有限）")
            if abs(sum(self.weights) - 1.0) > 1e-6:
                raise FakeMoveError(f"weights Σ≠1: {sum(self.weights)!r}")
        if not 0.0 < self.active_buy_mid < 1.0:
            raise FakeMoveError(f"active_buy_mid 越界: {self.active_buy_mid!r}")
        if self.big_order_scale <= 0.0:
            raise FakeMoveError(f"big_order_scale 须>0: {self.big_order_scale!r}")
        if self.lhb_scale <= 0.0:
            raise FakeMoveError(f"lhb_scale 须>0: {self.lhb_scale!r}")
        if not 0.0 < self.pattern_match_threshold <= 1.0:
            raise FakeMoveError(f"pattern_match_threshold 越界: {self.pattern_match_threshold!r}")
        if not 0.0 < self.warn_threshold < 1.0:
            raise FakeMoveError(f"warn_threshold 越界: {self.warn_threshold!r}")


@dataclass(frozen=True)
class FakeMoveWarning:
    """>85% 暂停追涨告警载荷（action=suspend_chase）。"""

    symbol: str
    fake_percent: float
    matched_patterns: tuple[FakeMovePattern, ...]
    action: str  # "suspend_chase" 暂停追涨
    raised_at: datetime.datetime


@dataclass(frozen=True)
class FakeMoveAssessment:
    """假动作评估输出（概率 + 维度分明细 + 模式命中 + 告警）。"""

    symbol: str
    fake_probability: float  # [0,1]
    fake_percent: float  # 0-100
    dim_scores: dict[SignalDim, float] = field(default_factory=dict)
    matched_patterns: tuple[FakeMovePattern, ...] = ()
    warning: FakeMoveWarning | None = None
    assessed_at: datetime.datetime | None = None


def _clamp01(x: float) -> float:
    """[0,1] 截断。"""
    return max(0.0, min(1.0, x))


def _validate_metrics(m: SignalMetrics) -> None:
    """7 维注入数据校验（比率∈[0,1]、金额有限、时段词表闭合）。"""
    for name in ("active_buy_ratio", "volume_persistence", "sector_follow_rate", "bottom_chip_ratio"):
        v = getattr(m, name)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0.0 <= v <= 1.0:
            raise FakeMoveError(f"{name} 越界: {v!r}（须∈[0,1] 有限实数）")
    for name in ("big_order_net_inflow", "lhb_net_buy"):
        v = getattr(m, name)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise FakeMoveError(f"{name} 非法: {v!r}（须有限实数）")
    if not isinstance(m.pump_window, PumpWindow):
        raise FakeMoveError(f"未知拉升时段: {m.pump_window!r}（词表闭合）")


class FakeMoveDetector:
    """主力假动作识别器（6 模式规则库 + 7 维打分 + >85% 暂停追涨）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        warning_sink: Callable[[FakeMoveWarning], None] | None = None,
        config: FakeMoveConfig | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._sink = warning_sink
        self._cfg = config or FakeMoveConfig()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _dim_scores(self, m: SignalMetrics) -> dict[SignalDim, float]:
        """7 维嫌疑分（各∈[0,1]，越高越可疑；静态表驱动确定性）。"""
        cfg = self._cfg
        return {
            SignalDim.ACTIVE_BUY: _clamp01((cfg.active_buy_mid - m.active_buy_ratio) / cfg.active_buy_mid),
            SignalDim.BIG_ORDER_INFLOW: (
                0.0 if m.big_order_net_inflow >= 0.0 else _clamp01(-m.big_order_net_inflow / cfg.big_order_scale)
            ),
            SignalDim.VOLUME_PERSISTENCE: _clamp01(1.0 - m.volume_persistence),
            SignalDim.SECTOR_FOLLOW: _clamp01(1.0 - m.sector_follow_rate),
            SignalDim.PUMP_WINDOW: _WINDOW_SUSPICION[m.pump_window],
            SignalDim.BOTTOM_CHIP: _clamp01(1.0 - m.bottom_chip_ratio),
            SignalDim.LHB: (0.0 if m.lhb_net_buy >= 0.0 else _clamp01(-m.lhb_net_buy / cfg.lhb_scale)),
        }

    # ── 评估 ─────────────────────────────────────────────────────────────

    def assess(self, symbol: str, metrics: SignalMetrics) -> FakeMoveAssessment:
        """7 维打分 → 假动作概率 + 模式命中 + >85% 暂停追涨告警。

        Raises:
            FakeMoveError: 空 symbol/信号取值越界或非有限/未知拉升时段。
        """
        if not symbol or not symbol.strip():
            raise FakeMoveError("symbol 为空")
        _validate_metrics(metrics)
        scores = self._dim_scores(metrics)
        weights = self._cfg.weights if self._cfg.weights is not None else _EQUAL_WEIGHTS
        probability = _clamp01(sum(w * scores[dim] for w, dim in zip(weights, _DIM_ORDER, strict=False)))
        matched = tuple(
            rule.pattern
            for rule in FAKE_MOVE_RULES.values()
            if all(scores[d] >= self._cfg.pattern_match_threshold for d in rule.contradiction_dims)
        )
        now = self._clock()
        warning: FakeMoveWarning | None = None
        if probability > self._cfg.warn_threshold:
            warning = FakeMoveWarning(
                symbol=symbol,
                fake_percent=probability * 100.0,
                matched_patterns=matched,
                action="suspend_chase",
                raised_at=now,
            )
            _log.warning(
                "假动作嫌疑 %.2f%% > %.2f%%: %s → 暂停追涨",
                probability * 100.0,
                self._cfg.warn_threshold * 100.0,
                symbol,
            )
            if self._sink is not None:
                try:
                    self._sink(warning)
                except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                    _log.exception("warning_sink 告警失败")
        return FakeMoveAssessment(
            symbol=symbol,
            fake_probability=probability,
            fake_percent=probability * 100.0,
            dim_scores=scores,
            matched_patterns=matched,
            warning=warning,
            assessed_at=now,
        )

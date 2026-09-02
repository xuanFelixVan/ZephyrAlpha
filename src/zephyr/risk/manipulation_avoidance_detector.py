# [BLUEPRINT] MOD-RK-39 | docs/03_modules/_domain_risk/manipulation_avoidance_detector/blueprint.md
# [MODULE] zephyr.risk.manipulation_avoidance_detector
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-02(Pre-Trade 禁开仓消费候选); D_ASHARE_SIGNAL(信号降权装配批); D_GOV_AUDIT(检测日志落账)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 五类子分线性截断∈[0,1]; 总分=Σw·s/Σw(默认等权); score≥0.6→AVOID/≥0.4→WATCH/否则CLEAR; AVOID入回避名单WATCH入观察名单(降序); WATCH/AVOID经audit_sink留痕; verdict/report frozen; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidManipulationInputError
# [TESTS] tests/risk/test_manipulation_avoidance_detector.py
# [A_module] module_id=MOD-RK-39 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Manipulation Avoidance Detector — 庄股操纵回避检测器 (MOD-RK-39, CAND-RSK-043, B13-04455 模块54)

A4 §6.1 模块54 落码（统计档）：对倒放量/尾盘异动/价量背离/换手异常/筹码高度集中
五类统计特征 → 操纵风险评分 → CLEAR/WATCH/AVOID 三级 → 回避名单（禁开仓 + 信号
降权消费）。仅用免费日线/分钟行情统计量（GNN/联邦学习档放弃，TSV 裁定）。

与既有件分工（蓝图 §0 查重裁定）：MOD-CMP-007/MOD-CMP-011（compliance 族）为
**自我操纵自证**（检测自身订单 Spoofing/Layering/WashTrade 以自证清白），方向相反；
MOD-SIG-088 为主力画像/合力方向（信号域资金行为分析）。本模块为**他人（庄股）操纵
回避**判定核心，口径互不重复。

纪律：纯函数无 IO；统计量由调用方注入（不越域取数，三维解耦）；禁开仓/降权仅产
信号（执行委托 MOD-RK-02 Pre-Trade / 信号域装配批）；检测日志经 audit_sink 回调
委托 D_GOV_AUDIT 落账（本模块不落盘）。

依据: blueprint.md（MOD-RK-39）§3 核心规则；ESMA 操纵检测思路（统计档）+
沪深交易所异常交易监控指标
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 统计特征 ManipulationFeatures
#   fields: volume_spike_ratio(对倒放量) + tail_move_ratio(尾盘异动) + price_volume_corr(价量背离) + turnover_spike_ratio(换手异常) + chip_concentration(筹码集中)
#   code: assess() features 参数
# - id: I2
#   name: 配置
#   fields: weights(五类权重) + wash_ref=5/tail_ref=0.5/turnover_ref=3 + watch=0.4/avoid=0.6
#   code: __init__ 参数
# 层: 算法
# - id: A1
#   name_zh: ① 子分映射（线性截断）
#   name_en: _sub_scores
#   intro: wash=min(1,vol/5); tail=min(1,tail/0.5); divergence=max(0,-corr); turnover=min(1,to/3); chip=直传
# - id: A2
#   name_zh: ② 加权总分与三级判定
#   name_en: assess
#   intro: score=Σw·s/Σw; ≥avoid→AVOID; ≥watch→WATCH; 否则CLEAR
# - id: A3
#   name_zh: ③ 回避名单聚合
#   name_en: assess_batch
#   intro: AVOID→avoid_list; WATCH→watch_list; 各按 score 降序
# 层: 输出
# - id: O1
#   name: ManipulationVerdict / AvoidanceReport
#   fields: score/level/feature_scores + avoid_list/watch_list（frozen）
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A2 --> O1
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "AvoidanceLevel",
    "AvoidanceReport",
    "InvalidManipulationInputError",
    "ManipulationAvoidanceDetector",
    "ManipulationFeatures",
    "ManipulationVerdict",
]

_FEATURE_KEYS: Final = ("wash", "tail", "divergence", "turnover", "chip")
_DEFAULT_WASH_REF: Final = 5.0  # 量比参考（当日量/N日均量 5 倍→满分）
_DEFAULT_TAIL_REF: Final = 0.5  # 尾盘异动参考（|尾盘收益|/全日振幅 0.5→满分）
_DEFAULT_TURNOVER_REF: Final = 3.0  # 换手异常参考（3 倍→满分）
_DEFAULT_WATCH_THRESHOLD: Final = 0.4
_DEFAULT_AVOID_THRESHOLD: Final = 0.6


class InvalidManipulationInputError(ZephyrBaseError):
    """操纵回避检测输入/配置非法（Fail-Closed）。"""


class AvoidanceLevel(str, Enum):
    """回避分级。"""

    CLEAR = "CLEAR"  # 正常
    WATCH = "WATCH"  # 观察名单
    AVOID = "AVOID"  # 回避名单（禁开仓 + 信号降权）


def _finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise InvalidManipulationInputError(f"{name} 必须为有限值: {value}")
    return v


def _non_negative(name: str, value: float) -> float:
    v = _finite(name, value)
    if v < 0:
        raise InvalidManipulationInputError(f"{name} 必须 ≥0: {value}")
    return v


@dataclass(frozen=True)
class ManipulationFeatures:
    """五类统计特征观测（frozen；由调用方用免费日线/分钟数据预计算注入）。"""

    volume_spike_ratio: float  # 当日成交量 / N 日均量（对倒放量代理，≥0）
    tail_move_ratio: float  # |尾盘 30min 收益| / 全日振幅（尾盘异动，≥0）
    price_volume_corr: float  # 近 N 日价量相关系数（价量背离，∈[-1,1]）
    turnover_spike_ratio: float  # 当日换手率 / N 日换手中位数（换手异常，≥0）
    chip_concentration: float  # 筹码集中度代理（控盘特征，∈[0,1]）

    def __post_init__(self) -> None:
        _non_negative("volume_spike_ratio", self.volume_spike_ratio)
        _non_negative("tail_move_ratio", self.tail_move_ratio)
        corr = _finite("price_volume_corr", self.price_volume_corr)
        if not -1.0 <= corr <= 1.0:
            raise InvalidManipulationInputError(f"price_volume_corr 必须 ∈[-1,1]: {corr}")
        _non_negative("turnover_spike_ratio", self.turnover_spike_ratio)
        chip = _finite("chip_concentration", self.chip_concentration)
        if not 0.0 <= chip <= 1.0:
            raise InvalidManipulationInputError(f"chip_concentration 必须 ∈[0,1]: {chip}")


@dataclass(frozen=True)
class ManipulationVerdict:
    """单标的操纵回避判定（frozen）。"""

    symbol: str
    score: float  # 操纵风险评分 ∈[0,1]
    level: AvoidanceLevel
    feature_scores: Mapping[str, float]  # 五类子分（wash/tail/divergence/turnover/chip）
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AvoidanceReport:
    """批量判定报告（frozen）。"""

    verdicts: tuple[ManipulationVerdict, ...]
    avoid_list: tuple[str, ...]  # 回避名单（AVOID，score 降序）
    watch_list: tuple[str, ...]  # 观察名单（WATCH，score 降序）


class ManipulationAvoidanceDetector:
    """庄股操纵回避检测器（五类统计特征 → 评分 → 回避名单）。

    Args:
        weights: 五类子分权重（默认等权；键限 wash/tail/divergence/turnover/chip，>0）
        wash_ref / tail_ref / turnover_ref: 子分线性截断参考值（>0）
        watch_threshold / avoid_threshold: 分级阈值（0<watch<avoid≤1）
        audit_sink: WATCH/AVOID 判定回调（委托 D_GOV_AUDIT 落账；None=仅返回）
    """

    def __init__(
        self,
        *,
        weights: Mapping[str, float] | None = None,
        wash_ref: float = _DEFAULT_WASH_REF,
        tail_ref: float = _DEFAULT_TAIL_REF,
        turnover_ref: float = _DEFAULT_TURNOVER_REF,
        watch_threshold: float = _DEFAULT_WATCH_THRESHOLD,
        avoid_threshold: float = _DEFAULT_AVOID_THRESHOLD,
        audit_sink: Callable[[ManipulationVerdict], None] | None = None,
    ) -> None:
        self._wash_ref = _non_negative("wash_ref", wash_ref) or self._reject_zero("wash_ref")
        self._tail_ref = _non_negative("tail_ref", tail_ref) or self._reject_zero("tail_ref")
        self._turnover_ref = _non_negative("turnover_ref", turnover_ref) or self._reject_zero("turnover_ref")
        watch = _finite("watch_threshold", watch_threshold)
        avoid = _finite("avoid_threshold", avoid_threshold)
        if not 0.0 < watch < avoid <= 1.0:
            raise InvalidManipulationInputError(f"阈值须满足 0<watch<avoid≤1: watch={watch}, avoid={avoid}")
        self._watch_threshold = watch
        self._avoid_threshold = avoid

        raw = dict.fromkeys(_FEATURE_KEYS, 1.0) if weights is None else dict(weights)
        if set(raw) != set(_FEATURE_KEYS):
            raise InvalidManipulationInputError(f"weights 键必须恰为五类 {sorted(_FEATURE_KEYS)}: {sorted(raw)}")
        parsed: dict[str, float] = {}
        for key, value in raw.items():
            w = _finite(f"weights[{key}]", value)
            if w <= 0:
                raise InvalidManipulationInputError(f"weights[{key}] 必须 >0: {value}")
            parsed[key] = w
        self._weights = parsed
        self._audit_sink = audit_sink

    @staticmethod
    def _reject_zero(name: str) -> float:
        raise InvalidManipulationInputError(f"{name} 必须 >0")

    def _sub_scores(self, f: ManipulationFeatures) -> dict[str, float]:
        return {
            "wash": min(1.0, f.volume_spike_ratio / self._wash_ref),
            "tail": min(1.0, f.tail_move_ratio / self._tail_ref),
            "divergence": max(0.0, -f.price_volume_corr),
            "turnover": min(1.0, f.turnover_spike_ratio / self._turnover_ref),
            "chip": f.chip_concentration,
        }

    def assess(self, symbol: str, features: ManipulationFeatures) -> ManipulationVerdict:
        """单标的判定（WATCH/AVOID 经 audit_sink 留痕）。"""
        if not symbol:
            raise InvalidManipulationInputError("symbol 不能为空")
        if not isinstance(features, ManipulationFeatures):
            raise InvalidManipulationInputError(f"features 类型非法: {type(features).__name__}")
        sub = self._sub_scores(features)
        total_w = sum(self._weights.values())
        score = sum(self._weights[k] * sub[k] for k in _FEATURE_KEYS) / total_w
        if score >= self._avoid_threshold:
            level = AvoidanceLevel.AVOID
        elif score >= self._watch_threshold:
            level = AvoidanceLevel.WATCH
        else:
            level = AvoidanceLevel.CLEAR
        verdict = ManipulationVerdict(
            symbol=symbol,
            score=score,
            level=level,
            feature_scores=sub,
        )
        if level is not AvoidanceLevel.CLEAR and self._audit_sink is not None:
            self._audit_sink(verdict)
        return verdict

    def assess_batch(self, batch: Mapping[str, ManipulationFeatures]) -> AvoidanceReport:
        """批量判定 → 回避名单（AVOID 降序）+ 观察名单（WATCH 降序）。"""
        if not batch:
            raise InvalidManipulationInputError("batch 不能为空")
        verdicts = tuple(self.assess(symbol, features) for symbol, features in batch.items())
        avoid = sorted(
            (v for v in verdicts if v.level is AvoidanceLevel.AVOID),
            key=lambda v: v.score,
            reverse=True,
        )
        watch = sorted(
            (v for v in verdicts if v.level is AvoidanceLevel.WATCH),
            key=lambda v: v.score,
            reverse=True,
        )
        return AvoidanceReport(
            verdicts=verdicts,
            avoid_list=tuple(v.symbol for v in avoid),
            watch_list=tuple(v.symbol for v in watch),
        )

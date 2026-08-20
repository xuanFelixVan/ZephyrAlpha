# [BLUEPRINT] MOD-RK-07 | docs/03_modules/_domain_risk/concentration_monitor/blueprint.md
# [MODULE] zephyr.risk.core.concentration_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy
# [CONSUMERS] MOD-RK-02(Pre-Trade Checker,集中度Hard Block) ; MOD-RK-03(Portfolio Risk Monitor,实时监控) ; MOD-RK-13(Crowding Monitor)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] weights归一化(总和=1);HHI∈[0,1];max_single_weight≤1;告警级别由当前集中度唯一决定;事件去抖(连续相同级别不重复发射)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidConcentrationInputError
# [TESTS] tests/risk/test_concentration_monitor.py
# [A_module] module_id=MOD-RK-07 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Concentration Risk Monitor — 集中度风险监控器 (MOD-RK-07)

D-RISK §1.2 L1 Pre-Trade + L2 Real-Time 双线使用。计算持仓集中度三大指标:
    1. HHI (Herfindahl-Hirschman Index): 个股权重平方和, [1/N, 1], 越高越集中
       - < 0.10  低集中 (分散)
       - 0.10~0.18 中等集中
       - > 0.18  高集中 (触发告警)
    2. 行业暴露 (Industry Exposure): 申万31行业权重分布, max_industry_weight vs limit
    3. 个股集中度 (Single Stock Concentration): max_single_weight vs limit

实时计算 + 三级告警 (NONE/WARNING/CRITICAL), 供 RK-02 Pre-Trade Hard Block + RK-03 监控。

属 A 类基础设施 (权重归一化 + 平方和 + 分组聚合, 数学逻辑明确), 阈值为 C 类可调参数。
依据: D:\临时工作区\依赖图	-D-RISK-风控域.md §1.2 RK-07, §7.5 行业集中度
SSoT: depgraph MOD-RK-07
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓权重 字典
#   fields: {symbol: weight}权重≥0且总和>0自动归一化; 负权重抛InvalidConcentrationInputError
#   code: update() weights L239
# - id: I2
#   name: 行业映射 字典
#   fields: {symbol: industry_name}可选; 无映射symbol归入__UNCLASSIFIED__; 不提供则跳过行业暴露
#   code: update() industry_mapping L240
# - id: I3
#   name: 集中度阈值配置 ConcentrationConfig
#   fields: hhi_warning0.10/hhi_critical0.18/max_single_weight0.10/max_industry_weight0.30/warning_ratio0.8
#   code: ConcentrationConfig L92-110
# 层: 特征
# - id: F1
#   name_zh: HHI赫芬达尔指数
#   name_en: hhi
#   intro: 个股权重平方和, 越高说明组合越集中
#   formula: HHI=Σw_i² ∈[1/N,1] (w为归一化权重)
#   code: concentration_monitor.py L337-339
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 最大个股权重
#   name_en: max_single_weight
#   intro: 权重最大那只票占组合多少
#   formula: max_single=max(w_i); 空仓返回(None,0)
#   code: concentration_monitor.py L341-347
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 最大行业权重
#   name_en: max_industry_weight
#   intro: 按行业聚合权重后取占比最高的行业
#   formula: industry_w[ind]=Σ_{s∈ind} w_s → max_industry=max(industry_w)
#   code: concentration_monitor.py L349-358 + L270-271
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 三级告警判定
#   name_en: _classify
#   intro: 三大指标各自比阈值, 取最严重级别并记录触发原因
#   desc: HHI≥0.18或个股>0.10或行业>0.30→CRITICAL; 达warning线(HHI0.10/个股80%限额/行业80%限额)→WARNING; 否则NONE; 逐级append breach_reasons
#   inputs: F1 F2 F3 I3
#   outputs: 告警级别 + breach_reasons列表
#   invariant: 告警级别由当前集中度唯一决定
# - id: A2
#   name_zh: ② 快照装配与事件去抖
#   name_en: ConcentrationMonitor.update
#   intro: 归一化权重算三大指标出快照, 级别变化才发射告警事件
#   desc: _normalize_weights校验归一化→算HHI/个股/行业→_classify→装ConcentrationSnapshot; level≠_last_level才构造ConcentrationAlertedEvent并_emit通知监听器
#   inputs: I1 I2 A1
#   outputs: ConcentrationSnapshot + 级别变化时发ConcentrationAlertedEvent
#   invariant: 事件去抖(连续相同级别不重复发射)
# 层: 输出
# - id: O1
#   name_zh: 集中度快照
#   name_en: ConcentrationSnapshot
#   intro: 含HHI/最大个股/最大行业/告警级别/触发原因的不可变快照
#   invariant: HHI∈[0,1]; weights归一化Σ=1
#   downstream: Pre-Trade Checker MOD-RK-02(集中度Hard Block); Portfolio Risk Monitor MOD-RK-03(实时监控); Crowding Monitor MOD-RK-13
# - id: O2
#   name_zh: 集中度告警事件
#   name_en: ConcentrationAlertedEvent
#   intro: 级别变化时经on_concentration_alerted订阅链路发给监听器的告警事件
#   downstream: Pre-Trade Checker MOD-RK-02; Portfolio Risk Monitor MOD-RK-03(经监听器订阅)
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 -.->|断点| F3
# I2 -.->|断点| F3
# F1 --> A1
# F2 --> A1
# F3 --> A1
# I3 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# A2 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ConcentrationAlertLevel",
    "ConcentrationConfig",
    "ConcentrationSnapshot",
    "ConcentrationAlertedEvent",
    "ConcentrationMonitor",
    "InvalidConcentrationInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class ConcentrationAlertLevel(str, Enum):
    """集中度告警级别 (严重度递增)。"""

    NONE = "NONE"  # 集中度在阈值内
    WARNING = "WARNING"  # 接近上限 (达 warning 阈值)
    CRITICAL = "CRITICAL"  # 超过硬上限

    @property
    def severity(self) -> int:
        return {"NONE": 0, "WARNING": 1, "CRITICAL": 2}[self.value]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidConcentrationInputError(ZephyrBaseError):
    """集中度监控输入数据非法 (如权重为负、权重和为零)。"""

    error_code = "ZA-RK-0007"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConcentrationConfig:
    """集中度阈值配置 (设计真源 §1.2 RK-07 + §7.4/§7.5)。

    Attributes:
        hhi_warning: HHI 告警阈值, 默认 0.10
        hhi_critical: HHI 硬上限, 默认 0.18 (监管标准)
        max_single_weight: 单一持仓权重硬上限, 默认 0.10 (10%, §7.4)
        single_warning_ratio: 达硬上限多少比例告警, 默认 0.8 (即 8% 告警)
        max_industry_weight: 单一行业权重硬上限, 默认 0.30 (§7.5, 极端±15%绝对上限30%)
        industry_warning_ratio: 达硬上限多少比例告警, 默认 0.8
    """

    hhi_warning: float = 0.10
    hhi_critical: float = 0.18
    max_single_weight: float = 0.10
    single_warning_ratio: float = 0.8
    max_industry_weight: float = 0.30
    industry_warning_ratio: float = 0.8

    def __post_init__(self) -> None:
        for name, val in (
            ("hhi_warning", self.hhi_warning),
            ("hhi_critical", self.hhi_critical),
            ("max_single_weight", self.max_single_weight),
            ("max_industry_weight", self.max_industry_weight),
        ):
            if not 0 < val <= 1:
                raise InvalidConcentrationInputError(f"{name} must be in (0,1], got {val}")
        if not 0 < self.single_warning_ratio <= 1:
            raise InvalidConcentrationInputError(
                f"single_warning_ratio must be in (0,1], got {self.single_warning_ratio}"
            )
        if not 0 < self.industry_warning_ratio <= 1:
            raise InvalidConcentrationInputError(
                f"industry_warning_ratio must be in (0,1], got {self.industry_warning_ratio}"
            )
        if self.hhi_warning >= self.hhi_critical:
            raise InvalidConcentrationInputError(
                f"hhi_warning ({self.hhi_warning}) must be < hhi_critical ({self.hhi_critical})"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConcentrationSnapshot:
    """集中度快照。

    Attributes:
        hhi: Herfindahl 指数 ∈ [1/N, 1]
        max_single_weight: 最大个股权重
        max_single_symbol: 最大权重个股代码 (None=空仓)
        max_industry_weight: 最大行业权重 (无行业映射时=None)
        max_industry_name: 最大权重行业名 (无行业映射时=None)
        holdings_count: 持仓数量
        industry_weights: 行业权重字典 {industry: weight}
        level: 综合告警级别 (取所有指标最严重级别)
        breach_reasons: 触发告警的原因列表
        timestamp: 快照时间
    """

    hhi: float
    max_single_weight: float
    max_single_symbol: str | None
    max_industry_weight: float | None
    max_industry_name: str | None
    holdings_count: int
    industry_weights: dict[str, float]
    level: ConcentrationAlertLevel
    breach_reasons: list[str]
    timestamp: datetime

    @property
    def is_critical(self) -> bool:
        return self.level is ConcentrationAlertLevel.CRITICAL

    @property
    def is_diversified(self) -> bool:
        """是否充分分散 (HHI < warning 阈值)。"""
        return self.hhi < 0.10


@dataclass(frozen=True)
class ConcentrationAlertedEvent:
    """集中度告警事件 (级别变化时发射)。"""

    level: ConcentrationAlertLevel
    previous_level: ConcentrationAlertLevel
    snapshot: ConcentrationSnapshot
    timestamp: datetime

    @property
    def is_escalation(self) -> bool:
        return self.level.severity > self.previous_level.severity


# ──────────────────────────────────────────────────────────────────────────────
# 集中度监控器
# ──────────────────────────────────────────────────────────────────────────────


class ConcentrationMonitor:
    """集中度风险监控器——HHI+行业暴露+个股集中度+三级告警。

    用法:
        monitor = ConcentrationMonitor()
        weights = {"600000.SH": 0.08, "000001.SZ": 0.06, ...}
        industries = {"600000.SH": "银行", "000001.SZ": "银行", ...}
        snap = monitor.update(weights, industry_mapping=industries)
        if snap.is_critical:
            # Hard Block (RK-02)

    Args:
        config: 阈值配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: ConcentrationConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or ConcentrationConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[ConcentrationAlertedEvent], None]] = []
        self._last_level = ConcentrationAlertLevel.NONE

    @property
    def config(self) -> ConcentrationConfig:
        return self._config

    @property
    def last_level(self) -> ConcentrationAlertLevel:
        return self._last_level

    # ── 公开 API ──

    def update(
        self,
        weights: dict[str, float],
        industry_mapping: dict[str, str] | None = None,
        now: datetime | None = None,
    ) -> ConcentrationSnapshot:
        """计算当前持仓集中度并返回快照 (级别变化时发射告警事件)。

        Args:
            weights: {symbol: weight}, 权重需 ≥0, 总和>0 (自动归一化)
            industry_mapping: {symbol: industry_name}, 可选, 用于行业暴露
            now: 时间戳

        Returns:
            ConcentrationSnapshot

        Raises:
            InvalidConcentrationInputError: 权重为负 / 权重和为零
        """
        now = now or self._clock()
        normalized = self._normalize_weights(weights)

        # 1. HHI
        hhi = self._calc_hhi(normalized)

        # 2. 个股集中度
        max_symbol, max_weight = self._max_weight(normalized)

        # 3. 行业暴露 (仅当显式提供行业映射时计算, 否则跳过避免误报)
        if industry_mapping:
            industry_weights = self._aggregate_industries(normalized, industry_mapping)
            max_ind_name = max(industry_weights, key=industry_weights.get)
            max_ind_weight = industry_weights[max_ind_name]
        else:
            industry_weights = {}
            max_ind_name = None
            max_ind_weight = None

        # 4. 级别判定
        reasons: list[str] = []
        level = self._classify(hhi, max_weight, max_ind_weight, reasons)

        snapshot = ConcentrationSnapshot(
            hhi=hhi,
            max_single_weight=max_weight,
            max_single_symbol=max_symbol,
            max_industry_weight=max_ind_weight,
            max_industry_name=max_ind_name,
            holdings_count=len(normalized),
            industry_weights=industry_weights,
            level=level,
            breach_reasons=reasons,
            timestamp=now,
        )

        # 5. 事件去抖
        if level is not self._last_level:
            event = ConcentrationAlertedEvent(
                level=level,
                previous_level=self._last_level,
                snapshot=snapshot,
                timestamp=now,
            )
            self._last_level = level
            self._emit(event)

        return snapshot

    def on_concentration_alerted(self, listener: Callable[[ConcentrationAlertedEvent], None]) -> None:
        """订阅集中度告警事件。"""
        self._listeners.append(listener)

    # ── 内部: 计算 ──

    @staticmethod
    def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
        """校验并归一化权重 (过滤 0 权重, 拒绝负权重)。"""
        if not weights:
            raise InvalidConcentrationInputError("weights is empty")
        # 先校验负权重 (在过滤 0 之前, 防止负权重被静默丢弃)
        for s, w in weights.items():
            if float(w) < 0:
                raise InvalidConcentrationInputError(f"negative weight for {s}: {w}")
        cleaned = {s: float(w) for s, w in weights.items() if w > 0}
        if not cleaned:
            raise InvalidConcentrationInputError("no positive weights (sum<=0 or all zero)")
        total = sum(cleaned.values())
        if total <= 0:
            raise InvalidConcentrationInputError(f"weights sum <= 0: {total}")
        return {s: w / total for s, w in cleaned.items()}

    @staticmethod
    def _calc_hhi(weights: dict[str, float]) -> float:
        """HHI = Σ w_i², ∈ [1/N, 1]。"""
        return float(sum(w * w for w in weights.values()))

    @staticmethod
    def _max_weight(weights: dict[str, float]) -> tuple[str | None, float]:
        """返回 (最大权重symbol, 最大权重值)。空仓返回 (None, 0)。"""
        if not weights:
            return None, 0.0
        sym = max(weights, key=weights.get)
        return sym, weights[sym]

    @staticmethod
    def _aggregate_industries(weights: dict[str, float], mapping: dict[str, str]) -> dict[str, float]:
        """按行业聚合权重。无映射的 symbol 归入 '__UNCLASSIFIED__'。"""
        agg: dict[str, float] = {}
        for sym, w in weights.items():
            ind = mapping.get(sym, "__UNCLASSIFIED__")
            agg[ind] = agg.get(ind, 0.0) + w
        return agg

    def _classify(
        self,
        hhi: float,
        max_single: float,
        max_industry: float | None,
        reasons: list[str],
    ) -> ConcentrationAlertLevel:
        """综合三大指标判定告警级别 (取最严重)。"""
        cfg = self._config
        levels: list[ConcentrationAlertLevel] = []

        # HHI
        if hhi >= cfg.hhi_critical:
            levels.append(ConcentrationAlertLevel.CRITICAL)
            reasons.append(f"HHI={hhi:.4f} >= critical {cfg.hhi_critical}")
        elif hhi >= cfg.hhi_warning:
            levels.append(ConcentrationAlertLevel.WARNING)
            reasons.append(f"HHI={hhi:.4f} >= warning {cfg.hhi_warning}")

        # 个股集中度
        single_warn_threshold = cfg.max_single_weight * cfg.single_warning_ratio
        if max_single > cfg.max_single_weight:
            levels.append(ConcentrationAlertLevel.CRITICAL)
            reasons.append(f"max_single={max_single:.4f} > limit {cfg.max_single_weight}")
        elif max_single >= single_warn_threshold:
            levels.append(ConcentrationAlertLevel.WARNING)
            reasons.append(f"max_single={max_single:.4f} >= warning {single_warn_threshold:.4f}")

        # 行业集中度
        if max_industry is not None:
            ind_warn_threshold = cfg.max_industry_weight * cfg.industry_warning_ratio
            if max_industry > cfg.max_industry_weight:
                levels.append(ConcentrationAlertLevel.CRITICAL)
                reasons.append(f"max_industry={max_industry:.4f} > limit {cfg.max_industry_weight}")
            elif max_industry >= ind_warn_threshold:
                levels.append(ConcentrationAlertLevel.WARNING)
                reasons.append(f"max_industry={max_industry:.4f} >= warning {ind_warn_threshold:.4f}")

        if not levels:
            return ConcentrationAlertLevel.NONE
        return max(levels, key=lambda lv: lv.severity)

    def _emit(self, event: ConcentrationAlertedEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 隔离监听器故障
                logger.error("Concentration alert listener error: %s", exc, exc_info=True)

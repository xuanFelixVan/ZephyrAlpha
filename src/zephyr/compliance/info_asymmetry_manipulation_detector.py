# [BLUEPRINT] MOD-CMP-014 | docs/03_modules/_domain_compliance/info_asymmetry_manipulation_detector/blueprint.md
# [MODULE] zephyr.compliance.info_asymmetry_manipulation_detector
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] 无（协议核心纯内存；clock/阈值配置/特征数据 全注入；仅 stdlib）
# [CONSUMERS] 运行时装配批（披露登记与行情特征统一注入 / 回避名单供漏斗排除）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 空窗期判定闭合(披露间隔>gap_days 或 11月-次年4月30日窗口); z扫描须len(returns)>=2且基准方差>0; 三模式评分各∈[0,1]确定性加权; 回避名单确定性排序去重; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/info_asymmetry_manipulation_detector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InfoAsymmetryError(占位 ZA-CMP-UNREGISTERED-INFO-ASYMMETRY)——空symbol/未登记披露/样本不足/基准方差为零/特征越界时抛
# [TESTS] tests/compliance/test_info_asymmetry_manipulation_detector.py
# [A_module] module_id=MOD-CMP-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""InfoAsymmetryManipulationDetector — 信息不对称期与操纵检测器（MOD-CMP-014）。

B10-01426（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-005，A1 模块54）：
**空窗期判定**（披露间隔 >90 天 / 11月-次年4月30日窗口）+ 异常波动 **z>2
扫描** + **三模式操纵嫌疑评分**（幌骗/对敲/尾盘操纵：偏离度 + 撤单率 +
间隔 + 量集中度等注入数据）+ **回避名单输出**供漏斗排除。

设计要点：
- **纯内存/DI**：时钟注入；披露日期、收益率序列、操纵特征全部经参数
  注入（不抓行情不触网）；阈值集中为 DetectorConfig 可注入。
- **确定性**：z 分数用总体标准差；三模式评分 = 特征归一化加权（各 ∈
  [0,1]），同输入必同输出；回避名单按 (symbol) 排序去重。
- **Fail-Closed**：未登记披露/样本不足/基准方差为零/特征越界一律抛
  InfoAsymmetryError，绝不静默放行。

查重分工：trading_compliance_detector=盘中合规规则族（无披露空窗语义）；
intraday_manipulation_detector=盘中流式操纵检测（本件=信息披露空窗期视角 +
三模式离线评分，零交集）。
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
    "AvoidanceEntry",
    "DetectorConfig",
    "InfoAsymmetryError",
    "InfoAsymmetryManipulationDetector",
    "ManipulationFeatures",
    "ManipulationMode",
    "ScanReport",
]


class InfoAsymmetryError(Exception):
    """信息不对称/操纵检测输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-CMP-UNREGISTERED-INFO-ASYMMETRY。
    """


class ManipulationMode(str, Enum):
    """操纵嫌疑模式（词表闭合）。"""

    SPOOFING = "spoofing"      # 幌骗（大额虚假申报+高撤单）
    WASH_TRADE = "wash_trade"  # 对敲（自成交+量集中）
    TAIL = "tail"              # 尾盘操纵（尾盘拉抬/打压）


@dataclass(frozen=True)
class DetectorConfig:
    """检测阈值配置（注入式；全部确定性）。"""

    gap_days: int = 90               # 披露间隔空窗阈值（天）
    z_threshold: float = 2.0         # 异常波动 z 阈值
    score_threshold: float = 0.6     # 操纵嫌疑入选阈值
    spoofing_cancel_weight: float = 0.7   # 幌骗：撤单率权重
    spoofing_dev_weight: float = 0.3      # 幌骗：偏离度权重
    wash_self_weight: float = 0.6         # 对敲：自成交占比权重
    wash_conc_weight: float = 0.4         # 对敲：量集中度权重
    tail_vol_weight: float = 0.5          # 尾盘：尾盘量占比权重
    tail_dev_weight: float = 0.5          # 尾盘：尾盘偏离度权重


@dataclass(frozen=True)
class ManipulationFeatures:
    """三模式操纵评分特征（数据注入；比率类 ∈ [0,1]，偏离度 ≥ 0）。"""

    deviation: float            # 价格偏离度（相对基准，≥0）
    cancel_rate: float          # 撤单率 ∈ [0,1]
    order_intervals: tuple[float, ...]  # 申报间隔序列（秒，均 ≥0）
    volume_concentration: float  # 量集中度 ∈ [0,1]
    tail_volume_ratio: float    # 尾盘成交量占比 ∈ [0,1]
    tail_deviation: float       # 尾盘价格偏离度 ≥0
    self_trade_ratio: float     # 自成交占比 ∈ [0,1]


@dataclass(frozen=True)
class ScanReport:
    """单标的扫描报告（frozen）。"""

    symbol: str
    as_of: datetime.date
    asymmetry_window: bool
    z_score: float
    volatility_anomaly: bool
    mode_scores: Mapping[ManipulationMode, float]
    suspected: bool
    scanned_at: datetime.datetime


@dataclass(frozen=True)
class AvoidanceEntry:
    """回避名单条目（供漏斗排除）。"""

    symbol: str
    score: float
    reasons: tuple[str, ...]
    raised_at: datetime.datetime


#: 空窗期法定窗口月份（11月-次年4月30日 → 月份 ∈ {11,12,1,2,3,4}）
_STATUTORY_WINDOW_MONTHS: Final[frozenset[int]] = frozenset({11, 12, 1, 2, 3, 4})


class InfoAsymmetryManipulationDetector:
    """信息不对称期与操纵检测器（空窗判定 + z 扫描 + 三模式评分 + 回避名单）。

    Args:
        clock: 时钟注入（报告/回避条目时戳确定性来源）。
        config: 阈值配置注入；None 用默认 DetectorConfig。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        config: DetectorConfig | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._config = config or DetectorConfig()
        self._validate_config(self._config)
        self._disclosures: dict[str, datetime.date] = {}
        self._avoidance: dict[str, AvoidanceEntry] = {}

    @staticmethod
    def _validate_config(config: DetectorConfig) -> None:
        if config.gap_days <= 0:
            raise InfoAsymmetryError(f"gap_days 非正: {config.gap_days!r}")
        if config.z_threshold <= 0:
            raise InfoAsymmetryError(f"z_threshold 非正: {config.z_threshold!r}")
        if not 0 < config.score_threshold <= 1:
            raise InfoAsymmetryError(f"score_threshold 越界: {config.score_threshold!r}")

    @staticmethod
    def _ratio(name: str, value: float) -> float:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise InfoAsymmetryError(f"{name} 非数值: {value!r}")
        if not 0.0 <= float(value) <= 1.0:
            raise InfoAsymmetryError(f"{name} 越界 [0,1]: {value!r}")
        return float(value)

    # ── 披露登记 ──────────────────────────────────────────────────────────

    def register_disclosure(self, symbol: str, last_disclosure_date: datetime.date) -> None:
        """登记标的上次披露日期（重复登记按最新覆盖，确定性）。"""
        if not symbol:
            raise InfoAsymmetryError("symbol 为空")
        if not isinstance(last_disclosure_date, datetime.date):
            raise InfoAsymmetryError(f"last_disclosure_date 非法: {symbol!r}")
        self._disclosures[symbol] = last_disclosure_date

    # ── 空窗期判定 ────────────────────────────────────────────────────────

    def is_asymmetry_window(self, symbol: str, as_of: datetime.date) -> bool:
        """空窗期判定：披露间隔 > gap_days，或落于 11月-次年4月30日法定窗口。"""
        if not symbol:
            raise InfoAsymmetryError("symbol 为空")
        if not isinstance(as_of, datetime.date):
            raise InfoAsymmetryError(f"as_of 非法: {as_of!r}")
        last = self._disclosures.get(symbol)
        if last is None:
            raise InfoAsymmetryError(f"未登记披露: {symbol!r}")
        if (as_of - last).days > self._config.gap_days:
            return True
        return as_of.month in _STATUTORY_WINDOW_MONTHS

    # ── z 扫描 ────────────────────────────────────────────────────────────

    def z_scan(self, returns: Sequence[float]) -> float:
        """末日收益率相对基准窗口的 z 分数（总体标准差；len≥2）。"""
        values = list(returns)
        if len(values) < 2:
            raise InfoAsymmetryError(f"收益率样本不足（须≥2）: {len(values)}")
        for v in values:
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
                raise InfoAsymmetryError(f"收益率非法: {v!r}")
        base = values[:-1]
        mean = sum(base) / len(base)
        variance = sum((v - mean) ** 2 for v in base) / len(base)
        if variance == 0.0:
            raise InfoAsymmetryError("基准窗口方差为零（无法计算 z 分数）")
        return (values[-1] - mean) / math.sqrt(variance)

    # ── 三模式操纵评分 ────────────────────────────────────────────────────

    def _validate_features(self, features: ManipulationFeatures) -> None:
        if not isinstance(features, ManipulationFeatures):
            raise InfoAsymmetryError(f"非法特征类型: {type(features).__name__!r}")
        if not isinstance(features.deviation, (int, float)) or features.deviation < 0:
            raise InfoAsymmetryError(f"deviation 非法: {features.deviation!r}")
        if not isinstance(features.tail_deviation, (int, float)) or features.tail_deviation < 0:
            raise InfoAsymmetryError(f"tail_deviation 非法: {features.tail_deviation!r}")
        self._ratio("cancel_rate", features.cancel_rate)
        self._ratio("volume_concentration", features.volume_concentration)
        self._ratio("tail_volume_ratio", features.tail_volume_ratio)
        self._ratio("self_trade_ratio", features.self_trade_ratio)
        for interval in features.order_intervals:
            if not isinstance(interval, (int, float)) or interval < 0:
                raise InfoAsymmetryError(f"order_intervals 含负值/非数值: {interval!r}")

    def score_manipulation(
        self, features: ManipulationFeatures
    ) -> dict[ManipulationMode, float]:
        """三模式嫌疑评分（各 ∈ [0,1]，确定性加权归一）。"""
        self._validate_features(features)
        cfg = self._config
        # 幌骗：撤单率 + 偏离度（偏离度按 0.1 封顶归一）
        spoofing = (
            cfg.spoofing_cancel_weight * features.cancel_rate
            + cfg.spoofing_dev_weight * min(features.deviation / 0.1, 1.0)
        )
        # 对敲：自成交占比 + 量集中度
        wash = (
            cfg.wash_self_weight * features.self_trade_ratio
            + cfg.wash_conc_weight * features.volume_concentration
        )
        # 尾盘操纵：尾盘量占比 + 尾盘偏离度（同封顶归一）
        tail = (
            cfg.tail_vol_weight * features.tail_volume_ratio
            + cfg.tail_dev_weight * min(features.tail_deviation / 0.1, 1.0)
        )
        return {
            ManipulationMode.SPOOFING: min(max(spoofing, 0.0), 1.0),
            ManipulationMode.WASH_TRADE: min(max(wash, 0.0), 1.0),
            ManipulationMode.TAIL: min(max(tail, 0.0), 1.0),
        }

    # ── 综合扫描 ──────────────────────────────────────────────────────────

    def scan(
        self,
        symbol: str,
        as_of: datetime.date,
        returns: Sequence[float],
        features: ManipulationFeatures,
    ) -> ScanReport:
        """综合扫描：空窗判定 + z 异常 + 三模式评分 → 命中则入回避名单。"""
        asymmetry = self.is_asymmetry_window(symbol, as_of)
        z_score = self.z_scan(returns)
        anomaly = abs(z_score) > self._config.z_threshold
        mode_scores = self.score_manipulation(features)
        hit_modes = tuple(
            mode.value for mode, score in mode_scores.items()
            if score >= self._config.score_threshold
        )
        suspected = bool(hit_modes)
        report = ScanReport(
            symbol=symbol,
            as_of=as_of,
            asymmetry_window=asymmetry,
            z_score=z_score,
            volatility_anomaly=anomaly,
            mode_scores=mode_scores,
            suspected=suspected,
            scanned_at=self._clock(),
        )
        reasons: list[str] = []
        if asymmetry:
            reasons.append("info_asymmetry_window")
        if anomaly:
            reasons.append(f"volatility_z>{self._config.z_threshold:g}")
        reasons.extend(hit_modes)
        if reasons:
            score = max(mode_scores.values())
            self._avoid(symbol, score, tuple(reasons))
        _log.info("扫描: %s asymmetry=%s z=%.3f suspected=%s", symbol, asymmetry, z_score, suspected)
        return report

    # ── 回避名单 ──────────────────────────────────────────────────────────

    def _avoid(self, symbol: str, score: float, reasons: tuple[str, ...]) -> None:
        existing = self._avoidance.get(symbol)
        if existing is not None and existing.score >= score:
            return  # 保留更高分条目（幂等）
        self._avoidance[symbol] = AvoidanceEntry(
            symbol=symbol, score=score, reasons=reasons, raised_at=self._clock()
        )
        _log.warning("回避名单: %s score=%.3f reasons=%s", symbol, score, reasons)

    def avoid_list(self) -> tuple[AvoidanceEntry, ...]:
        """回避名单（按 symbol 确定性排序）。"""
        return tuple(self._avoidance[s] for s in sorted(self._avoidance))

    def avoid_symbols(self) -> tuple[str, ...]:
        """回避标的集合（按 symbol 确定性排序，供漏斗排除）。"""
        return tuple(sorted(self._avoidance))

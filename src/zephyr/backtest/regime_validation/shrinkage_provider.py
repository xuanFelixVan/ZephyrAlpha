# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.shrinkage_provider
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.shrinkage_engine; zephyr.regime.core.regime_detector
# [CONSUMERS] zephyr.backtest.regime_validation.c1_comparator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 返回值∈[0,1.0](只减不增); PIT as-of join(不查未来); shrinkage_enabled=False→恒1.0; 不修改 RegimeDetector 状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ShrinkageProviderError(ZA-BT-0016)
# [TESTS] tests/backtest/test_shrinkage_provider.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #MOD-REGIME-001 #C1-shrinkage-comparator

"""L_BACKTEST — Shrinkage Provider 适配层 (B2: mock 生成器 + ShrinkageAdapter)

为 ShrinkageBacktestEngine 提供 Shrinkage 因子的多种供给方式，对接
RegimeDetector (MOD-REGIME-001) 的 ShrinkageResult，并支持 HMM 未就绪时的
mock 占位。是 11_regime_backtest_validation_plan §4.3 C1 开/关对比的输入侧。

四类 Provider:
  ① ConstShrinkageProvider       — 恒定值（1.0=关/C1 基准，<1.0=测试）
  ② ScheduleShrinkageProvider    — 按日期查表 + PIT as-of join（回放预计算序列）
  ③ MockShrinkageProvider        — 规则 mock（波动率分位→4档映射，HMM 未就绪时占位）
  ④ RegimeDetectorShrinkageAdapter — 适配真实 RegimeDetector（on-demand + 缓存）

ShrinkageAdapter 工具函数:
  - clamp_shrinkage              — 钳制 [0,1]（只减不增不变量）
  - build_schedule_from_results  — list[(date, ShrinkageResult)] → schedule dict
  - build_schedule_from_detector — 批量跑 RegimeDetector → schedule dict（离线回放）

设计要点:
  - 所有 Provider 实现均满足 ShrinkageProvider 协议（structural typing）
  - PIT as-of join：查表时只取 ≤ 查询日期的最近一条，不查未来（铁律）
  - RegimeDetector.shrinkage_enabled=False 时，detector 自身返回 value=1.0，
    adapter 透传，无需 adapter 再判断开关（单一真源在 detector）

依据: 11_regime_backtest_validation_plan §2.2/§4.3 + 30_multi_strategy_concurrency §2.2（Shrinkage=Confidence×Risk）
SSoT: depgraph MOD-BT-001 / MOD-REGIME-001
Version: 0.1.0
"""

from __future__ import annotations

import bisect
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Protocol

from zephyr.backtest.implementations.shrinkage_engine import ShrinkageProvider

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class ShrinkageProviderError(ZephyrBaseError):
    """ZA-BT-0016: Shrinkage provider 构造/查表错误。

    改号留痕：原 ZA-BT-0010 与 data_handler.DataHandlerError 重码，
    #ARCH-ERRCODE-001 裁定 git 首引入者保留 canonical，本类后引入（2026-08-06）改号。
    """

    error_code = "ZA-BT-0016"


# ──────────────────────────────────────────────────────────────────────────────
# 工具函数（ShrinkageAdapter）
# ──────────────────────────────────────────────────────────────────────────────


def clamp_shrinkage(value: float) -> float:
    """钳制 Shrinkage 到 [0.0, 1.0]（只减不增不变量）。

    NaN → 1.0（保守退化为满部署）；越界 → 截断。
    """
    if value != value:  # NaN
        return 1.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def build_schedule_from_results(
    results: list[tuple[datetime, Any]],
) -> dict[datetime, float]:
    """从 RegimeDetector 预计算结果构建 schedule dict。

    Args:
        results: [(date, ShrinkageResult), ...] 或 [(date, float), ...]。
            ShrinkageResult 取 .value；float 直接用；其余类型报错。

    Returns:
        {date: shrinkage_value}（已钳制 [0,1]），按 date 去重后者覆盖。
    """
    schedule: dict[datetime, float] = {}
    for entry in results:
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise ShrinkageProviderError(
                f"results 每项须为 (date, ShrinkageResult|float) 二元组, got {type(entry).__name__}"
            )
        dt, payload = entry
        if not isinstance(dt, datetime):
            raise ShrinkageProviderError(f"日期须为 datetime, got {type(dt).__name__}")
        value = _extract_shrinkage_value(payload)
        schedule[dt] = clamp_shrinkage(value)
    return schedule


def _extract_shrinkage_value(payload: Any) -> float:
    """从 ShrinkageResult 或 float 提取 shrinkage 值。"""
    # ShrinkageResult 有 .value 字段
    if hasattr(payload, "value") and isinstance(payload.value, (int, float)):
        return float(payload.value)
    if isinstance(payload, (int, float)):
        return float(payload)
    raise ShrinkageProviderError(f"无法从 {type(payload).__name__} 提取 shrinkage 值（须为 ShrinkageResult 或 float）")


def build_schedule_from_detector(
    detector: Any,
    dated_inputs: dict[datetime, tuple[dict, dict, dict]],
) -> dict[datetime, float]:
    """批量跑 RegimeDetector.detect() 构建 schedule dict（离线回放模式）。

    Args:
        detector: RegimeDetector 实例（已 fit 或降级均可）。
        dated_inputs: {date: (regime_features, overlay_signals, risk_signal_inputs)}。

    Returns:
        {date: shrinkage_value}（已钳制 [0,1]）。detector.shrinkage_enabled=False
        时全部为 1.0（开关由 detector 单一真源控制）。
    """
    schedule: dict[datetime, float] = {}
    for dt, inputs in sorted(dated_inputs.items()):
        regime_features, overlay_signals, risk_inputs = inputs
        try:
            _probs, shrinkage_result = detector.detect(regime_features, overlay_signals, risk_inputs)
            schedule[dt] = clamp_shrinkage(_extract_shrinkage_value(shrinkage_result))
        except Exception as exc:  # 单日异常降级为满部署，不阻断批量回放
            _logger.warning("RegimeDetector.detect 异常 (date=%s)，当日退化为 1.0: %s", dt, exc)
            schedule[dt] = 1.0
    return schedule


# ──────────────────────────────────────────────────────────────────────────────
# ① ConstShrinkageProvider — 恒定值
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConstShrinkageProvider:
    """恒定 Shrinkage 因子。

    value=1.0 → C1 基准组（关，等价于 DefaultBacktestEngine）。
    value<1.0 → 测试用（如 0.5 表示每日半仓）。
    """

    value: float = 1.0

    def __post_init__(self) -> None:
        if self.value != self.value:
            raise ShrinkageProviderError("value 不能为 NaN")

    def get_shrinkage(self, date: datetime) -> float:  # noqa: ARG002
        return clamp_shrinkage(self.value)


# ──────────────────────────────────────────────────────────────────────────────
# ② ScheduleShrinkageProvider — 按日期查表 + PIT as-of join
# ──────────────────────────────────────────────────────────────────────────────


class ScheduleShrinkageProvider:
    """按日期查表的 Shrinkage 供给（PIT as-of join）。

    回放 RegimeDetector 预计算序列的主用 provider。查询日期 d 时返回
    schedule 中 ≤ d 的最近一条 shrinkage；d 早于首条则返回 1.0（regime 未启动）。

    PIT 铁律：只取 ≤ 查询日期的记录，绝不查未来（bisect_right 在排序日期上二分）。
    """

    def __init__(self, schedule: dict[datetime, float] | None = None) -> None:
        """初始化。

        Args:
            schedule: {date: shrinkage}。None/空 → 恒返回 1.0（无节流）。
                值会被钳制到 [0,1]。
        """
        raw = schedule or {}
        self._dates: list[datetime] = []
        self._values: list[float] = []
        for dt in sorted(raw.keys()):
            self._dates.append(dt)
            self._values.append(clamp_shrinkage(raw[dt]))

    def get_shrinkage(self, date: datetime) -> float:
        """PIT as-of join：返回 ≤ date 的最近 shrinkage，无则 1.0。"""
        if not self._dates:
            return 1.0
        # bisect_right 给出 > date 的首个位置，-1 即 ≤ date 的最近一条
        idx = bisect.bisect_right(self._dates, date) - 1
        if idx < 0:
            return 1.0  # date 早于 schedule 首条 → regime 未启动
        return self._values[idx]

    @property
    def schedule(self) -> dict[datetime, float]:
        """当前 schedule 副本（已排序去重，值已钳制）。"""
        return dict(zip(self._dates, self._values, strict=True))


# ──────────────────────────────────────────────────────────────────────────────
# ③ MockShrinkageProvider — 规则 mock（HMM 未就绪时占位）
# ──────────────────────────────────────────────────────────────────────────────

# 波动率 → Shrinkage 4 档映射（对照 regime ConfidenceSignal 4 档，反相关）
# (波动率上界, shrinkage) —— 从低到高匹配，取首个 vol < 上界
# 设计：低波→满部署，高波/危机→强收缩，模拟 regime 防御行为
_MOCK_VOL_BANDS: tuple[tuple[float, float], ...] = (
    (0.15, 1.00),  # vol<15%  → 满部署（calm）
    (0.25, 0.85),  # 15-25%   → 轻度收缩
    (0.40, 0.60),  # 25-40%   → 中度收缩
    (float("inf"), 0.30),  # ≥40% → 强收缩（crisis-like）
)


class MockShrinkageProvider:
    """mock Shrinkage 生成器——基于波动率分位的规则映射。

    HMM/RegimeDetector 未就绪时，用波动率代理 regime 风险状态，生成贴近 regime
    防御行为的 Shrinkage 序列，供 C1 验证框架先跑通。验证后替换为真实 detector。

    映射（_MOCK_VOL_BANDS，反相关）:
      vol < 15%  → 1.00（满部署）
      15-25%     → 0.85（轻度收缩）
      25-40%     → 0.60（中度收缩）
      ≥ 40%      → 0.30（强收缩，crisis-like）

    Usage:
        mock = MockShrinkageProvider(volatility_schedule={dt1: 0.12, dt2: 0.35, ...})
        engine = ShrinkageBacktestEngine(provider=mock)
    """

    def __init__(
        self,
        volatility_schedule: dict[datetime, float] | None = None,
        vol_fn: Callable[[datetime], float] | None = None,
        bands: tuple[tuple[float, float], ...] | None = None,
    ) -> None:
        """初始化。

        Args:
            volatility_schedule: {date: vol} 波动率序列（与 vol_fn 二选一）。
            vol_fn: 给定日期返回波动率的 callable（在线计算，如查 ClickHouse）。
            bands: 自定义 (vol上界, shrinkage) 映射；None 用默认 _MOCK_VOL_BANDS。
        """
        if volatility_schedule is None and vol_fn is None:
            raise ShrinkageProviderError("须提供 volatility_schedule 或 vol_fn 之一")
        self._vol_fn: Callable[[datetime], float] | None = vol_fn
        self._bands = bands or _MOCK_VOL_BANDS
        # 预计算 schedule 模式：转 ScheduleShrinkageProvider 的 as-of join 语义
        if volatility_schedule is not None:
            self._schedule_provider = ScheduleShrinkageProvider(
                {dt: self._vol_to_shrinkage(v, self._bands) for dt, v in volatility_schedule.items()}
            )
        else:
            self._schedule_provider = None

    def get_shrinkage(self, date: datetime) -> float:
        if self._schedule_provider is not None:
            return self._schedule_provider.get_shrinkage(date)
        # vol_fn 模式：在线计算
        try:
            vol = float(self._vol_fn(date))  # type: ignore[misc]
        except Exception as exc:
            _logger.warning("vol_fn 异常 (date=%s)，退化为 1.0: %s", date, exc)
            return 1.0
        return self._vol_to_shrinkage(vol, self._bands)

    @staticmethod
    def _vol_to_shrinkage(vol: float, bands: tuple[tuple[float, float], ...]) -> float:
        """波动率 → shrinkage 4 档映射。NaN/负值 → 1.0（保守）。"""
        if vol != vol or vol < 0:  # NaN 或负
            return 1.0
        for upper, shrinkage in bands:
            if vol < upper:
                return clamp_shrinkage(shrinkage)
        return clamp_shrinkage(bands[-1][1])


# ──────────────────────────────────────────────────────────────────────────────
# ④ RegimeDetectorShrinkageAdapter — 适配真实 RegimeDetector
# ──────────────────────────────────────────────────────────────────────────────


class RegimeDetectorShrinkageAdapter:
    """把 RegimeDetector (MOD-REGIME-001) 适配为 ShrinkageProvider。

    on-demand 调用 detector.detect() 并缓存结果。shrinkage_enabled 开关由 detector
    单一真源控制（False 时 detector 返回 value=1.0，adapter 透传）。

    Usage:
        detector = RegimeDetector(shrinkage_enabled=True)
        detector.fit(train_features)
        adapter = RegimeDetectorShrinkageAdapter(
            detector=detector,
            inputs_provider=lambda dt: (features, overlay, risk_inputs),
        )
        engine = ShrinkageBacktestEngine(provider=adapter)

    注: 回测逐日回放推荐先用 build_schedule_from_detector 离线批量预算，
        再用 ScheduleShrinkageProvider 查表（避免回测中重复跑 HMM 推断）。
        本 adapter 适合小规模/在线场景。
    """

    def __init__(
        self,
        detector: Any,
        inputs_provider: Callable[[datetime], tuple[dict, dict, dict]],
    ) -> None:
        """初始化。

        Args:
            detector: RegimeDetector 实例（已 fit 或降级均可）。
            inputs_provider: 给定日期返回 (regime_features, overlay_signals,
                risk_signal_inputs) 的 callable。
        """
        self._detector = detector
        self._inputs_provider = inputs_provider
        self._cache: dict[datetime, float] = {}

    def get_shrinkage(self, date: datetime) -> float:
        if date in self._cache:
            return self._cache[date]
        try:
            regime_features, overlay_signals, risk_inputs = self._inputs_provider(date)
            _probs, shrinkage_result = self._detector.detect(regime_features, overlay_signals, risk_inputs)
            value = clamp_shrinkage(_extract_shrinkage_value(shrinkage_result))
        except Exception as exc:
            _logger.warning(
                "RegimeDetectorShrinkageAdapter 异常 (date=%s)，退化为 1.0: %s",
                date,
                exc,
            )
            value = 1.0
        self._cache[date] = value
        return value

    @property
    def cache(self) -> dict[datetime, float]:
        """已缓存的 (date, shrinkage) 副本（归因用）。"""
        return dict(self._cache)


# ──────────────────────────────────────────────────────────────────────────────
# ⑤ DeadzoneShrinkageProvider — 死区装饰器（平稳期微抖过滤，降低 Turnover）
# ──────────────────────────────────────────────────────────────────────────────


class DeadzoneShrinkageProvider:
    """死区装饰器——Shrinkage 变化 < deadzone 不生效（保持上次实际生效值）。

    平稳期微抖被过滤（减少无效调仓/Turnover），危机期大幅调整保留（防御不迟钝）。
    装饰任意 ShrinkageProvider（Const/Schedule/Mock/RegimeDetectorAdapter），开闭原则
    不改被包装者。

    分析依据（logs/c1_repro shrinkage_schedule.csv 抖动分析，2026-08-06）：
      - 平稳期日均|Δ|=0.24% < deadzone(2%) → 过滤
      - 危机期日均|Δ|=2.16% > deadzone(2%) → 保留
      - 死区 0.02 模拟减少调仓 73%（2529→686 次）

    状态依赖：_last_effective 按日期递增累积（回测引擎 for date in sorted_dates
    保证顺序调用）。walk-forward 重跑前调 reset() 避免跨回测状态泄漏。
    deadzone=0 时退化为透传（不干预，与 inner 行为一致）。

    Args:
        inner: 被装饰的 ShrinkageProvider（任意实现 get_shrinkage 的对象）。
        deadzone: 死区阈值（默认 0.02）。raw 与 last_effective 差值 < 此值则不更新。
    """

    def __init__(self, inner: Any, deadzone: float = 0.02) -> None:
        if deadzone < 0:
            raise ShrinkageProviderError(f"deadzone 不能为负, got {deadzone}")
        self._inner = inner
        self._deadzone = float(deadzone)
        self._last_effective: float | None = None

    def get_shrinkage(self, date: datetime) -> float:
        """返回死区平滑后的 Shrinkage。

        raw 与上次实际生效值差值 < deadzone 时返回上次值（过滤微抖），
        否则更新 last_effective 并返回 raw（保留有效调整）。
        """
        raw = clamp_shrinkage(self._inner.get_shrinkage(date))
        if self._last_effective is None:
            self._last_effective = raw
            return raw
        if abs(raw - self._last_effective) < self._deadzone:
            return self._last_effective  # 变化太小，保持上次
        self._last_effective = raw
        return raw

    def reset(self) -> None:
        """重置状态（walk-forward 重跑前调用，避免跨回测状态泄漏）。"""
        self._last_effective = None

    @property
    def deadzone(self) -> float:
        """当前死区阈值。"""
        return self._deadzone

    @property
    def inner(self) -> Any:
        """被装饰的 provider（归因/调试用）。"""
        return self._inner


__all__ = [
    "ShrinkageProvider",
    "ShrinkageProviderError",
    "clamp_shrinkage",
    "build_schedule_from_results",
    "build_schedule_from_detector",
    "ConstShrinkageProvider",
    "ScheduleShrinkageProvider",
    "MockShrinkageProvider",
    "RegimeDetectorShrinkageAdapter",
    "DeadzoneShrinkageProvider",
]

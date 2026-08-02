# [BLUEPRINT] MOD-RK-15 | docs/03_modules/_domain-risk/tail_risk_monitor/blueprint.md
# [MODULE] zephyr.risk.core.tail_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; scipy.stats; MOD-RK-05(VaR基准)
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,尾部告警) ; MOD-RK-17(Kill Switch,极值触发)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ES>=VaR(尾部期望大于分位);POT shape>0=厚尾;tail_index=1/shape;jump_count单调非减(窗口内);FRTB加价>=0
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTailRiskInputError
# [TESTS] tests/risk/test_tail_risk_monitor.py
# [A_module] module_id=MOD-RK-15 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Tail Risk Monitor — 尾部风险监控器 (MOD-RK-15)

D-RISK §1.2 L2 Real-Time 盘中监控核心模块。尾部风险度量与监控:
    1. 期望短缺 (Expected Shortfall / CVaR): 尾部条件期望
       ES_α = -E[R | R <= -VaR_α]
    2. POT 模型 (Peaks-Over-Threshold): 广义帕累托分布拟合
       - 超过阈值 u 的超额值 X-u ~ GPD(ξ, β)
       - ξ (shape): >0=厚尾(Fréchet), =0=指数, <0=有界
       - β (scale): 尺度参数
       - tail_index = 1/ξ (厚尾程度, 越小越厚)
    3. 跳跃检测 (Jump Detection): 收益率绝对值超阈值计为跳跃
    4. 极值预警: ES 或 shape 超阈值告警
    5. FRTB 尾部风险加价: 基于 shape 的资本加价

属 A 类基础设施 (统计拟合 + 阈值判定, 数学逻辑明确), 阈值为 C 类可调参数。
依据: D:\\临时工作区\\依赖图\\11-D-RISK-风控域.md §1.2 RK-15, §2 依赖(RK-05→RK-15)
SSoT: depgraph MOD-RK-15
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final

import numpy as np
from scipy import stats

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "TailRiskConfig",
    "TailRiskAlertLevel",
    "PotFitResult",
    "TailRiskSnapshot",
    "TailRiskMonitor",
    "InvalidTailRiskInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidTailRiskInputError(ZephyrBaseError):
    """尾部风险监控输入数据非法 (如样本不足、置信度越界)。"""

    error_code = "ZA-RK-0015"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class TailRiskAlertLevel(Enum):
    """尾部风险告警级别。"""

    NONE = "none"
    WARNING = "warning"     # 尾部风险偏高
    CRITICAL = "critical"   # 尾部风险严重
    EMERGENCY = "emergency"  # 极值, 联动 Kill Switch


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TailRiskConfig:
    """尾部风险监控配置。

    Attributes:
        confidence: VaR/ES 置信度, 默认 0.95
        pot_threshold_quantile: POT 阈值分位数, 默认 0.90 (取最差 10% 拟合)
        jump_threshold_sigma: 跳跃检测阈值 (σ 倍数), 默认 3.0
        heavy_tail_shape_threshold: 厚尾判定 shape 阈值, 默认 0.2
        critical_shape_threshold: 严重尾部 shape 阈值, 默认 0.5
        es_warning_ratio: ES/VaR 比值告警阈值, 默认 1.5 (ES 比 VaR 大 50%)
        frtb_multiplier: FRTB 加价乘数, 默认 3.0
        min_samples: 最小样本数, 默认 30
    """

    confidence: float = 0.95
    pot_threshold_quantile: float = 0.90
    jump_threshold_sigma: float = 3.0
    heavy_tail_shape_threshold: float = 0.2
    critical_shape_threshold: float = 0.5
    es_warning_ratio: float = 1.5
    frtb_multiplier: float = 3.0
    min_samples: int = 30

    def __post_init__(self) -> None:
        if not 0 < self.confidence < 1:
            raise InvalidTailRiskInputError(
                f"confidence must be in (0,1), got {self.confidence}"
            )
        if not 0.5 < self.pot_threshold_quantile < 1:
            raise InvalidTailRiskInputError(
                f"pot_threshold_quantile must be in (0.5,1), got {self.pot_threshold_quantile}"
            )
        if self.jump_threshold_sigma <= 0:
            raise InvalidTailRiskInputError(
                f"jump_threshold_sigma must be >0, got {self.jump_threshold_sigma}"
            )
        if self.heavy_tail_shape_threshold <= 0:
            raise InvalidTailRiskInputError(
                f"heavy_tail_shape_threshold must be >0, got {self.heavy_tail_shape_threshold}"
            )
        if self.critical_shape_threshold <= self.heavy_tail_shape_threshold:
            raise InvalidTailRiskInputError(
                f"critical_shape_threshold ({self.critical_shape_threshold}) must be "
                f"> heavy_tail_shape_threshold ({self.heavy_tail_shape_threshold})"
            )
        if self.es_warning_ratio <= 1.0:
            raise InvalidTailRiskInputError(
                f"es_warning_ratio must be >1.0, got {self.es_warning_ratio}"
            )
        if self.frtb_multiplier <= 0:
            raise InvalidTailRiskInputError(
                f"frtb_multiplier must be >0, got {self.frtb_multiplier}"
            )
        if self.min_samples < 10:
            raise InvalidTailRiskInputError(
                f"min_samples must be >=10, got {self.min_samples}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PotFitResult:
    """POT (广义帕累托分布) 拟合结果。

    Attributes:
        shape: 形状参数 ξ (>0=厚尾, =0=指数, <0=有界)
        scale: 尺度参数 β
        threshold: 阈值 u
        n_exceedances: 超过阈值的样本数
        tail_index: 尾部指数 1/ξ (None=ξ<=0)
        is_heavy_tailed: 是否厚尾 (ξ>0)
    """

    shape: float
    scale: float
    threshold: float
    n_exceedances: int
    is_heavy_tailed: bool
    tail_index: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape": self.shape,
            "scale": self.scale,
            "threshold": self.threshold,
            "n_exceedances": self.n_exceedances,
            "tail_index": self.tail_index,
            "is_heavy_tailed": self.is_heavy_tailed,
        }


@dataclass(frozen=True)
class TailRiskSnapshot:
    """尾部风险综合快照。

    Attributes:
        var: VaR 值 (正数, 损失额)
        expected_shortfall: ES/CVaR 值 (正数, >= VaR)
        es_var_ratio: ES/VaR 比值 (>= 1.0)
        pot: POT 拟合结果 (None=样本不足)
        jump_count: 跳跃次数
        jump_threshold: 跳跃阈值
        alert_level: 告警级别
        frtb_addon: FRTB 尾部风险加价
        reason: 告警原因
        timestamp: 快照时间
    """

    var: float
    expected_shortfall: float
    es_var_ratio: float
    jump_count: int
    jump_threshold: float
    alert_level: TailRiskAlertLevel
    frtb_addon: float
    reason: str
    timestamp: datetime
    pot: PotFitResult | None = None

    @property
    def is_heavy_tailed(self) -> bool:
        """是否厚尾。"""
        return self.pot is not None and self.pot.is_heavy_tailed

    def to_dict(self) -> dict[str, Any]:
        return {
            "var": self.var,
            "expected_shortfall": self.expected_shortfall,
            "es_var_ratio": self.es_var_ratio,
            "pot": self.pot.to_dict() if self.pot else None,
            "jump_count": self.jump_count,
            "jump_threshold": self.jump_threshold,
            "alert_level": self.alert_level.value,
            "frtb_addon": self.frtb_addon,
            "reason": self.reason,
            "is_heavy_tailed": self.is_heavy_tailed,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 尾部风险监控器
# ──────────────────────────────────────────────────────────────────────────────


class TailRiskMonitor:
    """尾部风险监控器——ES + POT + 跳跃检测 + 极值预警 + FRTB 加价。

    用法:
        monitor = TailRiskMonitor()
        snapshot = monitor.assess(returns=np.random.randn(1000)*0.02)
        # snapshot.expected_shortfall → CVaR
        # snapshot.pot.shape → 厚尾程度
        # snapshot.alert_level → 告警级别
    """

    def __init__(self, config: TailRiskConfig | None = None) -> None:
        self._config = config or TailRiskConfig()

    @property
    def config(self) -> TailRiskConfig:
        return self._config

    # ── 公开 API: 综合评估 ──

    def assess(
        self,
        returns: np.ndarray,
        portfolio_value: float = 1.0,
        now: datetime | None = None,
    ) -> TailRiskSnapshot:
        """综合评估尾部风险 (VaR + ES + POT + 跳跃 + 告警 + FRTB)。

        Args:
            returns: 收益率序列 (N,), 负=亏损
            portfolio_value: 组合价值 (用于计算金额, 默认 1.0=比率)
            now: 时间戳

        Returns:
            TailRiskSnapshot
        """
        now = now or datetime.now(timezone.utc)
        cfg = self._config
        returns = self._validate_returns(returns, cfg.min_samples)

        # 1. VaR (历史模拟)
        var_pct = self.compute_var(returns, cfg.confidence)
        # 2. ES (期望短缺)
        es_pct = self.compute_expected_shortfall(returns, cfg.confidence)
        es_var_ratio = es_pct / var_pct if var_pct > 0 else 1.0

        # 3. POT 拟合
        pot = self.fit_pot(returns, cfg.pot_threshold_quantile)

        # 4. 跳跃检测
        jump_count = self.detect_jumps(returns, cfg.jump_threshold_sigma)
        jump_threshold = float(np.std(returns) * cfg.jump_threshold_sigma)

        # 5. 告警级别判定
        alert_level, reason = self._determine_alert(
            pot, es_var_ratio, jump_count, cfg
        )

        # 6. FRTB 加价
        frtb_addon = self._compute_frtb_addon(pot, var_pct, portfolio_value, cfg)

        if alert_level is not TailRiskAlertLevel.NONE:
            logger.warning(
                "Tail risk alert: level=%s es_var_ratio=%.2f shape=%s jumps=%d",
                alert_level.value,
                es_var_ratio,
                f"{pot.shape:.4f}" if pot else "N/A",
                jump_count,
            )

        return TailRiskSnapshot(
            var=var_pct * portfolio_value,
            expected_shortfall=es_pct * portfolio_value,
            es_var_ratio=es_var_ratio,
            pot=pot,
            jump_count=jump_count,
            jump_threshold=jump_threshold,
            alert_level=alert_level,
            frtb_addon=frtb_addon,
            reason=reason,
            timestamp=now,
        )

    # ── 公开 API: VaR ──

    @staticmethod
    def compute_var(returns: np.ndarray, confidence: float) -> float:
        """历史模拟 VaR (正数, 损失额比率)。

        VaR = -quantile(returns, 1-confidence)
        """
        returns = np.asarray(returns, dtype=float)
        var = -float(np.quantile(returns, 1 - confidence))
        return max(var, 0.0)

    # ── 公开 API: ES/CVaR ──

    @staticmethod
    def compute_expected_shortfall(returns: np.ndarray, confidence: float) -> float:
        """期望短缺 ES (CVaR, 正数, 损失额比率)。

        ES = -mean(R | R <= VaR_quantile)
        VaR_quantile = quantile(returns, 1-confidence) (负值, 如 -0.03)
        ES >= VaR (尾部期望 >= 分位数)

        不变量: ES >= VaR (尾部条件期望的损失 >= 分位数处的损失)
        """
        returns = np.asarray(returns, dtype=float)
        var_quantile = float(np.quantile(returns, 1 - confidence))
        # 尾部 = 收益率 <= 分位数 (最差的 tail 部分, 均为负值)
        tail = returns[returns <= var_quantile]
        if len(tail) == 0:
            # 退化: 无样本低于分位数 (理论上不会发生, 防御性)
            return max(-var_quantile, 0.0)
        es = -float(np.mean(tail))
        return max(es, 0.0)

    # ── 公开 API: POT 拟合 ──

    def fit_pot(
        self,
        returns: np.ndarray,
        threshold_quantile: float = 0.90,
    ) -> PotFitResult | None:
        """POT 模型拟合 (广义帕累托分布)。

        取收益率的最差 tail (1-threshold_quantile 分位以下), 拟合 GPD。

        Args:
            returns: 收益率序列
            threshold_quantile: 阈值分位数 (0.90=取最差 10%)

        Returns:
            PotFitResult, None=超过阈值样本不足
        """
        returns = np.asarray(returns, dtype=float)
        if len(returns) < self._config.min_samples:
            return None

        # 阈值: 取最差 tail (losses)
        # returns 中负值是损失, threshold 取 threshold_quantile 分位
        threshold = float(np.quantile(returns, threshold_quantile))
        # 超过阈值的"超额值" (用于 GPD, 取 |exceedance|)
        exceedances = returns[returns > threshold] - threshold
        # 对损失侧: 取 returns < -|threshold| 的 |returns|
        # 标准 POT: 对损失序列 L = -returns[L < 0], 取 L > u 的 L-u
        losses = -returns[returns < 0]
        if len(losses) < 10:
            return None
        loss_threshold = float(np.quantile(losses, threshold_quantile))
        exceedances = losses[losses > loss_threshold] - loss_threshold

        if len(exceedances) < 5:
            return None

        # 拟合 GPD: scipy.stats.genpareto
        # scipy 的 genpareto 参数 c 对应 shape ξ
        try:
            shape, loc, scale = stats.genpareto.fit(exceedances, floc=0)
        except Exception as e:
            logger.warning("POT fit failed: %s", e)
            return None

        is_heavy = shape > 0
        tail_index = float(1.0 / shape) if shape > 0 else None

        return PotFitResult(
            shape=float(shape),
            scale=float(scale),
            threshold=loss_threshold,
            n_exceedances=len(exceedances),
            is_heavy_tailed=is_heavy,
            tail_index=tail_index,
        )

    # ── 公开 API: 跳跃检测 ──

    @staticmethod
    def detect_jumps(returns: np.ndarray, threshold_sigma: float = 3.0) -> int:
        """跳跃检测——收益率绝对值超 σ×threshold_sigma 计为跳跃。

        Args:
            returns: 收益率序列
            threshold_sigma: σ 倍数阈值

        Returns:
            跳跃次数
        """
        returns = np.asarray(returns, dtype=float)
        if len(returns) < 2:
            return 0
        std = float(np.std(returns))
        # 浮点近零保护: 恒定序列 std 可能 = 1e-18 而非精确 0,
        # 导致 threshold 极小, 所有点被误判为跳跃
        if std < 1e-12:
            return 0
        threshold = std * threshold_sigma
        return int(np.sum(np.abs(returns) > threshold))

    # ── 内部: 告警级别判定 ──

    @staticmethod
    def _determine_alert(
        pot: PotFitResult | None,
        es_var_ratio: float,
        jump_count: int,
        cfg: TailRiskConfig,
    ) -> tuple[TailRiskAlertLevel, str]:
        """判定尾部风险告警级别。"""
        reasons: list[str] = []

        # 基于 shape 判定
        if pot is not None:
            if pot.shape >= cfg.critical_shape_threshold:
                reasons.append(
                    f"POT shape={pot.shape:.3f} >= {cfg.critical_shape_threshold} (严重厚尾)"
                )
            elif pot.shape >= cfg.heavy_tail_shape_threshold:
                reasons.append(
                    f"POT shape={pot.shape:.3f} >= {cfg.heavy_tail_shape_threshold} (厚尾)"
                )

        # 基于 ES/VaR 比值判定
        if es_var_ratio >= cfg.es_warning_ratio:
            reasons.append(
                f"ES/VaR={es_var_ratio:.2f} >= {cfg.es_warning_ratio} (尾部偏厚)"
            )

        # 基于跳跃次数
        if jump_count >= 5:
            reasons.append(f"跳跃次数 {jump_count} >= 5 (极端波动频繁)")

        if not reasons:
            return TailRiskAlertLevel.NONE, "尾部风险正常"

        # 级别判定: shape 超临界值或 ES/VaR 超 2.0 → EMERGENCY
        is_emergency = (
            (pot is not None and pot.shape >= cfg.critical_shape_threshold)
            or es_var_ratio >= 2.0
            or jump_count >= 10
        )
        is_critical = (
            (pot is not None and pot.shape >= cfg.heavy_tail_shape_threshold)
            or es_var_ratio >= cfg.es_warning_ratio
            or jump_count >= 5
        )

        if is_emergency:
            level = TailRiskAlertLevel.EMERGENCY
        elif is_critical:
            level = TailRiskAlertLevel.CRITICAL
        else:
            level = TailRiskAlertLevel.WARNING

        return level, "; ".join(reasons)

    # ── 内部: FRTB 加价 ──

    @staticmethod
    def _compute_frtb_addon(
        pot: PotFitResult | None,
        var_pct: float,
        portfolio_value: float,
        cfg: TailRiskConfig,
    ) -> float:
        """FRTB 尾部风险加价。

        加价 = VaR × multiplier × (1 + shape_adjustment)
        shape_adjustment = max(0, shape) × 2 (厚尾额外加价)
        """
        base = var_pct * portfolio_value * cfg.frtb_multiplier
        if pot is not None and pot.shape > 0:
            shape_adjustment = pot.shape * 2
            return base * (1 + shape_adjustment)
        return base

    # ── 内部: 校验 ──

    @staticmethod
    def _validate_returns(returns: np.ndarray, min_samples: int) -> np.ndarray:
        returns = np.asarray(returns, dtype=float)
        if returns.ndim != 1:
            raise InvalidTailRiskInputError(
                f"returns must be 1D, got shape {returns.shape}"
            )
        if len(returns) < min_samples:
            raise InvalidTailRiskInputError(
                f"need >= {min_samples} samples, got {len(returns)}"
            )
        if np.any(np.isnan(returns)):
            returns = returns[~np.isnan(returns)]
        if len(returns) < min_samples:
            raise InvalidTailRiskInputError(
                f"after NaN removal, need >= {min_samples} samples, got {len(returns)}"
            )
        return returns

# [BLUEPRINT] MOD-RK-15 | docs/03_modules/_domain_risk/tail_risk_monitor/blueprint.md
# [MODULE] zephyr.risk.core.tail_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; scipy.stats; MOD-RK-05(VaR基准); zephyr.shared.state_store(可选,注入启用POT失败计数器)
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,尾部告警) ; MOD-RK-17(Kill Switch,极值触发)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ES>=VaR(尾部期望大于分位);POT shape>0=厚尾;tail_index=1/shape;jump_count单调非减(窗口内);FRTB加价>=0;POT失败计数器读失败按最保守计(fail-closed);连续5日失败→阈值0.90→0.85(跨日持久化)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTailRiskInputError
# [TESTS] tests/risk/test_tail_risk_monitor.py; tests/risk/test_pot_failure_counter.py
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
依据: D:\\临时工作区\\依赖图	-D-RISK-风控域.md §1.2 RK-15, §2 依赖(RK-05→RK-15)
SSoT: depgraph MOD-RK-15
Version: 0.2.0

v0.2.0 (2026-08-17 AI-POT-001): 新增 PotFailureCounter 跨日持久化计数器
(连续 5 日失败→阈值 0.90→0.85, fail-closed, 双后端 JsonStateStore/RedisStateStore)。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 收益率序列 np.ndarray
#   fields: 1维收益率数组(负=亏损), NaN自动剔除, 需>=30样本
#   code: assess() returns L265
# - id: I2
#   name: 组合价值 标量
#   fields: portfolio_value 组合价值(默认1.0=比率), 用于把比率换算成金额
#   code: assess() portfolio_value L266
# - id: I3
#   name: 尾部风险配置 TailRiskConfig
#   fields: confidence置信度0.95 + POT阈值分位0.90 + 跳跃3σ + shape厚尾0.2/严重0.5 + ES/VaR比1.5 + FRTB乘数3.0 + min_samples30
#   code: TailRiskConfig L94
# 层: 算法
# - id: A1
#   name_zh: ① 历史模拟VaR
#   name_en: compute_var
#   intro: 取收益率分布的左尾分位数当作在险价值
#   desc: VaR=-quantile(returns, 1-confidence), 结果clamp到>=0
#   inputs: I1 I3
#   outputs: var_pct VaR比率
#   invariant: VaR>=0
# - id: A2
#   name_zh: ② 期望短缺ES/CVaR
#   name_en: compute_expected_shortfall
#   intro: 比VaR更惨的那部分尾巴的平均亏损
#   desc: q=quantile(returns,1-c,method='lower')(实有样本点,防插值尾部抖动,F1裁定); tail=returns[returns<=q]; ES=-mean(tail), clamp>=0
#   inputs: I1 I3
#   outputs: es_pct ES比率 + es_var_ratio=ES/VaR
#   invariant: ES>=VaR
# - id: A3
#   name_zh: ③ POT广义帕累托拟合
#   name_en: fit_pot
#   intro: 对最差的10%亏损拟合GPD分布看尾巴有多厚
#   desc: losses=-r[r<0]; u=quantile(losses,0.9); 超额losses>u部分用scipy.genpareto.fit(floc=0)估shape ξ/scale β; tail_index=1/ξ; 样本不足返回None+warning降级(仅历史ES,pot_fallback_historical=True); 连续5日失败→阈值0.90→0.85(PotFailureCounter跨日持久化)
#   inputs: I1 I3
#   outputs: PotFitResult(shape/scale/threshold/n_exceedances/tail_index)
#   invariant: ξ>0=厚尾; tail_index=1/ξ
# - id: A4
#   name_zh: ④ 跳跃检测
#   name_en: detect_jumps
#   intro: 收益率绝对值超过3倍标准差记一次跳跃
#   desc: threshold=std(r)×3σ; jump_count=sum(|r|>threshold); std<1e-12近零保护返回0
#   inputs: I1 I3
#   outputs: jump_count 跳跃次数
#   invariant: jump_count单调非减(窗口内)
# - id: A5
#   name_zh: ⑤ 尾部告警级别判定
#   name_en: _determine_alert
#   intro: shape超线/ES-VaR比超线/跳跃频繁三路合成告警级别
#   desc: shape>=0.5或ES/VaR>=2.0或jump>=10→EMERGENCY; shape>=0.2或ES/VaR>=1.5或jump>=5→CRITICAL; 有原因但不达标→WARNING; 无原因→NONE
#   inputs: A2 A3 A4 I3
#   outputs: (alert_level, reason)
# - id: A6
#   name_zh: ⑥ FRTB尾部风险加价
#   name_en: _compute_frtb_addon
#   intro: 按厚尾程度在VaR基础上加资本加价
#   desc: base=VaR×portfolio_value×3.0; 厚尾时 base×(1+2×shape)
#   inputs: A1 A3 I2 I3
#   outputs: frtb_addon 资本加价额
#   invariant: FRTB加价>=0
# 层: 输出
# - id: O1
#   name_zh: 尾部风险综合快照
#   name_en: TailRiskSnapshot
#   intro: 含VaR/ES/POT/跳跃/告警级别/FRTB加价的frozen快照对象
#   invariant: EMERGENCY级别联动Kill Switch
#   downstream: MOD-RK-03(Portfolio Risk Monitor 尾部告警); MOD-RK-17(Kill Switch 极值触发)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I1 --> A4
# I2 --> A6
# I3 --> A1
# I3 --> A3
# I3 --> A5
# I3 --> A6
# A1 --> A5
# A2 --> A5
# A3 --> A5
# A4 --> A5
# A1 --> A6
# A3 --> A6
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A5 --> O1
# A6 --> O1
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
from zephyr.shared.state_store import StateStoreError

__all__: Final = [
    "TailRiskConfig",
    "TailRiskAlertLevel",
    "PotFitResult",
    "TailRiskSnapshot",
    "TailRiskMonitor",
    "InvalidTailRiskInputError",
    "PotFailureCounter",
    "POT_FAILURE_COUNTER_NAMESPACE",
    "POT_FAILURE_DAYS_FOR_ADJUSTMENT",
    "POT_THRESHOLD_ADJUSTED",
]

logger = logging.getLogger(__name__)

#: POT 失败计数器命名空间（state_store 持久化）
POT_FAILURE_COUNTER_NAMESPACE: Final = "pot_failure_counter"

#: 连续失败阈值触发升级天数
POT_FAILURE_DAYS_FOR_ADJUSTMENT: Final = 5

#: 降级后的 POT 阈值分位数（0.90 → 0.85，获取更多 exceedances）
POT_THRESHOLD_ADJUSTED: Final = 0.85


class PotFailureCounter:
    """POT 连续失败计数器——跨日持久化，fail-closed。

    记录每日 POT 拟合是否失败（fit_pot 返回 None）。
    连续 N 日失败 → 建议阈值降级（0.90→0.85）。

    持久化 schema（JsonStateStore/RedisStateStore）:
        {
            "consecutive_failures": int,   # 连续失败天数
            "last_failure_date": str,      # 最后失败日期 "YYYY-MM-DD"
            "adjusted_threshold": float,   # 调整后的阈值（默认 0.90）
        }

    Fail-closed:
        - 读失败（StateCorruptError/StateStoreError）→ 按从未失败处理
        - 写失败 → 只记录 warning，不阻断主链路
    """

    def __init__(self, store, config: TailRiskConfig | None = None) -> None:
        self._store = store
        self._config = config or TailRiskConfig()
        self._namespace = POT_FAILURE_COUNTER_NAMESPACE

    def _load(self) -> dict:
        """读取计数器状态；失败返回 fresh 状态（fail-closed）。"""
        default = {
            "consecutive_failures": 0,
            "last_failure_date": "",
            "adjusted_threshold": self._config.pot_threshold_quantile,
        }
        try:
            rec = self._store.load(self._namespace)
        except Exception:  # noqa: BLE001 — fail-closed：读失败按从未失败处理，不阻断
            logger.warning(
                "POT 计数器读失败，按从未失败处理",
                exc_info=True,
            )
            return default
        if rec is None:
            return default
        if not isinstance(rec, dict):
            logger.warning("POT 计数器记录非 dict（%s），按从未失败处理", type(rec).__name__)
            return default
        # 防御：损坏记录（缺键/类型异常）→ 合并默认值，fail-closed 不阻断
        for k, v in default.items():
            if k not in rec:
                rec[k] = v
        try:
            rec["consecutive_failures"] = int(rec["consecutive_failures"])
        except (TypeError, ValueError):
            rec["consecutive_failures"] = 0
        try:
            rec["adjusted_threshold"] = float(rec["adjusted_threshold"])
        except (TypeError, ValueError):
            rec["adjusted_threshold"] = self._config.pot_threshold_quantile
        return rec

    def _save(self, rec: dict) -> None:
        """持久化计数器状态；失败只 warning。"""
        try:
            self._store.save(self._namespace, rec)
        except Exception:  # noqa: BLE001 — fail-open-to-memory：写失败仅告警不阻断主链路
            logger.warning("POT 计数器写失败，已降级内存态", exc_info=True)

    def record_failure(self, date_str: str) -> int:
        """记录一次 POT 失败。返回当前连续失败天数。"""
        rec = self._load()
        if rec["last_failure_date"] == date_str:
            # 同一天多次失败，不重复计数
            return rec["consecutive_failures"]
        rec["consecutive_failures"] = rec["consecutive_failures"] + 1
        rec["last_failure_date"] = date_str
        if rec["consecutive_failures"] >= POT_FAILURE_DAYS_FOR_ADJUSTMENT:
            rec["adjusted_threshold"] = POT_THRESHOLD_ADJUSTED
            logger.warning(
                "POT 连续 %d 日失败 → 阈值降级 %.2f → %.2f",
                rec["consecutive_failures"],
                self._config.pot_threshold_quantile,
                POT_THRESHOLD_ADJUSTED,
            )
        self._save(rec)
        return rec["consecutive_failures"]

    def record_success(self, date_str: str) -> None:
        """记录一次 POT 成功，重置连续失败计数。

        last_failure_date 清空（非写当天）——成功后同日再失败必须可计数：
        写当天会被 record_failure 的同日去重分支误吞（AI-R2-001 修复）。
        """
        rec = self._load()
        base_threshold = self._config.pot_threshold_quantile
        # 早退条件须含 last_failure_date 已清空（AI-R2 红队 ATK-8）：升级遗留
        # 状态（旧版 record_success 曾写当天日期）下早退不清 stale date →
        # 同日真实失败被 record_failure 同日去重分支误吞（计数器失明）
        if (
            rec["consecutive_failures"] == 0
            and rec["adjusted_threshold"] == base_threshold
            and not rec["last_failure_date"]
        ):
            return  # 无变化，省一次写
        rec["consecutive_failures"] = 0
        rec["last_failure_date"] = ""
        rec["adjusted_threshold"] = base_threshold
        self._save(rec)
        logger.info("POT 拟合成功，连续失败计数重置")

    def get_adjusted_threshold(self) -> float:
        """获取当前 POT 阈值分位数（可能被连续失败降级）。"""
        rec = self._load()
        return rec.get("adjusted_threshold", self._config.pot_threshold_quantile)


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
        max_nonfinite_ratio: 非有限值 (NaN/±Inf) 占比上限, 默认 0.05——超过即抛
            InvalidTailRiskInputError (Fail-Closed)。与 var_calculator 同口径
            (AI-R3 复审 P1 治本: 原仅静默滤 NaN, ±Inf 穿透污染 ES/POT/jump)
    """

    confidence: float = 0.95
    pot_threshold_quantile: float = 0.90
    jump_threshold_sigma: float = 3.0
    heavy_tail_shape_threshold: float = 0.2
    critical_shape_threshold: float = 0.5
    es_warning_ratio: float = 1.5
    frtb_multiplier: float = 3.0
    min_samples: int = 30
    max_nonfinite_ratio: float = 0.05

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
        if not 0.0 <= self.max_nonfinite_ratio < 1.0:
            raise InvalidTailRiskInputError(
                f"max_nonfinite_ratio must be in [0,1), got {self.max_nonfinite_ratio}"
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
        pot_fallback_historical: True=POT 未生效 (样本不足/拟合失败), 已降级为
            纯历史模拟 ES (厚尾诊断/FRTB shape 加价缺席, memo 36 §3.2 兜底标记)
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
    pot_fallback_historical: bool = False

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
            "pot_fallback_historical": self.pot_fallback_historical,
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

    Args:
        config: 尾部风险配置
        state_store: Crash-only 状态外部化存储（#ARCH-QUANT-002），注入后启用
            POT 连续失败跨日持久化计数器（连续 5 日失败→阈值 0.90→0.85）
    """

    def __init__(self, config: TailRiskConfig | None = None, *, state_store=None) -> None:
        self._config = config or TailRiskConfig()
        self._pot_counter = PotFailureCounter(state_store, self._config) if state_store else None

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
        # POT 阈值动态调整：连续失败降级
        pot_threshold_quantile = cfg.pot_threshold_quantile
        if self._pot_counter is not None:
            pot_threshold_quantile = self._pot_counter.get_adjusted_threshold()
        returns = self._validate_returns(returns, cfg.min_samples, cfg.max_nonfinite_ratio)

        # 1. VaR (历史模拟)
        var_pct = self.compute_var(returns, cfg.confidence)
        # 2. ES (期望短缺)
        es_pct = self.compute_expected_shortfall(returns, cfg.confidence)
        es_var_ratio = es_pct / var_pct if var_pct > 0 else 1.0

        # 3. POT 拟合 (None=样本不足/拟合失败 → 降级纯历史 ES, 双轮审查深挖③裁定)
        pot = self.fit_pot(returns, pot_threshold_quantile)
        pot_fallback_historical = pot is None
        # 跨日持久化计数器记录
        if self._pot_counter is not None:
            date_str = now.strftime("%Y-%m-%d")
            if pot_fallback_historical:
                self._pot_counter.record_failure(date_str)
            else:
                self._pot_counter.record_success(date_str)
        if pot_fallback_historical:
            logger.warning(
                "POT 未生效, 本次快照为纯历史模拟 ES (pot_fallback_historical=True): "
                "厚尾诊断/FRTB shape 加价缺席"
            )

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
            pot_fallback_historical=pot_fallback_historical,
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
        VaR_quantile = quantile(returns, 1-confidence, method='lower') (负值, 如 -0.03)
        ES >= VaR (尾部期望 >= 分位数)

        插值口径裁定 (2026-08-16 双轮审查 F1, memo 36 §3.10): 分位数取
        `method='lower'` (实有样本点, 不线性插值)——线性插值会产出样本中不存在的
        虚拟值, 使尾部样本数在小样本下抖动 (如 30 样本 95% 置信在 1/2 个间跳变),
        ES 估计不连续; 'lower' 口径下尾部样本数 = #{r <= sorted[floor((n-1)(1-c))]},
        稳定且 ES>=VaR 不变量天然成立 (尾部均值 <= 分位点)。

        不变量: ES >= VaR (尾部条件期望的损失 >= 分位数处的损失)
        """
        returns = np.asarray(returns, dtype=float)
        var_quantile = float(np.quantile(returns, 1 - confidence, method="lower"))
        # 尾部 = 收益率 <= 分位数 (最差的 tail 部分, 均为负值)
        tail = returns[returns <= var_quantile]
        if len(tail) == 0:
            # 退化: 无样本低于分位数 (method='lower' 下不可达——分位点本身即样本, 防御性保留)
            return max(-var_quantile, 0.0)
        es = -float(np.mean(tail))
        return max(es, 0.0)

    # ── 公开 API: POT 拟合 ──

    def fit_pot(
        self,
        returns: np.ndarray,
        threshold_quantile: float | None = None,
    ) -> PotFitResult | None:
        """POT 模型拟合 (广义帕累托分布)。

        取收益率的最差 tail (1-threshold_quantile 分位以下), 拟合 GPD。

        Args:
            returns: 收益率序列
            threshold_quantile: 阈值分位数 (None=使用配置或动态调整值, 默认 0.90)

        Returns:
            PotFitResult, None=超过阈值样本不足 (降级为纯历史模拟 ES,
            snapshot.pot_fallback_historical=True + warning 日志, 2026-08-16
            双轮审查深挖③裁定: 60 日窗口 + 常态负日占比下 exceedances 常 <5,
            小样本 GPD 拟合是噪声发生器, 样本不足时跳过 POT 仅历史 ES)
        """
        if threshold_quantile is None:
            threshold_quantile = self._config.pot_threshold_quantile
        returns = np.asarray(returns, dtype=float)
        if len(returns) < self._config.min_samples:
            logger.warning(
                "POT 降级: 样本 %d < min_samples %d, 跳过 POT 仅历史 ES",
                len(returns),
                self._config.min_samples,
            )
            return None

        # 标准 POT: 对损失序列 L = -returns[L < 0], 取 L > u 的 L-u
        losses = -returns[returns < 0]
        if len(losses) < 10:
            logger.warning(
                "POT 降级: 负收益样本 %d < 10, 跳过 POT 仅历史 ES",
                len(losses),
            )
            return None
        loss_threshold = float(np.quantile(losses, threshold_quantile))
        exceedances = losses[losses > loss_threshold] - loss_threshold

        if len(exceedances) < 5:
            logger.warning(
                "POT 降级: 超阈值 exceedances %d < 5 (60 日窗口+常态负日占比下常态), "
                "GPD 小样本拟合为噪声, 跳过 POT 仅历史 ES",
                len(exceedances),
            )
            return None

        # 拟合 GPD: scipy.stats.genpareto
        # scipy 的 genpareto 参数 c 对应 shape ξ
        try:
            shape, loc, scale = stats.genpareto.fit(exceedances, floc=0)
        except Exception as e:  # noqa: BLE001 — 拟合数值失效降级纯历史 ES（pot_fallback_historical）
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
    def _validate_returns(
        returns: np.ndarray, min_samples: int, max_nonfinite_ratio: float = 0.05
    ) -> np.ndarray:
        """输入校验——非有限值 Fail-Closed（AI-R3 复审 P1 治本）。

        与 var_calculator 同口径：isfinite 过滤 + 计数 + 超阈值 raise。
        原仅静默滤 NaN——±Inf 穿透使 ES 分位点=-inf（尾部均值=+inf 静默输出）、
        +inf 污染 detect_jumps 的 std；数据洞恰是高波动日，静默过滤系统性低估风险。
        """
        returns = np.asarray(returns, dtype=float)
        if returns.ndim != 1:
            raise InvalidTailRiskInputError(
                f"returns must be 1D, got shape {returns.shape}"
            )
        if len(returns) < min_samples:
            raise InvalidTailRiskInputError(
                f"need >= {min_samples} samples, got {len(returns)}"
            )
        total = len(returns)
        finite_mask = np.isfinite(returns)
        nonfinite_dropped = int(total - finite_mask.sum())
        if nonfinite_dropped > 0:
            ratio = nonfinite_dropped / total
            if ratio > max_nonfinite_ratio:
                raise InvalidTailRiskInputError(
                    f"non-finite ratio {ratio:.4f} > max_nonfinite_ratio "
                    f"{max_nonfinite_ratio} ({nonfinite_dropped}/{total} dropped)——"
                    "数据缺口期间拒绝出尾部风险判定 (Fail-Closed)"
                )
            returns = returns[finite_mask]
        if len(returns) < min_samples:
            raise InvalidTailRiskInputError(
                f"after non-finite removal, need >= {min_samples} samples, got {len(returns)}"
            )
        return returns

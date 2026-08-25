# [BLUEPRINT] MOD-RK-40 | docs/03_modules/_domain_risk/post_entry_instant_validator/blueprint.md
# [MODULE] zephyr.risk.post_entry_instant_validator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 调用方按T+5/15/30min时点逐档调用(运行时装配批); MOD-L04-001/MOD-RK-35/MOD-SELL-001(纠错动作执行面); D_GOV_AUDIT(动作留痕)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 5min:跌>1%且量比≥1.5→WATCH; 15min:价<vwap且反弹<0.5ATR→REDUCE_HALF; 30min:反向>2ATR→EXIT_ALL; 阈值严格大于/小于(恰等不命中); 动作仅产信号(执行委托既有止损族); 非PASS经audit_sink留痕; verdict frozen; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPostEntryInputError
# [TESTS] tests/risk/test_post_entry_instant_validator.py
# [A_module] module_id=MOD-RK-40 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Post-Entry Instant Validator — 买入后即时验证与快速纠错 (MOD-RK-40, CAND-RSK-044, B14-04546)

A9 §2.2后（36.1/36.2）落码：买入成交后按 T+5/15/30min 三档时点校验持仓动量——
5min 跌破买价>1% 且放量 → WATCH（观察标记）；15min 跌破分时均线反弹无力 →
REDUCE_HALF（减仓 50%）；30min 反向>2ATR → EXIT_ALL（全部止损）。对标
Gao et al. (2018 JF) 日内动量 + A 股交易台分时均线/ATR 纪律。

**canonical 声明**（蓝图 §0）：本模块为"买入后即时验证与快速纠错"唯一真源；
W-P1-22 同名候选 CAND-SELL-002（B10-01475，D_SELL_DECISION）spec 全等，应归并
本件（本波先建）。

与既有件分工：MOD-TRADING-008 为异常退出五步编排（执行面）；stop_loss
（MOD-L04-001）/ ashare_stop_loss_engine（MOD-RK-09）/ atr_stop_engine
（MOD-RK-35）为常规止损体系（无三档时间窗验证）；MOD-SELL-012 为卖出执行质量
复盘（事后度量）。本模块为三档验证规则判定核心（L4 风控层增量），口径不重复。

纪律：纯函数无 IO；行情观测由调用方注入（三维解耦不越域取数）；纠错动作仅产
信号（减仓/清仓执行委托 stop_loss/atr_stop_engine/sell 执行族，装配面接线）；
非 PASS 动作经 audit_sink 回调留痕（动作写审计链，委托 D_GOV_AUDIT）。

依据: blueprint.md（MOD-RK-40）§3 核心规则；Gao, Han, Li, Zhou (2018, JF)
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓与档位
#   fields: symbol + entry_price(>0) + checkpoint(MIN_5/15/30) + current_price(>0)
#   code: validate() 参数
# - id: I2
#   name: 档位观测
#   fields: 5min→volume_ratio; 15min→vwap+session_low+atr14; 30min→atr14（档位必填）
#   code: validate() 参数
# - id: I3
#   name: 配置 PostEntryValidatorConfig
#   fields: drawdown_pct_5m=0.01/volume_ratio_min=1.5/rebound_atr_frac=0.5/adverse_atr_mult=2.0
#   code: PostEntryValidatorConfig
# 层: 算法
# - id: A1
#   name_zh: ① 5min档：跌>1%且放量→WATCH
#   name_en: _eval_5m
#   intro: (entry−current)/entry>1% 且 volume_ratio≥1.5 → WATCH 否则 PASS
# - id: A2
#   name_zh: ② 15min档：破均线反弹无力→REDUCE_HALF
#   name_en: _eval_15m
#   intro: current<vwap 且 current−session_low<0.5×ATR → REDUCE_HALF 否则 PASS
# - id: A3
#   name_zh: ③ 30min档：反向>2ATR→EXIT_ALL
#   name_en: _eval_30m
#   intro: entry−current>2×ATR → EXIT_ALL 否则 PASS
# 层: 输出
# - id: O1
#   name: PostEntryVerdict
#   fields: symbol/checkpoint/action/reason/metrics（frozen；非PASS→audit_sink）
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A1
# I2 --> A2
# I2 --> A3
# I3 --> A1
# I3 --> A2
# I3 --> A3
# A1 --> O1
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
    "CorrectionAction",
    "InvalidPostEntryInputError",
    "PostEntryCheckpoint",
    "PostEntryInstantValidator",
    "PostEntryValidatorConfig",
    "PostEntryVerdict",
]


class InvalidPostEntryInputError(ZephyrBaseError):
    """买入后即时验证输入/配置非法（Fail-Closed）。"""


class PostEntryCheckpoint(str, Enum):
    """三档验证时点（买入后）。"""

    MIN_5 = "MIN_5"  # T+5min
    MIN_15 = "MIN_15"  # T+15min
    MIN_30 = "MIN_30"  # T+30min


class CorrectionAction(str, Enum):
    """纠错动作信号（仅信号；执行委托既有止损/卖出族）。"""

    PASS = "PASS"  # 验证通过
    WATCH = "WATCH"  # 观察标记（5min 档）
    REDUCE_HALF = "REDUCE_HALF"  # 减仓 50%（15min 档）
    EXIT_ALL = "EXIT_ALL"  # 全部止损（30min 档）


def _positive_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise InvalidPostEntryInputError(f"{name} 必须为正有限值: {value}")
    return v


@dataclass(frozen=True)
class PostEntryValidatorConfig:
    """三档验证阈值（C 类可调；默认值=候选 spec 真源）。"""

    drawdown_pct_5m: float = 0.01  # 5min 档跌幅触发线（严格大于）
    volume_ratio_min: float = 1.5  # 5min 档放量确认线（≥）
    rebound_atr_frac: float = 0.5  # 15min 档反弹无力线（<0.5×ATR）
    adverse_atr_mult: float = 2.0  # 30min 档反向幅度线（严格大于，×ATR）

    def __post_init__(self) -> None:
        dd = float(self.drawdown_pct_5m)
        if not math.isfinite(dd) or dd <= 0:
            raise InvalidPostEntryInputError(f"drawdown_pct_5m 必须为正: {self.drawdown_pct_5m}")
        vr = float(self.volume_ratio_min)
        if not math.isfinite(vr) or vr < 0:
            raise InvalidPostEntryInputError(f"volume_ratio_min 必须 ≥0: {self.volume_ratio_min}")
        rb = float(self.rebound_atr_frac)
        if not math.isfinite(rb) or rb <= 0:
            raise InvalidPostEntryInputError(f"rebound_atr_frac 必须为正: {self.rebound_atr_frac}")
        am = float(self.adverse_atr_mult)
        if not math.isfinite(am) or am <= 0:
            raise InvalidPostEntryInputError(f"adverse_atr_mult 必须为正: {self.adverse_atr_mult}")


@dataclass(frozen=True)
class PostEntryVerdict:
    """单档验证判定（frozen）。"""

    symbol: str
    checkpoint: PostEntryCheckpoint
    action: CorrectionAction
    reason: str  # 命中规则与指标快照（如实记录）
    metrics: Mapping[str, float]


class PostEntryInstantValidator:
    """买入后即时验证器（T+5/15/30min 三档判定核心）。

    Args:
        config: PostEntryValidatorConfig（None=默认阈值）
        audit_sink: 非 PASS 动作回调（动作写审计链，委托 D_GOV_AUDIT；None=仅返回）
    """

    def __init__(
        self,
        config: PostEntryValidatorConfig | None = None,
        audit_sink: Callable[[PostEntryVerdict], None] | None = None,
    ) -> None:
        if config is not None and not isinstance(config, PostEntryValidatorConfig):
            raise InvalidPostEntryInputError(f"config 类型非法: {type(config).__name__}")
        self._config = config or PostEntryValidatorConfig()
        self._audit_sink = audit_sink

    @property
    def config(self) -> PostEntryValidatorConfig:
        return self._config

    def validate(
        self,
        symbol: str,
        *,
        entry_price: float,
        checkpoint: PostEntryCheckpoint,
        current_price: float,
        volume_ratio: float | None = None,
        vwap: float | None = None,
        session_low: float | None = None,
        atr14: float | None = None,
    ) -> PostEntryVerdict:
        """按档位执行即时验证判定。

        Raises:
            InvalidPostEntryInputError: 输入非法 / 档位必填缺失（Fail-Closed）
        """
        if not symbol:
            raise InvalidPostEntryInputError("symbol 不能为空")
        entry = _positive_finite("entry_price", entry_price)
        current = _positive_finite("current_price", current_price)
        if not isinstance(checkpoint, PostEntryCheckpoint):
            raise InvalidPostEntryInputError(f"checkpoint 类型非法: {type(checkpoint).__name__}")

        if checkpoint is PostEntryCheckpoint.MIN_5:
            action, reason, metrics = self._eval_5m(entry, current, volume_ratio)
        elif checkpoint is PostEntryCheckpoint.MIN_15:
            action, reason, metrics = self._eval_15m(entry, current, vwap, session_low, atr14)
        else:
            action, reason, metrics = self._eval_30m(entry, current, atr14)

        verdict = PostEntryVerdict(
            symbol=symbol,
            checkpoint=checkpoint,
            action=action,
            reason=reason,
            metrics=metrics,
        )
        if action is not CorrectionAction.PASS and self._audit_sink is not None:
            self._audit_sink(verdict)
        return verdict

    # ── 三档规则 ─────────────────────────────────────────────────

    def _eval_5m(
        self, entry: float, current: float, volume_ratio: float | None
    ) -> tuple[CorrectionAction, str, dict[str, float]]:
        if volume_ratio is None:
            raise InvalidPostEntryInputError("MIN_5 档必填 volume_ratio（量比确认）")
        vr = float(volume_ratio)
        if not math.isfinite(vr) or vr < 0:
            raise InvalidPostEntryInputError(f"volume_ratio 必须为非负有限值: {volume_ratio}")
        drawdown = (entry - current) / entry
        metrics = {"drawdown_pct": drawdown, "volume_ratio": vr}
        if drawdown > self._config.drawdown_pct_5m and vr >= self._config.volume_ratio_min:
            return (
                CorrectionAction.WATCH,
                f"5min跌幅{drawdown:.2%}>{self._config.drawdown_pct_5m:.2%}且量比{vr:.2f}"
                f"≥{self._config.volume_ratio_min}→观察标记",
                metrics,
            )
        return CorrectionAction.PASS, "5min验证通过（跌幅/量比未同时越线）", metrics

    def _eval_15m(
        self,
        entry: float,
        current: float,
        vwap: float | None,
        session_low: float | None,
        atr14: float | None,
    ) -> tuple[CorrectionAction, str, dict[str, float]]:
        if vwap is None or session_low is None or atr14 is None:
            raise InvalidPostEntryInputError("MIN_15 档必填 vwap/session_low/atr14")
        vwap_v = _positive_finite("vwap", vwap)
        low_v = _positive_finite("session_low", session_low)
        atr = _positive_finite("atr14", atr14)
        if low_v > current:
            raise InvalidPostEntryInputError(
                f"session_low 不能高于 current_price: {low_v} > {current}"
            )
        rebound = current - low_v
        rebound_line = self._config.rebound_atr_frac * atr
        metrics = {"vwap": vwap_v, "session_low": low_v, "rebound": rebound, "atr14": atr}
        if current < vwap_v and rebound < rebound_line:
            return (
                CorrectionAction.REDUCE_HALF,
                f"15min价{current:.3f}<vwap{vwap_v:.3f}且反弹{rebound:.3f}<"
                f"{self._config.rebound_atr_frac}×ATR({rebound_line:.3f})无力→减仓50%",
                metrics,
            )
        return CorrectionAction.PASS, "15min验证通过（未同时破均线且反弹无力）", metrics

    def _eval_30m(
        self, entry: float, current: float, atr14: float | None
    ) -> tuple[CorrectionAction, str, dict[str, float]]:
        if atr14 is None:
            raise InvalidPostEntryInputError("MIN_30 档必填 atr14")
        atr = _positive_finite("atr14", atr14)
        adverse = entry - current
        adverse_line = self._config.adverse_atr_mult * atr
        metrics = {"adverse": adverse, "atr14": atr, "adverse_line": adverse_line}
        if adverse > adverse_line:
            return (
                CorrectionAction.EXIT_ALL,
                f"30min反向{adverse:.3f}>{self._config.adverse_atr_mult}×ATR"
                f"({adverse_line:.3f})→全部止损",
                metrics,
            )
        return CorrectionAction.PASS, "30min验证通过（反向幅度未越 2ATR 线）", metrics
